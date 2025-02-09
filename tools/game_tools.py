import pygame
import sys

from tools.load_tools import load_image
from classes.enemys import Skeleton, Beholder, Zombie, Bat, Boss
from classes.environment import Tile, Wall, Torch, Door
from classes.base_classes import Player
from groops import all_sprites, enemy_group, wall_group, player_group
from random import randint
from os import listdir

tile_width = tile_height = 64


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level, player_image, name_level):
    new_player, x, y = None, None, None
    player_x, player_y = None, None
    link_tile, link_wall = f'img/tiles_{name_level}', f'img/walls_{name_level}'
    len_list_tiles, list_walls = len(listdir(f'data/{link_tile}')), listdir(f'data/{link_wall}')
    enemy_list = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            for i in range(1, len_list_tiles + 1):
                if level[y][x] == str(i):
                    Tile((all_sprites,), x, y, f'{link_tile}/{i}.png', (tile_width, tile_height), (0, 35))
            for wall in list_walls:
                if level[y][x] == wall.split(".")[0]:
                    Wall((all_sprites, wall_group), x, y, f'{link_wall}/{wall}', (tile_width, tile_height))
            if level[y][x] == '@':
                player_x, player_y = x, y
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
            elif level[y][x] == 'S':
                enemy_list.append(('S', x, y))
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
            elif level[y][x] == 's':
                enemy_list.append(('s', x, y))
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
            elif level[y][x] == 'G':
                enemy_list.append(('G', x, y))
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
            elif level[y][x] == '!':
                Wall((all_sprites, wall_group), x, y, f'img/{link_wall}/1.png', (tile_width, tile_height))
                Torch((all_sprites,), load_image('img/torch_wall.png'), 3, 1, x, y, tile_width, tile_height)
            elif level[y][x] == "D":
                Tile((all_sprites,), x, y, 'img/tile.png', (tile_width, tile_height), (0, 35))
                Door((all_sprites, wall_group), player_group, x, y, 'img/door_1.png', (tile_width, tile_height),
                     (0, 35))
            elif level[y][x] == 'B':
                enemy_list.append(('B', x, y))
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
            elif level[y][x] == 'Z':
                enemy_list.append(('Z', x, y))
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
            elif level[y][x] == '*':
                enemy_list.append(('*', x, y))
                Tile((all_sprites,), x, y, f'{link_tile}/{str(randint(1, len_list_tiles))}.png',
                     (tile_width, tile_height), (0, 35))
    for enemy in enemy_list:
        if enemy[0] == 'S':
            Skeleton((all_sprites, enemy_group), 1, 0.5,
                     (load_image('img/skeleton_1.png'), load_image('img/skeleton_2.png')), 4, 1, enemy[1], enemy[2],
                     tile_width, tile_height, 'data/sound/skel_death.mp3', (wall_group, player_group, enemy_group))
        elif enemy[0] == 's':
            image = 'img/skeleton_shield.png'
            Skeleton((all_sprites, enemy_group), 1, 1,
                     (load_image(image), load_image(image)), 6, 1, enemy[1], enemy[2],
                     tile_width, tile_height, 'data/sound/skel_death.mp3', (wall_group, player_group, enemy_group))
        elif enemy[0] == 'G':
            image = 'img/boss.png'
            Boss((all_sprites, enemy_group), 4, 1,
                 (load_image(image), load_image(image)), 8, 1, enemy[1], enemy[2],
                 tile_width, tile_height, 'data/sound/skel_death.mp3', (wall_group, player_group, enemy_group))
        elif enemy[0] == 'B':
            Bat((all_sprites, enemy_group), 1, 0.5,
                (load_image('img/bat.png'),), 4, 1, enemy[1], enemy[2],
                tile_width, tile_height, 'data/sound/skel_death.mp3', (wall_group, player_group, enemy_group))
        elif enemy[0] == 'Z':
            Zombie((all_sprites, enemy_group), 2, 1,
                   (load_image('img/zombie.png'),), 8, 1, enemy[1], enemy[2],
                   tile_width, tile_height, 'data/sound/skel_death.mp3', (wall_group, player_group, enemy_group))
        elif enemy[0] == '*':
            Beholder((all_sprites, enemy_group), 3, 1,
                     (load_image('img/beholder.png'),), 4, 1, enemy[1], enemy[2],
                     tile_width, tile_height, 'data/sound/skel_death.mp3', (wall_group, player_group, enemy_group))
    new_player = Player((all_sprites, player_group), player_image, 4, 1, player_x, player_y, tile_width, tile_height,
                        (wall_group, enemy_group))
    return new_player, x, y
