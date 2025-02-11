import pygame

from groops import all_sprites, buttons_group
from tools.game_tools import terminate
from tools.load_tools import load_image
from const import RED, BLACK, FPS, INTRO_TEXT, LEVEL_TEXT, DOP_TEXT, SIZE, WIDTH, HEIGHT

pygame.mixer.init()
sound = pygame.mixer.Sound("data/sound/level_1.mp3")
sound.set_volume(0.5)
sound.play(-1)
pygame.display.set_icon(load_image("img/ico.png"))
pygame.display.set_caption("MOVE")


class GameState:
    def __init__(self):
        self.menu = True
        self.name_level = ""

    def set_menu_state(self, state):
        self.menu = state

    def set_name_level(self, level_name):
        self.name_level = level_name

    def get_menu_state(self):
        return self.menu

    def get_name_level(self):
        return self.name_level


class MenuButton(pygame.sprite.Sprite):
    def __init__(self, groups, text, font, colour, move):
        super().__init__(*groups)
        self.image = font.render(text, 1, colour)
        self.text = text
        self.rect = pygame.Rect(move[0] - self.image.get_rect().w // 2, move[1] - self.image.get_rect().h // 2,
                                self.image.get_rect().w, self.image.get_rect().h)

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            if self.text == INTRO_TEXT[1]:
                next_screen_menu(screen_menu, LEVEL_TEXT)
            elif self.text == INTRO_TEXT[2]:
                next_screen_menu(screen_menu, DOP_TEXT)
            elif self.text == "Выход":
                terminate()
            elif self.text == "Подземелье":
                game_state.set_menu_state(False)
                game_state.set_name_level("dungeon")
            elif self.text == "Обучение":
                game_state.set_menu_state(False)
                game_state.set_name_level("tytorial")
            elif self.text == "Skeleton Rush":
                game_state.set_menu_state(False)
                game_state.set_name_level("skeleton_rush")
            elif self.text == "В главное меню":
                game_state.set_menu_state(True)
                next_screen_menu(screen_menu, INTRO_TEXT)
                return False
            elif self.text == "Перезапуск":
                return False
            elif self.text == "Обратно к игре":
                return 42
            elif self.text == "Назад":
                next_screen_menu(screen_menu, INTRO_TEXT)
        return True


def next_screen_menu(screen, text):
    screen.fill(BLACK)
    for button in buttons_group:
        button.kill()
    information_screen(screen, clock, FPS, RED, text)


def information_screen(screen, clock, fps, color, menu_text):
    pygame.font.init()
    font = pygame.font.Font(None, 64)
    text_coord_x, text_coord_y = WIDTH // 2, HEIGHT // 2 - (64 * 4)
    for line in menu_text:
        MenuButton((all_sprites, buttons_group), line, font, color,
                   (text_coord_x, text_coord_y))
        text_coord_y += 96 if text_coord_y != 128 else 192
        buttons_group.draw(screen)
        pygame.display.flip()

    while game_state.get_menu_state():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            buttons_group.update(event)
        pygame.display.flip()
        clock.tick(fps)
    for button in buttons_group:
        button.kill()


screen_menu = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
game_state = GameState()
