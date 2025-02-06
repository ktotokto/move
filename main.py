import pygame
import time

from classes import Camera
from tools import load_image, terminate, generate_level, load_level
from groops import all_sprites, enemy_group, effects_group, attack_group
from enemy_move import move_a, loader_move

BLACK = pygame.Color("#000000")
RED = pygame.Color("#ff0000")
GREEN = pygame.Color("#00ff00")
SIZE = WIDTH, HEIGHT = (1024, 768)
FPS = 60

player_image = load_image('img/ger.png')
player, level_x, level_y = generate_level(load_level('maps/level_test.txt'), player_image)
animation, count_move = False, 0
camera = Camera(WIDTH, HEIGHT)
pygame.init()
pygame.mixer.init()
sound_main = pygame.mixer.Sound('data/sound/level_1.mp3')
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("MOVE")
clock = pygame.time.Clock()
tick_effect, tick_move, tick_animation = 0, 0, 0

camera.update(player)
for sprite in all_sprites:
    camera.apply(sprite)
loader_move.update_init_coord(camera)
loader_move.load_level_move(camera)
screen.fill(BLACK)
all_sprites.draw(screen)
pygame.display.flip()
sound_main.set_volume(0)
sound_main.play()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN and not animation:
            animation = True if player.move(event.key) else False
            if animation:
                for enemy in enemy_group:
                    attack_enemy_list = [(enemy.rect.x // 64 - 1, enemy.rect.y // 64),
                                         (enemy.rect.x // 64 + 1, enemy.rect.y // 64),
                                         (enemy.rect.x // 64, enemy.rect.y // 64 - 1),
                                         (enemy.rect.x // 64, enemy.rect.y // 64 + 1)]
                    if (player.rect.x // 64, (player.rect.y + 12) // 64) in attack_enemy_list:
                        enemy.move('attack', player.rect.x, (player.rect.y + 12))
                    elif (player.rect.x // 64, (player.rect.y + 12) // 64) in enemy.update_vision(4):
                        x, y = move_a((player.rect.x // 64, (player.rect.y + 12) // 64),
                                      (enemy.rect.x // 64, enemy.rect.y // 64), camera)
                        enemy.move('chase', x, y)
                    else:
                        enemy.move('pass')
                    pygame.display.flip()
                camera.update(player)
                for sprite in all_sprites:
                    camera.apply(sprite)
                loader_move.update_init_coord(camera)
    tick_animation = 0 if tick_animation > 16 else tick_animation + 1
    tick_effect = 0 if tick_effect > 4 else tick_effect + 1
    tick_move = 0 if tick_move > 4 else tick_move + 1
    if animation:
        if tick_move == 0:
            player.update_sprite(count_move)
            for enemy in enemy_group:
                enemy.update_move(count_move)
            count_move += 1
            if count_move == len(player.list_move):
                animation, count_move = False, 0
    screen.fill(BLACK)
    if tick_animation == 0:
        all_sprites.update()
    if tick_effect == 0:
        for effect in effects_group:
            effect.update_effect()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
