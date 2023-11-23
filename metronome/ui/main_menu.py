import pygame
from metronome.ui.colors import *


class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont(None, 30)
            text = font.render(self.text, 1, BLACK)
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


class MenuUI:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.bpm = 60  # Starting BPM
        self.beats_per_bar = 4  # Default Beats Per Bar
        self.selected_exercise = 0  # Default selected exercise
        self.exercise_list = ["Happy Feet", "Hand Independence", "Whole Body Scrub"]
        self.create_buttons()

    def create_buttons(self):
        self.start_button = Button((100, 255, 100), self.width // 2 - 50, self.height // 2 - 150, 100, 50, 'Start')
        self.bpm_down_button = Button(WHITE, 0, 10, 50, 25, '-')
        self.bpm_up_button = Button(WHITE, 200, 10, 50, 25, '+')
        self.beats_down_button = Button(WHITE, 0, 50, 50, 25, '-')
        self.beats_up_button = Button(WHITE, 200, 50, 50, 25, '+')
        self.exercise_buttons = [Button(LIGHT_BLUE, self.width // 2 - 90, self.height // 2 - 90 + i * 30, 180, 25, exercise)
                                 for i, exercise in enumerate(self.exercise_list)]

    def draw(self):
        # Draw background
        self.screen.fill(WHITE)
        # Draw menu square
        menu_width, menu_height = 300, 300
        # Draw menu square
        menu_rect = pygame.Rect(self.width // 2 - menu_width/2, self.height // 2 - menu_height / 2, menu_width, menu_height)
        pygame.draw.rect(self.screen, LIGHT_BLUE, menu_rect)

        # Draw buttons
        self.start_button.draw(self.screen)
        self.bpm_up_button.draw(self.screen)
        self.bpm_down_button.draw(self.screen)
        self.beats_up_button.draw(self.screen)
        self.beats_down_button.draw(self.screen)

        # Draw exercise buttons
        for i, button in enumerate(self.exercise_buttons):
            button.color = HIGHLIGHT_COLOR if i == self.selected_exercise else LIGHT_BLUE
            button.draw(self.screen)

        # BPM and Beats Per Bar display
        font = pygame.font.SysFont(None, 36)
        bpm_text = font.render(f'BPM: {self.bpm}', True, BLACK)
        beats_text = font.render(f'Beats/Bar: {self.beats_per_bar}', True, BLACK)
        self.screen.blit(bpm_text, (60, 10))
        self.screen.blit(beats_text, (60, 50))
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
    menu_ui = MenuUI(screen)
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
