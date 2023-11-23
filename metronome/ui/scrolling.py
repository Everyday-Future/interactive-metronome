
import sys
import time
import random
import pygame
from config import Config
from metronome.exercise.exercise import Exercise, BarPattern
from metronome.arduino.arduino_threaded import Hit, ArduinoController


black = (0, 0, 0)
white = (255, 255, 255)
green = (40, 255, 40)
blue = (40, 40, 255)
light_blue = (140, 140, 255)
red = (255, 40, 40)


# Line and Target Classes
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
        color = light_blue if self.hit else blue
        pygame.draw.circle(self.window, color, (int(self.x), int(self.channel * 70 + 300)), 12)


class Attempt(MovingObject):
    def draw(self):
        color = green if self.hit else white
        pygame.draw.circle(self.window, color, (int(self.x - self.screen_width / 2), int(self.channel * 70 + 300)), 6)


class BeatLine:
    def __init__(self, window, creation_time, beats_on_screen, click_sound_tick, click_sound_tock=None,
                 on_the_one=False):
        self.window = window
        self.screen_width, self.screen_height = self.window.get_size()
        self.creation_time = creation_time
        self.beats_on_screen = beats_on_screen
        self.x = self.screen_width  # Starting position at the right edge
        self.hit = False
        self.on_the_one = on_the_one
        self.click_sound_tick = click_sound_tick
        self.click_sound_tock = click_sound_tock or click_sound_tick

    def update(self):
        elapsed_time = time.time() - self.creation_time
        # The object should move across the entire width in 4 seconds
        self.x = self.screen_width - (self.screen_width * elapsed_time / self.beats_on_screen)

    def draw(self, targeted_beat, beats_per_bar):
        if self.on_the_one is True:
            pygame.draw.line(self.window, white, (self.x, 200), (self.x, self.screen_height), 3)
        else:
            pygame.draw.line(self.window, white, (self.x, 200), (self.x, self.screen_height), 1)
        if abs(self.x - (self.screen_width / 2)) < 2.0 and self.hit is False:
            self.click_sound_tick.play()
            self.hit = True
            targeted_beat += 1
            targeted_beat %= beats_per_bar
        return targeted_beat


# GameUI Class
class GameUI:
    def __init__(self, hit_collector: ArduinoController, bpm: int = 60,
                 beats_per_bar: int = 4, beats_on_screen: int = 6):
        pygame.init()
        pygame.mixer.init()
        self.width, self.height = 1080, 800
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Rhythm Game with Metronome')
        # Game settings
        self.BPM = bpm
        self.beat_interval = 60.0 / self.BPM
        self.next_beat_time = time.time() + self.beat_interval
        self.center_line_position = self.width // 2
        self.beats_per_bar = beats_per_bar
        self.beats_on_screen = beats_on_screen
        self.next_beat = 0
        self.targeted_beat = -1
        self.channels = 4
        self.keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
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
        self.hits = []
        self.hit_accuracy = 10

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

    def update_and_draw(self, current_time):
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
                                       on_the_one=self.next_beat == 0))
            self.targets.append(Target(window=self.window,
                                       creation_time=current_time,
                                       beats_on_screen=self.beats_on_screen,
                                       channel=0))
            self.targets.append(Target(window=self.window,
                                       creation_time=current_time,
                                       beats_on_screen=self.beats_on_screen,
                                       channel=1))
            self.targets.append(Target(window=self.window,
                                       creation_time=current_time,
                                       beats_on_screen=self.beats_on_screen,
                                       channel=2))
            self.targets.append(Target(window=self.window,
                                       creation_time=current_time,
                                       beats_on_screen=self.beats_on_screen,
                                       channel=3))
            self.next_beat += 1
            self.next_beat %= self.beats_per_bar
            self.next_beat_time += self.beat_interval
        # Display Score, Misses, and Combo
        score_text = self.font.render(f"Score: {self.score}", True, white)
        self.window.blit(score_text, (10, 10))
        misses_text = self.font.render(f"Misses: {self.misses}", True, white)
        self.window.blit(misses_text, (10, 40))
        combo_text = self.font.render(f"Combo: {self.combo} (Max: {self.max_combo})", True, white)
        self.window.blit(combo_text, (10, 70))
        # Display the current BPM
        bpm_text = self.font.render(f"BPM: {self.BPM}", True, white)
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
        bpm_text = self.font.render(f"Exercise: {self.beats_per_bar}", True, white)
        text_rect = bpm_text.get_rect(center=(self.width / 2, 130))
        self.window.blit(bpm_text, text_rect)
        # Update the Display
        pygame.display.flip()


def run():
    hit_collector = ArduinoController(port=Config.COM_PORT, baudrate=Config.BAURDRATE, name='hits')
    hit_collector.connect()
    if hit_collector.running is False:
        raise ValueError(f"could not connect to Arduino on port={Config.COM_PORT} at baudrate={Config.BAURDRATE}")
    ui = GameUI(hit_collector=hit_collector,
                bpm=random.randint(40, 90),
                beats_per_bar=random.choice([3, 4, 4, 4, 4, 5]),
                beats_on_screen=8)
    try:
        # Main loop
        running = True
        while running:
            current_time = time.time()

            # Handle Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    ui.handle_keydown(event=event, current_time=current_time)
            ui.update_and_draw(current_time=current_time)
    except:
        del ui
        hit_collector.disconnect()
        pygame.quit()
        raise
    del ui
    hit_collector.disconnect()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    run()
