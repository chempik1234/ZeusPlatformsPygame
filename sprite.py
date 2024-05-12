import os

import pygame


def load_image(name, color_key=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image.set_colorkey(image.get_at((49, 0)))
    else:
        image = image.convert_alpha()
    return image


class MySprite(pygame.sprite.Sprite):
    def __init__(self, group, image, x, y, parent=None):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)
        self.parent = parent

    def get_event(self, event):
        pass
