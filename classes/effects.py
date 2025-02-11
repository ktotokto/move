import pygame

from tools.load_tools import load_image


class Attack(pygame.sprite.Sprite):
    def __init__(self, groups, damage, conflict_groups, images_list, sprite, shift, image_change, revers=(False, 0), sound="attack_sound_1.mp3"):
        super().__init__(*groups)
        self.images_list, self.image_index = [
            pygame.transform.scale(image, (image.get_width() * image_change, image.get_height() * image_change))
            for image in images_list], 0
        self.revers, self.damage, self.damage_flag = revers, damage, True
        self.image = self.images_list[self.image_index]
        self.image_revers()
        self.conflict_groups = conflict_groups
        self.rect = pygame.Rect(sprite.rect.x + shift[0],
                                sprite.rect.y + shift[1], 1, 1)
        pygame.mixer.Sound(f'data/sound/{sound}').play()

    def update_effect(self):
        if self.damage_flag:
            for group in self.conflict_groups:
                for sprite in group:
                    if (self.rect.x // 64, self.rect.y // 64) == (
                            (sprite.rect.x - sprite.delta_x) // 64, (sprite.rect.y + 12 - sprite.delta_y) // 64):
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


class HeartBar:
    def __init__(self, pos, max_hearts):
        self.pos = pos
        self.max_hearts = max_hearts
        img_size = load_image("img/full_heart.png").get_width() * 2, load_image("img/full_heart.png").get_height() * 2
        self.full_heart = pygame.transform.scale(load_image("img/full_heart.png"), (img_size[0], img_size[1]))
        self.half_heart = pygame.transform.scale(load_image("img/half_heart.png"), (img_size[0], img_size[1]))
        self.empty_heart = pygame.transform.scale(load_image("img/empty_heart.png"), (img_size[0], img_size[1]))
        self.hearts = [self.full_heart] * max_hearts

    def draw(self, screen):
        for i in range(len(self.hearts)):
            screen.blit(self.hearts[i], (self.pos[0] + i * self.full_heart.get_width(), self.pos[1]))

    def update(self, current_health):
        hearts_to_draw = []
        full_hearts = int(current_health)
        half_heart_needed = current_health % 1 != 0

        for i in range(full_hearts):
            hearts_to_draw.append(self.full_heart)

        if half_heart_needed:
            hearts_to_draw.append(self.half_heart)
        while len(hearts_to_draw) < self.max_hearts:
            hearts_to_draw.append(self.empty_heart)
        self.hearts = hearts_to_draw
