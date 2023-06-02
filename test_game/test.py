import copy
import random

import pygame as pg

pg.init()


def main():
    sprite_image = pg.Surface((150, 120))
    sprite_image.fill(pg.Color('dodgerblue1'))
    sprite_image.set_alpha(128)

    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()
    sprite = pg.sprite.Sprite()
    sprite.image = sprite_image
    sprite.rect = sprite.image.get_rect(center=screen.get_rect().center)

    sprite_group = []
    for _ in range(5000):
        sprite = pg.sprite.Sprite()
        sprite.image = sprite_image
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = random.randint(0, screen.get_width())
        sprite.rect.y = random.randint(0, screen.get_height())
        sprite.rect.width = 300
        sprite.rect.height = 300
        sprite_group.append(sprite)

    while 1:
        clock.tick(200)
        print(f"\r{clock.get_fps():.2f}", end='')
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()

        screen.fill((30, 30, 30))
        for sprite in sprite_group:
            screen.blit(sprite.image, sprite.rect)

        pg.display.flip()


if __name__ == '__main__':
    main()
