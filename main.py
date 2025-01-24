import pygame

from classes import Camera
from tools import load_image, terminate, generate_level, load_level
from groops import all_sprites, enemy_group


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
        clock.tick(10)


BLACK = pygame.Color("#000000")
RED = pygame.Color("#ff0000")
SIZE = WIDTH, HEIGHT = (1024, 800)
FPS = 20

player_image = load_image('ger.png')
tile_image = {"p1": load_image('test_pol.png'), "st": load_image('test_block.png'),
              "enemy": load_image('test_enemy.png')}

player, level_x, level_y = generate_level(load_level('level_test.txt'), player_image)
camera = Camera(WIDTH, HEIGHT)
pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("MOVE")
clock = pygame.time.Clock()

camera.update(player)
for sprite in all_sprites:
    camera.apply(sprite)
for i in range(4):
    screen.fill(BLACK)
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(10)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            for enemy in enemy_group:
                enemy.move()
            player.move(event.key)
            for i in range(4):
                screen.fill(BLACK)
                player.update_sprite(event.key)
                all_sprites.draw(screen)
                all_sprites.update()
                pygame.display.flip()
                clock.tick(20)
