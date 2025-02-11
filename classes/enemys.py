import pygame
import os

from classes.base_classes import AnimationSprite, load_image
from classes.effects import Attack
from classes.environment import Loot
from groops import wall_group, all_sprites, effects_group, attack_group, player_group, enemy_group, stat
from random import randint, choice


class Enemy(AnimationSprite):
    def __init__(self, groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height,
                 sound_url, conflict_groups=None):
        super().__init__(groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups)
        self.sound_dead = pygame.mixer.Sound(sound_url)
        self.hit_points, self.damage = hit_points, damage
        self.list_move, self.flag_revers, self.sheet_index = [0, 0, 1, 1], False, 0
        self.cut_sheet(sheet[self.sheet_index], columns, rows)
        self.sheet, self.columns, self.rows = sheet, columns, rows
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_width, y * tile_height)
        self.delta_x, self.delta_y = 0, 0

    def update_vision(self, radius_vision):
        vision = set()
        coord_walls_list = [(wall.rect.x // 64, wall.rect.y // 64) for wall in wall_group]
        radius_list = [(radius_vision + 1, radius_vision + 1, 1, 1),
                       (radius_vision + 1, -(radius_vision + 1), 1, -1),
                       (-(radius_vision + 1), radius_vision + 1, -1, 1),
                       (-(radius_vision + 1), -(radius_vision + 1), -1, -1)]
        for end_x, end_y, step_x, step_y in radius_list:
            for y in range(0, end_y, step_y):
                flag_wall = True
                for x in range(0, end_x, step_x):
                    if (self.rect.x // 64 + x, self.rect.y // 64 + y) not in coord_walls_list and abs(y) + abs(
                            x) <= radius_vision:
                        vision.add((self.rect.x // 64 + x, self.rect.y // 64 + y))
                        flag_wall = False
                    else:
                        vision.add((self.rect.x // 64 + x, self.rect.y // 64 + y))
                        break
                if flag_wall:
                    break
        return vision

    def damage_counter(self, damage):
        self.hit_points -= damage
        if self.hit_points <= 0:
            self.sound_dead.play()
            Loot((all_sprites,), self.rect.x // 64, self.rect.y // 64, 'img/gold.png', (self.rect.w, self.rect.w))
            stat["Врагов убито"] += 1
            self.kill()

    def move(self, activity, x=0, y=0):
        self.delta_x, self.delta_y = 0, 0

        if activity == 'attack':
            self.attack(x, y)
        elif self.__class__ == Zombie:
            self.delta_x = self.tile_width * self.move_y
            if self.check_move(1):
                self.move_y = -self.move_y
                self.flag_revers_horizontal = (self.flag_revers_horizontal + 1) % 2
        elif activity == 'pass' or self.__class__ == Bat:
            move, axis_coord = choice([-1, 1]), randint(0, 1)
            if axis_coord:
                self.delta_x = self.tile_width * move
            else:
                self.delta_y = self.tile_height * move
        elif activity == 'chase':
            self.delta_x, self.delta_y = (x * 64 - self.rect.x), (y * 64 - self.rect.y)

        self.check_move(1)

    def check_move(self, count_move):
        self.rect = self.rect.move(self.delta_x // count_move, self.delta_y // count_move)
        for conflict_group in self.conflict_groups:
            flag_remove = False
            if self in conflict_group:
                conflict_group.remove(self)
                flag_remove = True
            if pygame.sprite.spritecollideany(self, conflict_group):
                self.rect = self.rect.move(-self.delta_x // count_move, -self.delta_y // count_move)
                self.delta_x, self.delta_y = 0, 0
                if flag_remove:
                    conflict_group.add(self)
                return True
            if flag_remove:
                conflict_group.add(self)
        self.rect = self.rect.move(-self.delta_x // count_move, -self.delta_y // count_move)
        return False

    def attack(self, player_x, player_y):
        if self.time_attack == 1:
            image_list = [load_image(f'img/enemy_melee_attack/{image}') for image in
                          os.listdir('data/img/enemy_melee_attack')]
            player_pos = (player_x - self.rect.x, player_y - self.rect.y)
            attack_revers_x = True if -player_pos[0] // 64 == 1 else False
            attack_revers_y = -player_pos[1] // 64
            self.attack_sprite = Attack((all_sprites, effects_group, attack_group), self.damage, (player_group,),
                                        image_list, self,
                                        (player_pos[0], player_pos[1]), 2, (attack_revers_x, attack_revers_y))
            self.time_attack = 0
        else:
            self.time_attack = 1

    def get_attack_list(self):
        x, y = self.rect.x // 64, self.rect.y // 64
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    def update_move(self, count_move):
        self.rect = self.rect.move(self.delta_x // 4, self.delta_y // 4)
        self.check_move(4)


class Skeleton(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height,
                 sound_url, conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height,
                         sound_url, conflict_groups)
        self.time_attack = 0

    def move(self, activity, x=0, y=0):
        super().move(activity, x, y)
        x, y = self.rect.x, self.rect.y
        self.sheet_index = (self.sheet_index + 1) % len(self.sheet)
        self.frames, self.cur_frame = [], 0
        self.cut_sheet(self.sheet[self.sheet_index], self.columns, self.rows)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)


class Bat(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height, sound_url,
                 conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height, sound_url,
                         conflict_groups)
        self.time_attack = 0


class Zombie(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height,
                 sound_url,
                 conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height,
                         sound_url, conflict_groups)
        self.time_attack = 0
        self.move_y = -1
        self.flag_revers_horizontal = 0

    def attack(self, player_x, player_y):
        if self.delta_x != 0 or self.delta_y != 0:
            self.time_attack = 0
        if self.time_attack == 1:
            image_list = [load_image(f'img/enemy_melee_attack/{image}') for image in
                          os.listdir('data/img/enemy_melee_attack')]
            player_pos = (player_x - self.rect.x, player_y - self.rect.y)
            attack_revers_x = True if -player_pos[0] // 64 == 1 else False
            attack_revers_y = -player_pos[1] // 64
            self.attack_sprite = Attack((all_sprites, effects_group, attack_group), self.damage, (player_group,),
                                        image_list, self,
                                        (player_pos[0], player_pos[1]), 2, (attack_revers_x, attack_revers_y))
            self.time_attack = 0
        else:
            self.time_attack = 1

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.flip(self.image, bool(self.flag_revers_horizontal), False)


class Beholder(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height, sound_url,
                 conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 3, sheet[i].get_height() * 3)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height, sound_url,
                         conflict_groups)
        self.time_attack = 0
        self.rect.center = (self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2)

    def move(self, activity, x=0, y=0):
        self.attack(x, y)

    def attack(self, player_x, player_y):
        if self.time_attack == 3:
            self.time_attack = 0
            image_list = [load_image(f'img/beholder_attack/{image}') for image in
                          os.listdir('data/img/beholder_attack')]
            for i in range(3):
                Attack((all_sprites, effects_group, attack_group), self.damage, (player_group, enemy_group),
                       image_list, self, (80 + (i * 64), 32), 2.6, (False, 0)).rect.h = 16
                Attack((all_sprites, effects_group, attack_group), self.damage, (player_group, enemy_group),
                       image_list, self, (-48 - (i * 64), 32), 2.6, (False, 0)).rect.h = 16
                Attack((all_sprites, effects_group, attack_group), self.damage, (player_group, enemy_group),
                       image_list, self, (16, 80 + (i * 64)), 2.6, (False, 1)).rect.h = 16
                Attack((all_sprites, effects_group, attack_group), self.damage, (player_group, enemy_group),
                       image_list, self, (16, -48 - (i * 64)), 2.6, (False, -1)).rect.h = 16
        else:
            self.time_attack += 1


class Boss(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height,
                 sound_url, conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height,
                         sound_url, conflict_groups)
        self.time_attack = 0

    def attack(self, player_x, player_y):
        if self.time_attack == 4:
            image_list = [load_image(f'img/dragon_attack/{image}') for image in
                          os.listdir('data/img/dragon_attack')]
            player_pos = (player_x - self.rect.x, player_y - self.rect.y)
            attack_revers_x = True if -player_pos[0] // 64 == 1 else False
            attack_revers_y = -player_pos[1] // 64
            self.attack_sprite = Attack((all_sprites, effects_group, attack_group), self.damage, (player_group,),
                                        image_list, self,
                                        (player_pos[0], player_pos[1]), 1, (attack_revers_x, attack_revers_y),
                                        "boss-attack.mp3")
            self.time_attack = 0
        else:
            self.time_attack += 1

    def get_attack_list(self):
        return self.update_vision(4)
