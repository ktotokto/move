import pygame

from classes.base_classes import load_image, AnimationSprite
from groops import player_group


class Tile(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        image = load_image(image)
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
        image = load_image(image)
        self.image = pygame.transform.scale(image, (image.get_width() * 2.6, image.get_height() * 2.5))
        self.rect = pygame.Rect(0, 0, 64, 29).move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])


class Loot(pygame.sprite.Sprite):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(*groups)
        image = load_image(image)
        self.image = pygame.transform.scale(image, (image.get_width() * 2.6, image.get_height() * 2.6))
        self.rect = pygame.Rect(0, 0, 64, 29).move(
            tile_size[0] * pos_x + move[0], tile_size[1] * pos_y + move[1])

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            for player in player_group:
                player.gold += 1
            self.kill()


class Win(Tile):
    def __init__(self, groups, pos_x, pos_y, image, tile_size, move=(0, 0)):
        super().__init__(groups, pos_x, pos_y, image, tile_size, move)
        self.win = False

    def update(self):
        for player in player_group:
            if (player.rect.x // 64, (player.rect.y + 12) // 64) == (self.rect.x // 64, self.rect.y // 64):
                self.win = True
