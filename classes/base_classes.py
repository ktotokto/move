import pygame
import os
import sys

from groops import all_sprites, effects_group, enemy_group, attack_group
from classes.effects import Attack
from tools.load_tools import load_image

pygame.mixer.init()


class AnimationSprite(pygame.sprite.Sprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height,
                 conflict_groups=None):
        super().__init__(*groups)
        self.frames, self.cur_frame = [], 0
        self.tile_height, self.tile_width = tile_height, tile_width
        self.conflict_groups = conflict_groups

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, self.tile_height, self.tile_width - 12)
        w, h = sheet.get_width() // columns, sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (w * i, h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (w, h))))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Camera:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -((target.rect.x + target.rect.w // 2 - self.w // 2) // 64) * 64
        self.dy = -((target.rect.y + target.rect.h // 2 - self.h // 2) // 64) * 64


class Player(AnimationSprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height,
                 conflict_groups=None):
        super().__init__(groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups)
        self.list_move, self.flag_revers_horizontal, self.attack_flag = [0, 0, 1, 1], False, False
        self.flag_revers_attack = (False, 0)
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * 2.9, sheet.get_height() * 2.9))
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_height, y * tile_width - 12)
        self.hit_points, self.attack_sprite, self.max_hit_points = 5, None, 5
        self.gold = 0

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.flip(self.image, self.flag_revers_horizontal, False)

    def update_sprite(self, count_move):
        self.update()
        if self.list_move[count_move]:
            self.rect = self.rect.move(self.delta_x, self.delta_y_end)
        else:
            self.rect = self.rect.move(self.delta_x, self.delta_y_start)

    def move(self, key):
        self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = 0, 0, 0, 0
        keys_move = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        attack_x, attack_y = 0, 0
        w, h = self.tile_width // 4, self.tile_height // 4
        if key in keys_move:
            if key == keys_move[0]:
                self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = 0, -h, -h, -h
                self.flag_revers_attack = (False, 1)
                attack_x, attack_y = 22, -30
            if key == keys_move[1]:
                self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = 0, h, h, h
                self.flag_revers_attack = (False, -1)
                attack_x, attack_y = 22, 84
            if key == keys_move[2]:
                self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = -w, -h, h, -h
                self.flag_revers_attack, self.flag_revers_horizontal = (True, 0), True
                attack_x, attack_y = -34, 30
            if key == keys_move[3]:
                self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = w, -h, h, -h
                self.flag_revers_attack, self.flag_revers_horizontal = (False, 0), False
                attack_x, attack_y = 66, 30
            if self.attack_flag:
                image_list = [load_image(f"img/sword_attack/{image}") for image in
                              os.listdir('data/img/sword_attack')]
                self.attack_sprite = Attack((all_sprites, effects_group, attack_group), 1, (enemy_group,), image_list,
                                            self, (attack_x, attack_y), 2, self.flag_revers_attack)
                self.attack_flag = False
                self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = 0, 0, 0, 0
                return True
            else:
                self.rect = self.rect.move(self.delta_x * 4, self.delta_y_start * 2 + self.delta_y_end * 2)
                for conflict_group in self.conflict_groups:
                    if pygame.sprite.spritecollideany(self, conflict_group):
                        conflict_group.update()
                        self.rect = self.rect.move(-self.delta_x * 4, -self.delta_y_start * 2 - self.delta_y_end * 2)
                        self.delta_x, self.delta_y_start, self.delta_y_end, self.delta_y = 0, 0, 0, 0
                        return False
                self.rect = self.rect.move(-self.delta_x * 4, -self.delta_y_start * 2 - self.delta_y_end * 2)
                return True
        elif key == pygame.K_q:
            self.attack_flag = False if self.attack_flag else True
        return False

    def damage_counter(self, damage):
        self.hit_points -= damage
        if self.hit_points <= 0:
            self.kill()


class Item:
    def __init__(self, name, description, col):
        self.name = name
        self.description = description
        self.col = col
