import pygame
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window
width, height = 800, 600
window = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
pygame.display.set_caption('Rhythm Game with Metronome')

# Colors and Fonts
black = (0, 0, 0)
white = (255, 255, 255)
green = (40, 255, 40)
blue = (40, 40, 255)
light_blue = (140, 140, 255)
red = (255, 40, 40)
font = pygame.font.Font(None, 36)

# Sound Effects
click_sound = pygame.mixer.Sound('../../data/sounds/tick.wav')
# Metronome Settings
BPM = 60  # Beats per minute
beat_interval = 60 / BPM  # Time between beats in seconds
next_beat_time = time.time() + beat_interval
beats_per_bar = 4
beats_on_screen = 6
next_beat = 0
targeted_beat = -1


# Line and Target Classes
class MovingObject:
    def __init__(self, creation_time, beats_on_screen, channel=-1):
        self.creation_time = creation_time
        self.beats_on_screen = beats_on_screen
        self.channel = channel
        self.x = width  # Starting position at the right edge
        self.hit = False

    def update(self):
        elapsed_time = time.time() - self.creation_time
        # The object should move across the entire width in 4 seconds
        self.x = width - (width * elapsed_time / self.beats_on_screen)


class Target(MovingObject):
    def draw(self):
        color = light_blue if self.hit else blue
        pygame.draw.circle(window, color, (int(self.x), int(self.channel * 70 + 300)), 20)


class Attempt(MovingObject):
    def draw(self):
        color = green if self.hit else white
        pygame.draw.circle(window, color, (int(self.x), int(self.channel * 70 + 300)), 10)


class BeatLine:
    def __init__(self, creation_time, beats_on_screen, on_the_one=False):
        self.creation_time = creation_time
        self.beats_on_screen = beats_on_screen
        self.x = width  # Starting position at the right edge
        self.hit = False
        self.on_the_one = on_the_one

    def update(self):
        elapsed_time = time.time() - self.creation_time
        # The object should move across the entire width in 4 seconds
        self.x = width - (width * elapsed_time / self.beats_on_screen)

    def draw(self, targeted_beat, beats_per_bar):
        if self.on_the_one is True:
            pygame.draw.line(window, white, (self.x, 200), (self.x, height), 3)
        else:
            pygame.draw.line(window, white, (self.x, 200), (self.x, height), 1)
        if abs(self.x - (width / 2)) < 2.0 and self.hit is False:
            click_sound.play()
            self.hit = True
            targeted_beat += 1
            targeted_beat %= beats_per_bar
        return targeted_beat


# GameUI Class
class GameUI:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Rhythm Game with Metronome')
        self.clock = pygame.time.Clock()

        # Game settings
        self.BPM = 60
        self.beat_interval = 60 / self.BPM
        self.next_beat_time = time.time() + self.beat_interval
        self.center_line_position = self.width // 2

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
        self.click_sound = pygame.mixer.Sound('click.wav')  # Ensure correct path

    def run(self):
        running = True
        while running:
            self.window.fill(self.black)
            current_time = time.time()

            # Event handling
            running = self.handle_events(current_time)

            # Update and draw game elements
            self.update_and_draw(current_time)

            # Update the display and tick the clock
            pygame.display.update()
            self.clock.tick(60)  # Run at 60 frames per second

        pygame.quit()

    def handle_events(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event, current_time)
        return True

    def handle_keydown(self, event, current_time):
        # [Key handling logic, similar to the previous script]
        pass

    def update_and_draw(self, current_time):
        # Update and draw lines, targets, and attempts
        # [Similar logic to the previous script]

        # Draw central line and display score, misses, and combo
        # [Similar logic to the previous script]
        pass



# Game Variables
channels = 4
lines = []
targets = []
attempts = []
center_line_position = width // 2
keys = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
score = 0
misses = 0
combo = 0
max_combo = 0
movement_speed = width / (4 * beat_interval)  # Adjusted to cover 4 beats across the screen

# Main Game Loop
running = True
while running:
    current_time = time.time()
    window.fill(black)

    # Draw Central Line (Marker for Beat Alignment)
    pygame.draw.line(window, white, (center_line_position, 200), (center_line_position, height), 5)

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            hit_attempt = False
            for i in range(channels):
                if event.key == keys[i]:
                    new_attempt = Attempt(current_time - beats_on_screen / 2 * beat_interval,
                                          beats_on_screen=beats_on_screen, channel=i)
                    hit = False
                    for target in targets:
                        if target.channel == i and abs(target.x - center_line_position) < 20 and not target.hit:
                            target.hit = True
                            new_attempt.hit = True
                            hit = True
                            score += 1
                            combo += 1
                            max_combo = max(max_combo, combo)
                            break
                    if not hit:
                        combo = 0
                        misses += 1
                    attempts.append(new_attempt)
                    hit_attempt = True
            if not hit_attempt:
                combo = 0

    for line in lines:
        line.update()
        targeted_beat = line.draw(targeted_beat=targeted_beat, beats_per_bar=beats_per_bar)
    lines = [line for line in lines if line.x >= 0]

    for target in targets:
        target.update()
        target.draw()
    targets = [target for target in targets if target.x >= 0]

    for attempt in attempts:
        attempt.update()
        attempt.draw()
    attempts = [attempt for attempt in attempts if attempt.x >= 0]

    # Generate and Update Lines and Targets
    if current_time >= next_beat_time:
        lines.append(BeatLine(creation_time=current_time, beats_on_screen=beats_on_screen, on_the_one=next_beat == 0))
        targets.append(Target(creation_time=current_time, beats_on_screen=beats_on_screen, channel=0))
        targets.append(Target(creation_time=current_time, beats_on_screen=beats_on_screen, channel=1))
        targets.append(Target(creation_time=current_time, beats_on_screen=beats_on_screen, channel=2))
        targets.append(Target(creation_time=current_time, beats_on_screen=beats_on_screen, channel=3))
        next_beat += 1
        next_beat %= beats_per_bar
        next_beat_time += beat_interval

    # Display Score, Misses, and Combo
    score_text = font.render(f"Score: {score}", True, white)
    window.blit(score_text, (10, 10))

    misses_text = font.render(f"Misses: {misses}", True, white)
    window.blit(misses_text, (10, 40))

    combo_text = font.render(f"Combo: {combo} (Max: {max_combo})", True, white)
    window.blit(combo_text, (10, 70))

    # Display the current BPM
    bpm_text = font.render(f"BPM: {BPM}", True, white)
    text_rect = bpm_text.get_rect()
    text_rect.right = width - 30  # align to right to 150px
    text_rect.top = 10
    window.blit(bpm_text, text_rect)
    # beats_per_bar
    bpb_text = font.render(f"Beats Per Bar: {beats_per_bar}", True, white)
    text_rect = bpb_text.get_rect()
    text_rect.right = width - 30  # align to right to 150px
    text_rect.top = 40
    window.blit(bpb_text, text_rect)
    # current_beat
    current_beat_text = font.render(f"Current Beat: {int(targeted_beat + 1)}", True, white)
    text_rect = current_beat_text.get_rect()
    text_rect.right = width - 30  # align to right to 150px
    text_rect.top = 70
    window.blit(current_beat_text, text_rect)
    # Exercise name
    bpm_text = font.render(f"Exercise: {beats_per_bar}", True, white)
    text_rect = bpm_text.get_rect(center=(width / 2, 130))
    window.blit(bpm_text, text_rect)

    # Update the Display
    pygame.display.flip()


# Quit Pygame
pygame.quit()
