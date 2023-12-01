import sys
import time
import pygame
from config import Config
from metronome.ui.colors import *
from metronome.ui.main_menu import MenuUI
from metronome.exercise.exercise import ExerciseFactory, Pattern
from metronome.arduino.arduino_threaded import Hit, ArduinoController


class MovingObject:
    def __init__(self, window, offset=0.0, channel=-1):
        self.window = window
        self.screen_width, self.screen_height = self.window.get_size()
        self.last_updated = time.time()
        self.offset = offset
        self.channel = channel
        self.x = self.screen_width + self.offset  # Starting position at the right edge
        self.hit = False
        self.font = pygame.font.Font(None, 24)

    def get_y(self):
        if self.channel == 0:
            return 0
        elif self.channel == 1:
            return 70
        elif self.channel == 2:
            return 180
        elif self.channel == 3:
            return 250
        else:
            return 300

    def update(self, speed):
        self.x -= speed * (time.time() - self.last_updated)
        self.last_updated = time.time()


class Target(MovingObject):
    def draw(self):
        if self.hit is True:
            pygame.draw.circle(self.window, LIGHT_BLUE, (int(self.x), int(self.get_y() + 250)), 12)
            pygame.draw.circle(self.window, BLACK, (int(self.x), int(self.get_y() + 250)), 10)
        else:
            pygame.draw.circle(self.window, LIGHT_BLUE, (int(self.x), int(self.get_y() + 250)), 12)
            if self.channel % 2 == 0:
                target_side = self.font.render("R", True, BLACK)
            else:
                target_side = self.font.render("L", True, BLACK)
            self.window.blit(target_side, (int(self.x - 6), int(self.get_y() + 243)))


class Attempt(MovingObject):
    def draw(self):
        color = GREEN if self.hit else WHITE
        pygame.draw.circle(self.window, color, (int(self.x - self.screen_width / 2), int(self.get_y() + 250)), 6)


