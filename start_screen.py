import sys

import pygame

from groops import all_sprites, buttons_group
from tools.game_tools import terminate

BLACK = pygame.Color("#000000")
RED = pygame.Color("#ff0000")
SIZE = WIDTH, HEIGHT = (1024, 800)
INTRO_TEXT = ["MOVE", "Начать игру", "Заставка", "Выход"]
LEVEL_TEXT = ["MOVE", "Обучение", "Первый уровень", "Skeleton Rush", "Назад"]
END_TEXT = ["MOVE", "Конец!", "Пока в разработке", "Назад"]
FPS = 60

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
menu = True
name_level = ""


class MenuButton(pygame.sprite.Sprite):
    def __init__(self, groups, text, font, colour, move):
        super().__init__(*groups)
        self.image = font.render(text, 1, colour)
        self.text = text
        self.rect = pygame.Rect(move[0] - self.image.get_rect().w // 2, move[1] - self.image.get_rect().h // 2,
                                self.image.get_rect().w, self.image.get_rect().h)

    def update(self, *args):
        global name_level, menu
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            if self.text == INTRO_TEXT[1]:
                next_screen_menu(screen, LEVEL_TEXT)
            elif self.text == INTRO_TEXT[2]:
                next_screen_menu(screen, END_TEXT)
            elif self.text == INTRO_TEXT[3]:
                terminate()
            elif self.text == "Первый уровень":
                name_level = "level_1"
                menu = False
            elif self.text == "Назад":
                next_screen_menu(screen, INTRO_TEXT)


def next_screen_menu(screen, text):
    screen.fill(BLACK)
    for button in buttons_group:
        button.kill()
    start_screen(screen, clock, FPS, RED, text)


def start_screen(screen, clock, fps, color, menu_text):
    pygame.font.init()
    font = pygame.font.Font(None, 64)
    text_coord_x, text_coord_y = WIDTH // 2, HEIGHT // 2 - (64 * 4)
    for line in menu_text:
        MenuButton((all_sprites, buttons_group), line, font, color,
                   (text_coord_x, text_coord_y))
        text_coord_y += 64 if text_coord_y != 144 else 192
        buttons_group.draw(screen)
        pygame.display.flip()

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            buttons_group.update(event)
        pygame.display.flip()
        clock.tick(fps)
    if not menu:
        for button in buttons_group:
            button.kill()


start_screen(screen, clock, FPS, RED, INTRO_TEXT)
