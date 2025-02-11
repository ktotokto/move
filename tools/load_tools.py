import pygame
import os
import sys
import sqlite3

from const import STAT_TEXT


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


class DataStat:
    def __init__(self, database_link):
        self.database_link = database_link

    def unload_sqlite(self, text):
        new_text = [line for line in text]
        with sqlite3.connect(f"data/sql/{self.database_link}") as file:
            cursor = file.cursor()
            query = '''SELECT kills, gold, time FROM global_stat'''
            cursor.execute(query)
            result = cursor.fetchone()
            for i, j in enumerate(range(1, 4)):
                new_text[j] = text[j] + str(result[i])
            return new_text

    def write_down(self, gold, kills, time):
        with sqlite3.connect(f"data/sql/{self.database_link}") as file:
            cursor = file.cursor()
            query = f''' UPDATE global_stat SET gold = gold + {gold}, \
             kills = kills + {kills}, time = time + {round(time / 60, 2)}'''
            cursor.execute(query)
            file.commit()
