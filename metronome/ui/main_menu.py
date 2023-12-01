import time

import pygame
from metronome.ui.colors import *
from config import Config


class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win):
        # pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        if self.text != '':
            font = pygame.font.SysFont(None, 30)
            text = font.render(self.text, 1, self.color)
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


class MenuUI:
    def __init__(self, screen, exercise_names):
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.bpm = 80  # Starting BPM
        self.beats_per_bar = 4  # Default Beats Per Bar
        self.selected_exercise = 0  # Default selected exercise
        self.exercise_list = exercise_names
        self.create_buttons()
        self.splash_image = pygame.image.load('./data/splash_screen.png').convert_alpha()
        self.menu_image = pygame.image.load('./data/menu_screen.png').convert_alpha()
        self.start_sound = pygame.mixer.Sound(Config.SOUND_TRUMPET_FPATH)

    def create_buttons(self):
        self.start_button = Button((100, 255, 100), 800, 750, 200, 200, '')
        self.bpm_down_button = Button(WHITE, 470, 700, 50, 25, '-')
        self.bpm_up_button = Button(WHITE, 670, 700, 50, 25, '+')
        self.beats_down_button = Button(WHITE, 1100, 700, 50, 25, '-')
        self.beats_up_button = Button(WHITE, 1300, 700, 50, 25, '+')
        self.exercise_buttons = [Button(WHITE, self.width // 2 - 150, self.height // 2 - 200 + i * 30, 300, 30, exercise)
                                 for i, exercise in enumerate(self.exercise_list)]

    def splash(self):
        if Config.DEBUG_MODE is True:
            # Skip splash to save time in debug mode
            return None
        self.screen.blit(self.splash_image, (0, 0))
        pygame.display.flip()
        self.start_sound.play()
        time.sleep(1.8)
        # Fade out splash screen
        for alpha in range(255, 0, -5):
            self.screen.fill((0, 0, 0))
            self.splash_image.set_alpha(alpha)
            self.screen.blit(self.splash_image, (0, 0))
            pygame.display.update()
            pygame.time.delay(30)
        # Transition to menu screen
        self.screen.fill((0, 0, 0))  # Clear screen
        self.screen.blit(self.menu_image, (0, 0))
        pygame.display.flip()

    def draw(self):
        # Draw background
        self.screen.fill(BLACK)
        self.screen.blit(self.menu_image, (0, 0))
        # Draw buttons
        self.start_button.draw(self.screen)
        self.bpm_up_button.draw(self.screen)
        self.bpm_down_button.draw(self.screen)
        self.beats_up_button.draw(self.screen)
        self.beats_down_button.draw(self.screen)
        # Draw exercise buttons
        for i, button in enumerate(self.exercise_buttons):
            button.color = HIGHLIGHT_COLOR if i == self.selected_exercise else MENU_COLOR
            button.draw(self.screen)
        # BPM and Beats Per Bar display
        font = pygame.font.SysFont(None, 36)
        bpm_text = font.render(f'BPM: {self.bpm}', True, WHITE)
        beats_text = font.render(f'Beats/Bar: {self.beats_per_bar}', True, WHITE)
        self.screen.blit(bpm_text, (547, 700))
        self.screen.blit(beats_text, (1150, 700))
        # Update the Display
        pygame.display.flip()

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.is_over(pos):
                return False  # Return False to toggle menu mode in the main loop
            if self.bpm_up_button.is_over(pos):
                self.bpm += 1
            if self.bpm_down_button.is_over(pos) and self.bpm > 0:
                self.bpm -= 1
            if self.beats_up_button.is_over(pos):
                self.beats_per_bar += 1
            if self.beats_down_button.is_over(pos) and self.beats_per_bar > 1:
                self.beats_per_bar -= 1
            for i, button in enumerate(self.exercise_buttons):
                if button.is_over(pos):
                    self.selected_exercise = i
        return True


def run():
    # Initialize Pygame
    pygame.init()
    # Screen dimensions and settings
    screen = pygame.display.set_mode((600, 800))
    pygame.display.set_caption('Exercise Menu')
    # Create Menu UI
    menu_ui = MenuUI(screen, exercise_names=["Happy Feet", "Hand Independence", "Whole Body Scrub"])
    menu_ui.splash()
    # Main loop
    running = True
    menu_mode = True
    while running:
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if menu_mode:
                menu_mode = menu_ui.handle_event(event, pos)
        if menu_mode:
            menu_ui.draw()
        else:
            screen.fill(BLACK)
            # Update the Display
            pygame.display.flip()
    # Quit Pygame
    pygame.quit()


if __name__ == '__main__':
    run()
