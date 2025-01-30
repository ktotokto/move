from pygame import sprite

all_sprites, wall_group, enemy_group, player_group, effects_group, attack_group, menu_group \
    = (sprite.Group(), sprite.Group(), sprite.Group(),
       sprite.Group(), sprite.Group(), sprite.Group(), sprite.Group())