class BeatLine:
    def __init__(self, window, click_sound_tick, click_sound_tock=None, beat_idx=1):
        self.window = window
        self.screen_width, self.screen_height = self.window.get_size()
        self.last_updated = time.time()
        self.x = self.screen_width  # Starting position at the right edge
        self.hit = False
        self.on_the_one = beat_idx == 0
        self.beat_idx = beat_idx
        self.click_sound_tick = click_sound_tick
        self.click_sound_tock = click_sound_tock or click_sound_tick
        self.font = pygame.font.Font(None, 36)

    def update(self, speed):
        self.x -= speed * (time.time() - self.last_updated)
        self.last_updated = time.time()

    def draw(self, targeted_beat, beats_per_bar):
        if self.on_the_one is True:
            pygame.draw.line(self.window, WHITE, (self.x, 200), (self.x, self.screen_height), 5)
        else:
            pygame.draw.line(self.window, WHITE, (self.x, 200), (self.x, self.screen_height), 1)
        bpm_text = self.font.render(f"{self.beat_idx + 1}", True, WHITE)
        text_rect = bpm_text.get_rect(center=(self.x, 180))
        self.window.blit(bpm_text, text_rect)
        if abs(self.x - (self.screen_width / 2)) < 2.0 and self.hit is False:
            if self.on_the_one is True:
                self.click_sound_tick.play()
            else:
                self.click_sound_tock.play()
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
        self.beat_interval = None
        self.next_beat_time = None
        self.beats_on_screen = beats_on_screen
        self.speed = 0
        self.update_bpm(self.bpm)
        self.center_line_position = self.width // 2
        self.beats_per_bar = beats_per_bar
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
        self.big_font = pygame.font.Font(None, 48)
        self.tick_sound = pygame.mixer.Sound('./data/sounds/tick.wav')
        self.tock_sound = pygame.mixer.Sound('./data/sounds/tock.wav')
        # Hit collection system
        self.hit_collector = hit_collector
        if self.hit_collector.running is False:
            self.hit_collector.connect()
        self.hit_accuracy = 15
        self.hit_threshold = 10.0  # out of 100
        self.got_first_hit = False
        self.penalize_missed_attempts = False

    def update_bpm(self, new_bpm):
        self.bpm = new_bpm
        self.beat_interval = 60.0 / self.bpm
        self.next_beat_time = time.time() + self.beat_interval
        self.speed = (self.width / (60.0 / self.bpm)) / self.beats_on_screen

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
        return True

    def handle_keydown(self, event):
        hit_attempt = False
        for i in range(self.channels):
            if event.key == self.keys[i]:
                new_attempt = Attempt(window=self.window,
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
                if not hit and self.penalize_missed_attempts is True:
                    self.combo = 0
                    self.misses += 1
                self.attempts.append(new_attempt)

    def pattern_to_targets(self, new_pattern: Pattern):
        """
        Turn a pattern into a list of targets
        """
        targets = []
        for idx, key in enumerate(['rh', 'lh', 'rf', 'lf']):
            for note_value in new_pattern[key]:
                targets.append(Target(window=self.window,
                                      offset=note_value * (self.width / self.beats_on_screen),
                                      channel=idx))
        return targets

    def update_and_draw(self, current_time):
        self.window.fill(BLACK)
        if self.got_first_hit is False:
            if self.hit_collector.get_hit() is not None:
                self.got_first_hit = True
                self.next_beat_time = time.time() + self.beat_interval
                self.next_beat = 0
                self.targeted_beat = -1
                return None
        else:
            self.check_inputs()
            # Draw guide lines for voices
            pygame.draw.line(self.window, GRAY, (0, 250), (self.width, 250), 1)
            pygame.draw.line(self.window, GRAY, (0, 320), (self.width, 320), 1)
            pygame.draw.line(self.window, GRAY, (0, 430), (self.width, 430), 1)
            pygame.draw.line(self.window, GRAY, (0, 500), (self.width, 500), 1)
            # Draw Central Line (Marker for Beat Alignment)
            pygame.draw.line(self.window, WHITE,
                             (self.center_line_position, 200), (self.center_line_position, self.height), 5)
            for line in self.lines:
                line.update(self.speed)
                self.targeted_beat = line.draw(targeted_beat=self.targeted_beat, beats_per_bar=self.beats_per_bar)
            self.lines = [line for line in self.lines if line.x >= 0]
            for target in self.targets:
                target.update(self.speed)
                target.draw()
            missed_targets = [target for target in self.targets if target.x < 0 and target.hit is False]
            if len(missed_targets) > 0:
                self.combo = 0
                self.misses += len(missed_targets)
            self.targets = [target for target in self.targets if target.x >= 0]
            for attempt in self.attempts:
                attempt.update(self.speed)
                attempt.draw()
            self.attempts = [attempt for attempt in self.attempts if attempt.x >= 0]
            # Generate and Update Lines and Targets
            if current_time >= self.next_beat_time:
                if self.next_beat == 0:
                    try:
                        self.current_pattern = self.exercise.__next__()
                    except StopIteration:
                        self.exercise.reset()
                        self.current_pattern = self.exercise.__next__()
                    self.targets.extend(self.pattern_to_targets(new_pattern=self.current_pattern))
                if self.exercise.is_last_beat() is True and self.next_beat == self.beats_per_bar - 1:
                    self.update_bpm(self.bpm + 5)
                self.lines.append(BeatLine(window=self.window,
                                           click_sound_tick=self.tick_sound,
                                           click_sound_tock=self.tock_sound,
                                           beat_idx=self.next_beat))
                self.next_beat += 1
                self.next_beat %= self.beats_per_bar
                self.next_beat_time += self.beat_interval
        # Display Score, Misses, and Combo
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.window.blit(score_text, (10, 10))
        # misses_text = self.font.render(f"Misses: {self.misses}", True, white)
        # self.window.blit(misses_text, (10, 40))
        if self.combo == self.max_combo and self.combo > 0:
            # New combo record
            combo_text = self.big_font.render(f"Combo: {self.combo} (Max: {self.max_combo})", True, RED)
            self.window.blit(combo_text, (10, 46))
        else:
            combo_text = self.font.render(f"Combo: {self.combo} (Max: {self.max_combo})", True, WHITE)
            self.window.blit(combo_text, (10, 40))
        # Display the current BPM
        bpm_text = self.font.render(f"BPM: {self.bpm}", True, WHITE)
        text_rect = bpm_text.get_rect()
        text_rect.right = self.width - 30  # align to right to 150px
        text_rect.top = 10
        self.window.blit(bpm_text, text_rect)
        # beats_per_bar
        bpb_text = self.font.render(f"Beats Per Bar: {self.beats_per_bar}", True, WHITE)
        text_rect = bpb_text.get_rect()
        text_rect.right = self.width - 30  # align to right to 150px
        text_rect.top = 40
        self.window.blit(bpb_text, text_rect)
        # current_beat
        current_beat_text = self.font.render(f"Current Beat: {int(self.targeted_beat + 1)}", True, WHITE)
        text_rect = current_beat_text.get_rect()
        text_rect.right = self.width - 30  # align to right to 150px
        text_rect.top = 70
        self.window.blit(current_beat_text, text_rect)
        # Exercise name
        bpm_text = self.font.render(f"Exercise: {self.current_pattern['name']}", True, WHITE)
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
                    game.handle_keydown(event=event)
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
