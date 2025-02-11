import pygame
import time

from tools.load_tools import load_image, load_level, draw_text
from tools.game_tools import terminate, generate_level
from groops import all_sprites, enemy_group, effects_group, stat, buttons_group
from enemy_move import move_a, loader_move
from classes.effects import HeartBar
from classes.base_classes import Camera, Item
from start_end_screen import information_screen, MenuButton, screen_menu, game_state
from const import BLACK, RED, GREEN, WHITE, SIZE, WIDTH, HEIGHT, FPS, MENU_TEXT, INTRO_TEXT, WIN_TEXT, DEFEAT_TEXT

clock = pygame.time.Clock()
information_screen(screen_menu, clock, FPS, RED, INTRO_TEXT)


def start_level():
    name_level = game_state.get_name_level()
    player_image = load_image('img/ger.png')
    player, level_x, level_y, win_tile = generate_level(load_level(f'maps/{name_level}.txt'), player_image, name_level)
    items = [Item('Меч', 'Оружие ближнего боя', 1), Item('Золото', '', player.gold),
             Item('Зелье здоровья', 'Востанавливает 2 xp', 5)]
    count_move = 0
    camera = Camera(WIDTH, HEIGHT)
    pygame.init()
    inventory_open, game, menu, animation, draw_win_defeat = False, True, False, False, False
    selected_item_index = 0
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("MOVE")
    start_time = time.time()
    tick_effect, tick_move, tick_animation = 0, 0, 0
    heart_bar = HeartBar((10, 10), 5)

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    loader_move.update_init_coord(camera)
    loader_move.load_level_move(camera)
    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()
    pygame.mixer.music.stop()
    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if (menu or win_tile.win or player.defeat) and event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons_group:
                    button_remove = button.update(event)
                    if not button_remove:
                        game = False
                    elif button_remove == 42:
                        menu = not menu
            if player.defeat and not draw_win_defeat:
                draw_win_defeat = True
                screen.fill(BLACK)
                for i, item_menu in enumerate(DEFEAT_TEXT + [f"{elem}: {stat[elem]}" for elem in stat]):
                    font = pygame.font.Font(None, 64)
                    text_coord_x, text_coord_y = WIDTH // 2, HEIGHT // 2 - (64 * 5)
                    MenuButton((all_sprites, buttons_group), item_menu, font, RED,
                               (text_coord_x, text_coord_y + i * 64))
                buttons_group.draw(screen)
            if win_tile.win and not draw_win_defeat:
                draw_win_defeat = True
                screen.fill(BLACK)
                for i, item_menu in enumerate(WIN_TEXT + [f"{elem}: {stat[elem]}" for elem in stat]):
                    font = pygame.font.Font(None, 64)
                    text_coord_x, text_coord_y = WIDTH // 2, HEIGHT // 2 - (64 * 5)
                    MenuButton((all_sprites, buttons_group), item_menu, font, RED,
                               (text_coord_x, text_coord_y + i * 64))
                buttons_group.draw(screen)
            elif event.type == pygame.KEYDOWN and not animation:
                if event.key == pygame.K_ESCAPE and not inventory_open:
                    menu = not menu
                    if menu:
                        for i, item_menu in enumerate(MENU_TEXT):
                            font = pygame.font.Font(None, 64)
                            text_coord_x, text_coord_y = WIDTH // 2, HEIGHT // 2 - (64 * 2)
                            MenuButton((all_sprites, buttons_group), item_menu, font, RED,
                                       (text_coord_x, text_coord_y + i * 96))
                        buttons_group.draw(screen)
                else:
                    if event.key == pygame.K_i:
                        inventory_open = not inventory_open
                        for item in items:
                            if item.name == "Золото":
                                item.col = player.gold
                if inventory_open:
                    if event.key == pygame.K_UP and selected_item_index > 0:
                        selected_item_index -= 1
                    elif event.key == pygame.K_DOWN and selected_item_index < len(items) - 1:
                        selected_item_index += 1
                    elif event.key == pygame.K_e:
                        if items[selected_item_index].name == "Зелье здоровья" and items[selected_item_index].col > 0:
                            items[selected_item_index].col -= 1
                            player.hit_points += 2
                            player.hit_points = 5 if player.hit_points > player.max_hit_points else player.hit_points
                else:
                    animation = True if player.move(event.key) else False
                    if animation:
                        for enemy in enemy_group:
                            if (player.rect.x // 64, (player.rect.y + 12) // 64) in enemy.get_attack_list():
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
        if inventory_open:
            screen.fill(BLACK)
            font = pygame.font.Font(None, 32)
            draw_text("Инвентарь:", font, WHITE, screen, 20, 20)
            for i, item in enumerate(items):
                color = GREEN if i == selected_item_index else WHITE
                draw_text(f"{i + 1}. {item.name} {item.col}x", font, color, screen, 40, 60 + i * 30)
                if i == selected_item_index:
                    draw_text(item.description, font, RED, screen, 300, 50 + i * 30)
        elif menu or win_tile.win or player.defeat:
            pass
        else:
            for button in buttons_group:
                button.kill()
            tick_animation = 0 if tick_animation > 16 else tick_animation + 1
            tick_effect = 0 if tick_effect > 8 else tick_effect + 1
            tick_move = 0 if tick_move > 4 else tick_move + 1
            if animation:
                if tick_move == 0:
                    list_move = [(player.rect.x + player.delta_x * 4,
                                  player.rect.y + 12 + player.delta_y_start * 2 + player.delta_y_end * 2)]
                    player.update_sprite(count_move)
                    for enemy in enemy_group:
                        if count_move == 0:
                            move = (enemy.rect.x + enemy.delta_x, enemy.rect.y + enemy.delta_y)
                            if (move[0], move[1]) in list_move:
                                enemy.delta_x, enemy.delta_y = 0, 0
                            else:
                                list_move.append(move)
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
            heart_bar.update(player.hit_points)
            heart_bar.draw(screen)
            if not menu:
                for button in buttons_group:
                    button.kill()
        pygame.display.flip()
        clock.tick(FPS)
        if not win_tile.win:
            stat["Золото собрано"] = player.gold
            stat["Время в игре"] = round(time.time() - start_time, 2)
    for sprite in all_sprites:
        sprite.kill()


while True:
    start_level()
    stat["Врагов убито"] = 0
