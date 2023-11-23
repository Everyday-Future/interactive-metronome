import sys
import time
import pygame
from config import Config
from metronome.ui.colors import *
from metronome.ui.main_menu import MenuUI
from metronome.exercise.exercise import ExerciseFactory, Pattern
from metronome.arduino.arduino_threaded import Hit, ArduinoController


class MovingObject:
    def __init__(self, window, creation_time, beats_on_screen, channel=-1):
        self.window = window
        self.screen_width, self.screen_height = self.window.get_size()
        self.creation_time = creation_time
        self.beats_on_screen = beats_on_screen
        self.channel = channel
        self.x = self.screen_width  # Starting position at the right edge
        self.hit = False

    def update(self):
        elapsed_time = time.time() - self.creation_time
        # The object should move across the entire width in 4 seconds
        self.x = self.screen_width - (self.screen_width * elapsed_time / self.beats_on_screen)


class Target(MovingObject):
    def draw(self):
        color = blue if self.hit else light_blue
        pygame.draw.circle(self.window, color, (int(self.x), int(self.channel * 70 + 300)), 12)


class Attempt(MovingObject):
    def draw(self):
        color = green if self.hit else white
        pygame.draw.circle(self.window, color, (int(self.x - self.screen_width / 2),
                                                int(self.channel * 70 + 300)), 6)


class BeatLine:
    def __init__(self, window, creation_time, beats_on_screen, click_sound_tick, click_sound_tock=None,
                 beat_idx=1):
        self.window = window
        self.screen_width, self.screen_height = self.window.get_size()
        self.creation_time = creation_time
        self.beats_on_screen = beats_on_screen
        self.x = self.screen_width  # Starting position at the right edge
        self.hit = False
        self.on_the_one = beat_idx == 0
        self.beat_idx = beat_idx
        self.click_sound_tick = click_sound_tick
        self.click_sound_tock = click_sound_tock or click_sound_tick
        self.font = pygame.font.Font(None, 36)

    def update(self):
        elapsed_time = time.time() - self.creation_time
        # The object should move across the entire width in 4 seconds
        self.x = self.screen_width - (self.screen_width * elapsed_time / self.beats_on_screen)

    def draw(self, targeted_beat, beats_per_bar):
        if self.on_the_one is True:
            pygame.draw.line(self.window, white, (self.x, 200), (self.x, self.screen_height), 5)
        else:
            pygame.draw.line(self.window, white, (self.x, 200), (self.x, self.screen_height), 1)
        bpm_text = self.font.render(f"{self.beat_idx + 1}", True, white)
        text_rect = bpm_text.get_rect(center=(self.x, 180))
        self.window.blit(bpm_text, text_rect)
        if abs(self.x - (self.screen_width / 2)) < 2.0 and self.hit is False:
            self.click_sound_tick.play()
            self.hit = True
            targeted_beat += 1
            targeted_beat %= beats_per_bar
        return targeted_beat


