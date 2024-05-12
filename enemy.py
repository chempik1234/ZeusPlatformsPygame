from random import randint

import pygame

from sprite import load_image, MySprite


class Enemy:
    def __init__(self, x, y, sprites_group, enemy_group, bullets_group, height=100):
        image = load_image(f"enemy{randint(0, 2)}.png")
        self.sprite = MySprite(enemy_group,
                               pygame.transform.scale(image,
                                                      (int(image.get_width() * height / image.get_height()),
                                                       height)),
                               x, y)
        self.sprite.parent = self
        self.sprites_group = sprites_group
        self.bullets_group = bullets_group

    def update(self):
        for attack in self.bullets_group:
            if pygame.sprite.collide_rect(self.sprite, attack):
                self.sprite.kill()
