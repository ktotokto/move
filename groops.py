from pygame import sprite

all_sprites, wall_group, enemy_group, player_group, effects_group, attack_group, menu_group, buttons_group \
    = (sprite.Group(), sprite.Group(), sprite.Group(),
       sprite.Group(), sprite.Group(), sprite.Group(), sprite.Group(), sprite.Group())
stat = {"kill_enemy": 0, "time": 0, "gold": 0}