class GameUI:
    def __init__(self, window, hit_collector: ArduinoController, exercise_name: str, bpm: int = 60,
                 beats_per_bar: int = 4, beats_on_screen: int = 6):
        self.window = window
        self.width, self.height = self.window.get_size()
        pygame.display.set_caption(f'Monotonous Industrial Blender - Extreme {exercise_name.title()} Edition')
        # Game settings
        self.bpm = bpm
        self.beat_interval = 60.0 / self.bpm
        self.next_beat_time = time.time() + self.beat_interval
        self.center_line_position = self.width // 2
        self.beats_per_bar = beats_per_bar
        self.beats_on_screen = beats_on_screen
        self.next_beat = 0
        self.targeted_beat = -1
        self.channels = 4
        self.keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
        self.exercise = ExerciseFactory().by_name(exercise_name=exercise_name)
        self.current_pattern = self.exercise.patterns[0].__getitem__(0)
        # Game state
        self.lines = []
        self.targets = []
        self.attempts = []
        self.score = 0
        self.misses = 0
        self.combo = 0
        self.max_combo = 0
        # Colors, fonts, and sounds
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.font = pygame.font.Font(None, 36)
        self.click_sound = pygame.mixer.Sound('./data/sounds/tick.wav')
        # Hit collection system
        self.hit_collector = hit_collector
        if self.hit_collector.running is False:
            self.hit_collector.connect()
        self.hit_accuracy = 10
        self.hit_threshold = 30.0  # out of 100

    def handle_events(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event, current_time)
        return True

    def handle_keydown(self, event, current_time):
        hit_attempt = False
        for i in range(self.channels):
            if event.key == self.keys[i]:
                new_attempt = Attempt(window=self.window,
                                      creation_time=current_time,
                                      beats_on_screen=self.beats_on_screen,
                                      channel=i)
                hit = False
                for target in self.targets:
                    if target.channel == i and abs(target.x - self.center_line_position) < self.hit_accuracy:
                        if target.hit is False:
                            self.score += 1
                            self.combo += 1
                            self.max_combo = max(self.max_combo, self.combo)
                        target.hit = True
                        new_attempt.hit = True
                        hit = True
                        break
                if not hit:
                    self.combo = 0
                    self.misses += 1
                self.attempts.append(new_attempt)
                hit_attempt = True
        if not hit_attempt:
            self.combo = 0

    def check_inputs(self):
        # Get new hits from the arduino
        new_hit = self.hit_collector.get_hit()
        if new_hit is not None:
            assert isinstance(new_hit, Hit)
            # print(f'new hit! channel={new_hit.channel} amplitude={new_hit.amplitude}'
            #       f'lag={round(time.time() - new_hit.time, 2)}')
            if new_hit.amplitude > self.hit_threshold:
                new_attempt = Attempt(window=self.window,
                                      creation_time=new_hit.time,
                                      beats_on_screen=self.beats_on_screen,
                                      channel=new_hit.channel)
                hit = False
                for target in self.targets:
                    close_enough = abs(target.x - self.center_line_position) < self.hit_accuracy
                    if target.channel == new_hit.channel and close_enough:
                        if target.hit is False:
                            self.score += 1
                            self.combo += 1
                            self.max_combo = max(self.max_combo, self.combo)
                        target.hit = True
                        new_attempt.hit = True
                        hit = True
                        break
                if not hit:
                    self.combo = 0
                    self.misses += 1
                self.attempts.append(new_attempt)

    def pattern_to_targets(self, new_pattern: Pattern, current_time: float):
        """
        Turn a pattern into a list of targets
        """
        targets = []
        for idx, key in enumerate(['rh', 'lh', 'rf', 'lf']):
            for note_value in new_pattern[key]:
                targets.append(Target(window=self.window,
                                      creation_time=current_time + note_value,
                                      beats_on_screen=self.beats_on_screen,
                                      channel=idx))
        return targets

    def update_and_draw(self, current_time):
        self.check_inputs()
        self.window.fill(black)
        # Draw Central Line (Marker for Beat Alignment)
        pygame.draw.line(self.window, white,
                         (self.center_line_position, 200), (self.center_line_position, self.height), 5)
        for line in self.lines:
            line.update()
            self.targeted_beat = line.draw(targeted_beat=self.targeted_beat, beats_per_bar=self.beats_per_bar)
        self.lines = [line for line in self.lines if line.x >= 0]
        for target in self.targets:
            target.update()
            target.draw()
        missed_targets = [target for target in self.targets if target.x < 0 and target.hit is False]
        self.misses += len(missed_targets)
        self.targets = [target for target in self.targets if target.x >= 0]
        for attempt in self.attempts:
            attempt.update()
            attempt.draw()
        self.attempts = [attempt for attempt in self.attempts if attempt.x >= 0]
        # Generate and Update Lines and Targets
        if current_time >= self.next_beat_time:
            self.lines.append(BeatLine(window=self.window,
                                       creation_time=current_time,
                                       beats_on_screen=self.beats_on_screen,
                                       click_sound_tick=self.click_sound,
                                       beat_idx=self.next_beat))
            if self.next_beat == 0:
                self.current_pattern = self.exercise.__next__()
                self.targets.extend(self.pattern_to_targets(new_pattern=self.current_pattern, current_time=current_time))
            self.next_beat += 1
            self.next_beat %= self.beats_per_bar
            self.next_beat_time += self.beat_interval
        # Display Score, Misses, and Combo
        score_text = self.font.render(f"Score: {self.score}", True, white)
        self.window.blit(score_text, (10, 10))
        misses_text = self.font.render(f"Misses: {self.misses}", True, white)
        self.window.blit(misses_text, (10, 40))
        combo_color = red if self.combo == self.max_combo and self.combo > 0 else white
        combo_text = self.font.render(f"Combo: {self.combo} (Max: {self.max_combo})", True, combo_color)
        self.window.blit(combo_text, (10, 70))
        # Display the current BPM
        bpm_text = self.font.render(f"BPM: {self.bpm}", True, white)
        text_rect = bpm_text.get_rect()
        text_rect.right = self.width - 30  # align to right to 150px
        text_rect.top = 10
        self.window.blit(bpm_text, text_rect)
        # beats_per_bar
        bpb_text = self.font.render(f"Beats Per Bar: {self.beats_per_bar}", True, white)
        text_rect = bpb_text.get_rect()
        text_rect.right = self.width - 30  # align to right to 150px
        text_rect.top = 40
        self.window.blit(bpb_text, text_rect)
        # current_beat
        current_beat_text = self.font.render(f"Current Beat: {int(self.targeted_beat + 1)}", True, white)
        text_rect = current_beat_text.get_rect()
        text_rect.right = self.width - 30  # align to right to 150px
        text_rect.top = 70
        self.window.blit(current_beat_text, text_rect)
        # Exercise name
        bpm_text = self.font.render(f"Exercise: {self.current_pattern['name']}", True, white)
        text_rect = bpm_text.get_rect(center=(self.width / 2, 130))
        self.window.blit(bpm_text, text_rect)
        # Update the Display
        pygame.display.flip()


def run():
    width, height = 1080, 600
    pygame.init()
    pygame.mixer.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Monotonous Industrial Blender - Main Menu')
    hit_collector = ArduinoController(port=Config.COM_PORT, baudrate=Config.BAURDRATE, name='hits')
    menu = MenuUI(screen=window, exercise_names=ExerciseFactory().list_names())
    game = None
    try:
        # Main loop
        menu_mode = True
        running = True
        while running:
            current_time = time.time()
            # Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if menu_mode:
                    pos = pygame.mouse.get_pos()
                    menu_mode = menu.handle_event(event, pos)
                elif not menu_mode and event.type == pygame.KEYDOWN:
                    game.handle_keydown(event=event, current_time=current_time)
            if menu_mode is True:
                menu.draw()
            else:
                if game is None:
                    game = GameUI(window=window,
                                  hit_collector=hit_collector,
                                  exercise_name=menu.exercise_list[menu.selected_exercise],
                                  bpm=menu.bpm,
                                  beats_per_bar=menu.beats_per_bar,
                                  beats_on_screen=8)
                    if hit_collector.running is False:
                        raise ValueError(
                            f"could not connect to Arduino on port={Config.COM_PORT} at baudrate={Config.BAURDRATE}")
                game.update_and_draw(current_time=current_time)
    except:
        del game
        hit_collector.disconnect()
        pygame.quit()
        raise
    del game
    hit_collector.disconnect()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    run()
