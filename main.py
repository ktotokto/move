import pygame

from classes import Camera
from tools import load_image, terminate, generate_level, load_level
from groops import all_sprites, enemy_group, effects_group


def fps():
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    for enemy in enemy_group:
        enemy.move()
    for i in range(4):
        screen.fill(BLACK)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


BLACK = pygame.Color("#000000")
RED = pygame.Color("#ff0000")
SIZE = WIDTH, HEIGHT = (1024, 800)
FPS = 60

player_image = load_image('ger.png')
player, level_x, level_y = generate_level(load_level('level_test.txt'), player_image)
animation, count_move = False, 0
camera = Camera(WIDTH, HEIGHT)
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("MOVE")
clock = pygame.time.Clock()
ANIMATION_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ANIMATION_EVENT, 300)
tick_effect = -1

camera.update(player)
for sprite in all_sprites:
    camera.apply(sprite)
screen.fill(BLACK)
all_sprites.draw(screen)
pygame.display.flip()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN and not animation:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            for enemy in enemy_group:
                enemy.move()
            animation = True if player.move(event.key) else False
        if event.type == ANIMATION_EVENT:
            all_sprites.update()
    if animation:
        for enemy in enemy_group:
            enemy.update_move(count_move)
        player.update_sprite(count_move)
        count_move += 1
        if count_move == len(player.list_move):
            animation, count_move = False, 0
    tick_effect = 0 if tick_effect > 10 else tick_effect + 1
    screen.fill(BLACK)
    if tick_effect == 0:
        for effect in effects_group:
            effect.update_effect()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
