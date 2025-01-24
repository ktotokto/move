import pygame
import os
import sys


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        self.image = load_image(image)
        self.rect = self.image.get_rect().move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])


class Wall(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        self.image = load_image(image)
        self.rect = pygame.Rect(0, 0, 64, 29).move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        self.image, self.tile_size = load_image(image), tile_size
        self.rect = self.image.get_rect().move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])

    def move(self):
        self.rect = self.rect.move(self.tile_size[0] // 2, 0)


class Camera:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.w // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.h // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups):
        super().__init__(*groups)
        self.frames, self.cur_frame, self.list_move, self.count_move, self.flag_revers = [], 0, [0, 0, 1, 1], 0, False
        self.tile_height, self.tile_width = tile_height, tile_width
        self.conflict_groups = conflict_groups
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(24, 0, 49, 64)
        w, h = sheet.get_width() // columns, sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (w * i, h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (w, h))))

    def update_sprite(self, key):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.list_move[self.count_move]:
            self.rect = pygame.Rect(self.rect.x + self.delta_x, self.rect.y + self.delta_y_start, 49, 64)
        else:
            self.rect = pygame.Rect(self.rect.x + self.delta_x, self.rect.y + self.delta_y_end, 49, 64)
        self.count_move += 1
        if self.count_move == 4:
            self.count_move = 0

        if key == pygame.K_LEFT:
            self.rect = self.rect.move(-8, 0) if not self.flag_revers else self.rect.move(0, 0)
            self.flag_revers = True
        if key == pygame.K_RIGHT:
            self.rect = self.rect.move(8, 0) if self.flag_revers else self.rect.move(0, 0)
            self.flag_revers = False
        if self.flag_revers:
            self.image = pygame.transform.flip(self.image, True, False)

    def move(self, key):
        self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
        if key == pygame.K_UP:
            self.delta_x, self.delta_y_start, self.delta_y_end \
                = 0, -self.tile_height // 4, -self.tile_height // 4
        if key == pygame.K_DOWN:
            self.delta_x, self.delta_y_start, self.delta_y_end \
                = 0, self.tile_height // 4, self.tile_height // 4
        if key == pygame.K_LEFT:
            self.delta_x, self.delta_y_start, self.delta_y_end \
                = -self.tile_width // 4, self.tile_height // 4, -self.tile_height // 4
        if key == pygame.K_RIGHT:
            self.delta_x, self.delta_y_start, self.delta_y_end \
                = self.tile_width // 4, self.tile_height // 4, -self.tile_height // 4
        self.rect = pygame.Rect(self.rect.x + self.delta_x * 2, self.rect.y + self.delta_y_start * 2, 49, 64)
        self.rect = pygame.Rect(self.rect.x + self.delta_x * 2, self.rect.y + self.delta_y_end * 2, 49, 64)
        if pygame.sprite.spritecollideany(self, *self.conflict_groups):
            self.rect = pygame.Rect(self.rect.x - self.delta_x * 2, self.rect.y - self.delta_y_start * 2, 49, 64)
            self.rect = pygame.Rect(self.rect.x - self.delta_x * 2, self.rect.y - self.delta_y_end * 2, 49, 64)
            self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
        self.rect = pygame.Rect(self.rect.x - self.delta_x * 2, self.rect.y - self.delta_y_start * 2, 49, 64)
        self.rect = pygame.Rect(self.rect.x - self.delta_x * 2, self.rect.y - self.delta_y_end * 2, 49, 64)
