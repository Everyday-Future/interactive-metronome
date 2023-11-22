
import pygame
import sys
import time
import random
from metronome.exercise.exercise import Exercise, BarPattern
from metronome.arduino.arduino_threaded import Hit, ArduinoController
from config import Config

# Colors and settings
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class MetronomeUI:
    """
    Main class for handling UI functionality for the metronome
    """

    def __init__(self, screen, metronome_speed=60, beats_per_bar=4):
        self.screen = screen
        screen_width, screen_height = self.screen.get_size()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tick_sound = pygame.mixer.Sound('./data/sounds/tick.wav')
        self.tock_sound = pygame.mixer.Sound('./data/sounds/tock.wav')
        self.metronome_speed = metronome_speed  # Initial tempo (BPM)
        self.tick_interval = 60 / metronome_speed
        self.min_speed = 40  # Minimum tempo (BPM)
        self.max_speed = 200  # Maximum tempo (BPM)
        self.beats_per_bar = beats_per_bar
        self.bar_percent = 0.0
        self.last_tick = time.time()
        self.tick_count = 0
        self.slider_active = False
        self.light_colors = [(255, 0, 0)] * self.beats_per_bar
        self.slider_rect = pygame.Rect(10, 40, 150, 20)  # Positioning slider under the tempo text
        self.slider_color = (200, 200, 200)
        self.slider_position = self.slider_rect[0] + (
                    self.slider_rect[2] * ((self.metronome_speed - self.min_speed) / (self.max_speed - self.min_speed)))
        # self.hit_box_generator = Exercise.note_tree_feet_alternating(num_beats=self.beats_per_bar, num_loops=8)
        self.hit_box_generator = Exercise.left_to_right_note_tree(num_beats=self.beats_per_bar, num_loops=8)
        self.prev_hit_box = self.hit_box_generator.__next__()
        self.current_hit_box = self.hit_box_generator.preview()

    def update_timers(self, beats_per_bar=None, metronome_speed=None):
        if beats_per_bar is not None:
            self.beats_per_bar = beats_per_bar
        self.light_colors = [(255, 0, 0)] * self.beats_per_bar
        if metronome_speed is not None:
            self.metronome_speed = metronome_speed
        self.tick_interval = 60 / self.metronome_speed
        # Calculate the percent progress through the bar
        current_time = time.time()
        prev_bar_percent = self.bar_percent
        self.bar_percent = ((self.tick_count - 1) % self.beats_per_bar) / self.beats_per_bar
        self.bar_percent += (current_time - self.last_tick) / self.tick_interval / self.beats_per_bar
        # Update the metronome tick
        if current_time - self.last_tick >= self.tick_interval:
            self.play_tick_sound()
            self.last_tick = current_time
            self.tick_count = (self.tick_count + 1) % self.beats_per_bar
            if self.tick_count == 1:
                self.increment_hitboxes()

    def play_tick_sound(self):
        if self.tick_count == 0:
            self.tick_sound.play()
        else:
            self.tock_sound.play()

    def increment_hitboxes(self):
        self.prev_hit_box = self.hit_box_generator.__next__()
        self.current_hit_box = self.hit_box_generator.preview()

    def draw_hitboxes(self):
        """
        Draw the hitboxes used to show note targets for hits.
        """
        box_color = (100, 100, 255)
        start_row = 200
        row_increment = 70
        for idx, hit_box_row in enumerate(self.current_hit_box):
            if isinstance(hit_box_row, BarPattern):
                hit_box_row = hit_box_row.pattern
            for hit_box in hit_box_row:
                pygame.draw.circle(self.screen,
                                   color=box_color,
                                   center=((hit_box / self.beats_per_bar) * self.screen_width,
                                           start_row + idx * row_increment),
                                   radius=20)
                # Current matrix preview
                pygame.draw.circle(self.screen,
                                   color=box_color,
                                   center=((hit_box / self.beats_per_bar) * self.screen_width / 3 + self.screen_width / 3,
                                           20 + idx * row_increment / 5),
                                   radius=2)
                if hit_box == 0:
                    # Wrap around to the other side
                    pygame.draw.circle(self.screen,
                                       color=box_color,
                                       center=(self.screen_width, start_row + idx * row_increment),
                                       radius=20)

    def draw_score(self, new_hits):
        """
        Evaluate new hits and augment the score with them
        """
        pass

    def draw(self):
        """Draw the metronome with multiple blinking lights, a tempo control slider, and updated UI."""
        # Clear screen and set background color
        self.screen.fill(WHITE)
        # Calculate spacing for lights
        light_spacing = self.screen_width / self.beats_per_bar
        light_size = (20, 20)
        # Determine the active light index
        active_light_index = (self.tick_count - 1) % self.beats_per_bar
        # Draw the blinking lights
        for i in range(self.beats_per_bar):
            light_position = (i * light_spacing - light_size[0] / 2, 100)
            light_color = self.light_colors[i] if i <= active_light_index else BLACK
            pygame.draw.ellipse(self.screen, light_color, pygame.Rect(light_position, light_size))
            pygame.draw.line(self.screen, (40, 40, 40), (i * light_spacing, 80),
                             (i * light_spacing, self.screen_height), 2)  # Line width of 2
        # Draw the tempo slider
        pygame.draw.rect(self.screen, self.slider_color, self.slider_rect)
        pygame.draw.circle(self.screen, BLACK,
                           (int(self.slider_position), self.slider_rect[1] + self.slider_rect[3] // 2), 10)
        # Render and draw the tempo text
        font = pygame.font.SysFont(None, 24)
        text = font.render(f'Tempo: {self.metronome_speed} BPM', True, BLACK)
        self.screen.blit(text, (10, 10))  # Top-left corner
        # Draw a vertical red line at the current time in the bar
        # font = pygame.font.SysFont(None, 24)
        # text = font.render(f'progress: {line_position * 100.0}%', True, BLACK)
        # screen.blit(text, (400, 10))  # Top-left corner
        line_x = int(self.screen_width * self.bar_percent)
        pygame.draw.line(self.screen, (255, 40, 40), (line_x, 80), (line_x, self.screen_height), 2)  # Line width of 2
        self.draw_hitboxes()

    def draw_a_hit(self, row_height, line_position, hit_age=1.0):
        fading_color = (int(hit_age * 255.0), 255, int(hit_age * 255.0))
        pygame.draw.circle(self.screen,
                           fading_color,
                           center=[int(self.screen_width * line_position), row_height],
                           radius=7)
        if self.screen_width * line_position < 7.0:
            pygame.draw.circle(self.screen,
                               fading_color,
                               center=[int(self.screen_width + self.screen_width * line_position), row_height],
                               radius=7)

    def handle_speed_slider_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.slider_rect.collidepoint(event.pos):
                self.slider_active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.slider_active = False
        elif event.type == pygame.MOUSEMOTION:
            if self.slider_active:
                x, y = event.pos
                x = max(self.slider_rect[0], min(x, self.slider_rect[0] + self.slider_rect[2]))
                new_speed = int(self.min_speed + (self.max_speed - self.min_speed) * (
                            (x - self.slider_rect[0]) / self.slider_rect[2]))
                return new_speed
        return None

    def handle_pygame_event(self, event, hits):
        # Get new hits from the spacebar
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                hits.append({'channel': -1, 'position': self.bar_percent, 'time': time.time()})
        new_speed = self.handle_speed_slider_event(event)
        if new_speed is not None and self.min_speed <= new_speed <= self.max_speed:
            self.metronome_speed = new_speed
            self.tick_interval = 60 / self.metronome_speed  # Update tick interval based on the slider
            self.slider_position = self.slider_rect[0] + (self.slider_rect[2] * (
                        (self.metronome_speed - self.min_speed) / (self.max_speed - self.min_speed)))


def run():
    # Initialize Pygame and mixer
    pygame.init()
    pygame.mixer.init()
    # Set up the screen
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Metronome App")
    ui = MetronomeUI(screen=screen,
                     metronome_speed=random.randint(50, 90),
                     beats_per_bar=random.choice([3, 4, 4, 4, 4, 5]))
    hit_collector = ArduinoController(port=Config.COM_PORT, baudrate=Config.BAURDRATE, name='hits')
    hit_collector.connect()
    hits = []
    # Clock for timing
    clock = pygame.time.Clock()

    try:
        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                ui.handle_pygame_event(event, hits)
            ui.update_timers()
            # Get new hits from the arduino
            new_hit = hit_collector.get_hit()
            if new_hit is not None:
                assert isinstance(new_hit, Hit)
                print(
                    f'new hit! channel={new_hit.channel} amplitude={new_hit.amplitude} lag={time.time() - new_hit.time}')
                if new_hit.amplitude > 700.0:
                    hits.append({'channel': new_hit.channel, 'position': ui.bar_percent, 'time': new_hit.time})
            # Draw metronome UI with blinking lights and tempo slider
            ui.draw()
            # Purge old hits and render new ones
            hits = [hit for hit in hits if (time.time() - hit['time']) < (ui.tick_interval * ui.beats_per_bar)]
            for hit in reversed(hits):
                ui.draw_a_hit(row_height=200 + int(hit['channel'] * 70),
                              line_position=hit['position'],
                              hit_age=(time.time() - hit['time']) / (ui.tick_interval * ui.beats_per_bar))
            # Update the display
            pygame.display.flip()
            # Cap the frame rate
            clock.tick(60)
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
