import pygame
import os
import sys
from groops import all_sprites, effects_group


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


class Skeleton(AnimationSprite):
    def __init__(self, groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups=None):
        super().__init__(groups, sheet, columns, rows, x, y, tile_width, tile_height, conflict_groups)
        self.list_move, self.flag_revers, self.sheet_index = [0, 0, 1, 1], False, 0
        sheet = [pygame.transform.scale(sheet[i], (sheet[i].get_width() * 2.6, sheet[i].get_height() * 2.6)) for i in
                 range(len(sheet))]
        self.cut_sheet(sheet[self.sheet_index], columns, rows)
        self.sheet, self.columns, self.rows = sheet, columns, rows
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_height + 8, y * tile_width)

    def update_move(self, count_move):
        if self.list_move[count_move]:
            self.rect = self.rect.move(self.delta_x, self.delta_y_end)
        else:
            self.rect = self.rect.move(self.delta_x, self.delta_y_start)

    def move(self):
        self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
        a = False
        if a:
            self.delta_x, self.delta_y_start, self.delta_y_end \
                = -self.tile_width // 4, -self.tile_height // 4, self.tile_height // 4
            x, y = self.rect.x, self.rect.y
            self.sheet_index = (self.sheet_index + 1) % len(self.sheet)
            self.frames, self.cur_frame = [], 0
            self.cut_sheet(self.sheet[self.sheet_index], self.columns, self.rows)
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(x, y)


class Attack(pygame.sprite.Sprite):
    def __init__(self, groups, images_list, sprite, tile_width, tile_height, shift, revers=(False, False)):
        super().__init__(*groups)
        self.images_list, self.image_index = [
            pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))
            for image in images_list], 0
        self.revers = revers
        self.image = self.images_list[self.image_index]
        self.image_revers()
        self.rect = pygame.Rect(sprite.rect.x + shift[0], sprite.rect.y + shift[1], tile_height, tile_width)
        self.sprite = sprite

    def update_effect(self):
        self.image_index += 1
        if self.image_index == len(self.images_list) - 1:
            self.kill()
        else:
            self.image = self.images_list[self.image_index]
            self.image_revers()

    def image_revers(self):
        self.image = pygame.transform.flip(self.image, self.revers[0], False)


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
        self.flag_revers_attack = (False, False)
        sheet = pygame.transform.scale(sheet, (sheet.get_width() * 2.9, sheet.get_height() * 2.9))
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x * tile_height + 8, y * tile_width)

    def update(self):
        pass

    def update_sprite(self, count_move):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.list_move[count_move]:
            self.rect = self.rect.move(self.delta_x, self.delta_y_end)
        else:
            self.rect = self.rect.move(self.delta_x, self.delta_y_start)
        self.image = pygame.transform.flip(self.image, self.flag_revers_horizontal, False)

    def move(self, key):
        self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
        keys_move = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        if key in keys_move:
            if key == keys_move[0]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = 0, -self.tile_height // 4, -self.tile_height // 4
                self.flag_revers_attack = (False, True)
            if key == keys_move[1]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = 0, self.tile_height // 4, self.tile_height // 4
                self.flag_revers_attack = (False, True)
            if key == keys_move[2]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = -self.tile_width // 4, -self.tile_height // 4, self.tile_height // 4
                self.rect = self.rect.move(-8, 0) if not self.flag_revers_horizontal else self.rect.move(0, 0)
                self.flag_revers_horizontal = True
                self.flag_revers_attack = (True, False)
            if key == keys_move[3]:
                self.delta_x, self.delta_y_start, self.delta_y_end \
                    = self.tile_width // 4, -self.tile_height // 4, self.tile_height // 4
                self.rect = self.rect.move(8, 0) if self.flag_revers_horizontal else self.rect.move(0, 0)
                self.flag_revers_horizontal = False
                self.flag_revers_attack = (False, False)
            if self.attack_flag:
                image_list = [load_image(image, 'data/sword_attack') for image in
                              os.listdir('data/sword_attack')]
                Attack((all_sprites, effects_group), image_list, self,
                       self.image.get_width(), self.image.get_height(),
                       (self.delta_x * 4, self.delta_y_start * 2 + self.delta_y_end * 2), self.flag_revers_attack)
                self.attack_flag = False
                return False
            else:
                self.rect = pygame.Rect(self.rect.x + self.delta_x * 4,
                                        self.rect.y + self.delta_y_start * 2 + self.delta_y_end * 2, 49, 64)
                if pygame.sprite.spritecollideany(self, *self.conflict_groups):
                    self.rect = pygame.Rect(self.rect.x - self.delta_x * 4,
                                            self.rect.y - self.delta_y_start * 2 - self.delta_y_end * 2, 49, 64)
                    self.delta_x, self.delta_y_start, self.delta_y_end = 0, 0, 0
                self.rect = pygame.Rect(self.rect.x - self.delta_x * 4,
                                        self.rect.y - self.delta_y_start * 2 - self.delta_y_end * 2, 49, 64)
            return True
        else:
            self.attack_flag = False if self.attack_flag else True
        return False
