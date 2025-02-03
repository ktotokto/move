import pygame
import os
import sys
from groops import all_sprites, effects_group, enemy_group, attack_group
from random import randint

pygame.mixer.init()


def load_image(name, directory):
    fullname = os.path.join(directory, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class AnimationSprite(pygame.sprite.Sprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups=None):
        super().__init__(*groups)
        self.frames, self.cur_frame = [], 0
        self.tile_height, self.tile_width = tile_height, tile_width
        self.conflict_groups = conflict_groups

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, self.tile_height, self.tile_width)
        w, h = sheet.get_width() // columns, sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (w * i, h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (w, h))))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        image = load_image(image, 'data')
        self.image = pygame.transform.scale(image, (image.get_width() * 2.5, image.get_height() * 2.5))
        self.rect = self.image.get_rect().move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])


class Door(Tile):
    def __init__(self, groups, player_group, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(groups, pos_x, pos_y, image, tile_size, move)
        self.player_group = player_group
        self.sound = pygame.mixer.Sound('data/sound/knock_door.mp3')

    def update(self):
        for player in self.player_group:
            if self.rect.colliderect(player):
                self.sound.play()
                self.kill()


class Torch(AnimationSprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups=None):
        super().__init__(groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups)
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * 3, sheet.get_height() * 3))
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[self.cur_frame]
        size_image = self.image.get_rect()
        self.rect = self.rect.move(x * tile_width + tile_width // 2 - size_image.w // 2,
                                   y * tile_height + tile_height // 2 - size_image.h)


class Wall(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        image = load_image(image, 'data')
        self.image = pygame.transform.scale(image, (image.get_width() * 2.6, image.get_height() * 2.5))
        self.rect = pygame.Rect(0, 0, 64, 29).move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])


class Enemy(AnimationSprite):
    def __init__(self, groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height, sound_url,
                 conflict_groups=None):
        super().__init__(groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups)
        self.sound_dead = pygame.mixer.Sound(sound_url)
        self.hit_points, self.damage = hit_points, damage
        self.list_move, self.flag_revers, self.sheet_index = [0, 0, 1, 1], False, 0
        self.cut_sheet(sheet[self.sheet_index], columns, rows)
        self.sheet, self.columns, self.rows = sheet, columns, rows
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_width, y * tile_height)

    def damage_counter(self, damage):
        self.hit_points -= damage
        if self.hit_points <= 0:
            self.sound_dead.play()
            self.kill()


class Skeleton(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height, sound_url,
                 conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height, sound_url,
                         conflict_groups)

    def update_move(self, count_move):
        self.rect = self.rect.move(self.delta_x, self.delta_y)

    def move(self):
        while True:
            self.delta_x, self.delta_y = 0, 0
            move, axis_x = randint(-1, 1), randint(0, 1)
            if axis_x:
                self.delta_x = self.tile_width * move // 4
            else:
                self.delta_y = self.tile_height * move // 4
            self.rect = self.rect.move(self.delta_x * 4, self.delta_y * 4)
            if pygame.sprite.spritecollideany(self, *self.conflict_groups):
                self.rect = self.rect.move(-self.delta_x * 4, -self.delta_y * 4)
                self.delta_x, self.delta_y = 0, 0
            else:
                self.rect = self.rect.move(-self.delta_x * 4, -self.delta_y * 4)
                break

            x, y = self.rect.x, self.rect.y
            self.sheet_index = (self.sheet_index + 1) % len(self.sheet)
            self.frames, self.cur_frame = [], 0
            self.cut_sheet(self.sheet[self.sheet_index], self.columns, self.rows)
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(x, y)

    def attack(self):
        pass


class Attack(pygame.sprite.Sprite):
    def __init__(self, groups, damage, conflict_groups, images_list, sprite, shift, revers=(False, 0)):
        super().__init__(*groups)
        self.images_list, self.image_index = [
            pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))
            for image in images_list], 0
        self.revers, self.damage, self.damage_flag = revers, damage, True
        self.image = self.images_list[self.image_index]
        self.image_revers()
        self.conflict_groups = conflict_groups
        self.rect = pygame.Rect(sprite.rect.x + shift[0],
                                sprite.rect.y + shift[1], 1, 1)
        pygame.mixer.Sound('data/sound/attack_sound_1.mp3').play()

    def update_effect(self):
        if self.damage_flag:
            for group in self.conflict_groups:
                for sprite in group:
                    if self.rect.colliderect(sprite):
                        sprite.damage_counter(self.damage)
        self.damage_flag = False
        self.image_index += 1
        if self.image_index == len(self.images_list) - 1:
            self.kill()
        else:
            self.image = self.images_list[self.image_index]
            self.image_revers()

    def image_revers(self):
        self.image = pygame.transform.flip(self.image, self.revers[0], False)
        if self.revers[1] == 1:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.revers[1] == -1:
            self.image = pygame.transform.rotate(self.image, -90)


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


class Player(AnimationSprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups=None):
        super().__init__(groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups)
        self.list_move, self.flag_revers_horizontal, self.attack_flag = [0, 0, 1, 1], False, False
        self.flag_revers_attack = (False, 0)
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * 2.9, sheet.get_height() * 2.9))
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_height, y * tile_width - 12)

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
        self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
        keys_move = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        attack_x, attack_y = 0, 0
        if key in keys_move:
            if key == keys_move[0]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = 0, -self.tile_height // 4, -self.tile_height // 4
                self.flag_revers_attack = (False, 1)
                attack_x, attack_y = 22, -30
            if key == keys_move[1]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = 0, self.tile_height // 4, self.tile_height // 4
                self.flag_revers_attack = (False, -1)
                attack_x, attack_y = 22, 84
            if key == keys_move[2]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = -self.tile_width // 4, -self.tile_height // 4, self.tile_height // 4
                self.flag_revers_horizontal = True
                self.flag_revers_attack = (True, 0)
                attack_x, attack_y = -34, 30
            if key == keys_move[3]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = self.tile_width // 4, -self.tile_height // 4, self.tile_height // 4
                self.flag_revers_horizontal = False
                self.flag_revers_attack = (False, 0)
                attack_x, attack_y = 66, 30
            if self.attack_flag:
                image_list = [load_image(image, 'data/img/sword_attack') for image in
                              os.listdir('data/img/sword_attack')]
                Attack((all_sprites, effects_group, attack_group), 1, (enemy_group,), image_list, self,
                       (attack_x, attack_y), self.flag_revers_attack)
                self.attack_flag = False
                self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
                return True
            else:
                self.rect = self.rect.move(self.delta_x * 4, self.delta_y_start * 2 + self.delta_y_end * 2)
                if pygame.sprite.spritecollideany(self, *self.conflict_groups):
                    for group in self.conflict_groups:
                        group.update()
                    self.rect = self.rect.move(-self.delta_x * 4, -self.delta_y_start * 2 - self.delta_y_end * 2)
                    self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
                    return False
                self.rect = self.rect.move(-self.delta_x * 4, -self.delta_y_start * 2 - self.delta_y_end * 2)
            return True
        elif key == pygame.K_q:
            self.attack_flag = False if self.attack_flag else True
        return False


class Wizard(Enemy):
    def __init__(self, groups, hit_points, damage, sheet, columns, rows, x, y, tile_width, tile_height, sound_url,
                 conflict_groups=None):
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        super().__init__(groups, sheet, hit_points, damage, columns, rows, x, y, tile_width, tile_height, sound_url,
                         conflict_groups)
