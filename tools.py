import pygame
import os
import sys
from classes import Tile, Enemy, Player, Wall
from groops import all_sprites, enemy_group, wall_group

tile_width = tile_height = 64


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def start_screen(screen, w, h, colour, clock, fps):
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (w, h))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, colour)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level, player_image):
    new_player, x, y = None, None, None
    player_x, player_y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                player_x, player_y = x, y
                Tile((all_sprites,), x, y, 'test_pol.png', (64, 64), (0, 35))
            elif level[y][x] == '1':
                Tile((all_sprites,), x, y, 'test_pol.png', (64, 64), (0, 35))
            elif level[y][x] == '#':
                Wall((all_sprites, wall_group), x, y, 'test_block.png', (64, 64))
            elif level[y][x] == '!':
                Enemy((all_sprites, enemy_group), x, y, 'test_enemy.png', (64, 64))
                Tile((all_sprites,), x, y, 'test_pol.png', (64, 64), (0, 35))

    new_player = Player((all_sprites,), player_image, 4, 1, 49, 64, tile_width, tile_height, (wall_group,))
    return new_player, x, y
