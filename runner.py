import pygame

from sprite import load_image, MySprite

RUNNING, JUMPING, FALLING, FALL_AFTER_JUMP = 1010, 2020, 3030, 4040


class Runner:
    def __init__(self, x, y, sprites_group, bullets_group, height=100, max_cd=2000):
        self.base_rect = None
        image = load_image("runner.png")
        self.sprite = MySprite(sprites_group,
                               pygame.transform.scale(image,
                                                      (int(image.get_width() * height / image.get_height()),
                                                       height)),
                               x, y)
        self.sprites_group = sprites_group
        self.bullets_group = bullets_group
        self.state = None
        self.y_acceleration = 0
        self.controllable = True

        self.mixer = pygame.mixer
        self.mixer.init()
        self.jump_sound = self.mixer.Sound('sounds/jump.mp3')
        self.attack_sound = self.mixer.Sound("sounds/attack.mp3")

        self.cd = 0
        self.max_cd = max_cd
        self.attack_sprite = None

    def jump(self, power=5):
        if self.state == RUNNING or self.y_acceleration == 0:
            self.y_acceleration = power
            self.state = JUMPING
            self.jump_sound.play()

    def update(self, tick):
        if self.state == RUNNING and self.y_acceleration > -4:
            pass
        elif self.y_acceleration < -10:
            if self.controllable:
                if self.state == JUMPING:
                    self.state = FALL_AFTER_JUMP
            else:
                self.state = FALLING
        elif self.check_collisions() and self.state != JUMPING:
            self.state = RUNNING
        if not self.check_collisions():
            if self.y_acceleration > 0:
                self.y_acceleration -= .1
            else:
                self.y_acceleration -= .2
        elif self.state != JUMPING:
            self.y_acceleration = 0
        self.sprite.rect.top -= self.y_acceleration
        platform = self.check_collisions()
        if platform and platform.rect.top < self.sprite.rect.bottom:
            if self.y_acceleration < -5:
                self.jump_sound.play()
            self.y_acceleration = 0
            self.sprite.rect.move_ip(0, platform.rect.top - self.sprite.rect.h - self.sprite.rect.top + 1)
        self.cd = max(0, self.cd - tick)
        if self.cd < self.max_cd // 2 and self.attack_sprite:
            self.attack_sprite.kill()
            self.attack_sprite = None
        elif self.attack_sprite:
            self.attack_sprite.rect.y = self.sprite.rect.y

    def shoot(self):
        if self.cd == 0:
            self.cd = self.max_cd
            self.attack_sprite = MySprite(self.bullets_group, load_image("attack.png"), self.sprite.rect.right - 20,
                                          self.sprite.rect.y)
            self.attack_sound.play()

    def check_collisions(self):
        for sprite in self.sprites_group:
            if sprite == self.sprite:
                continue
            if pygame.sprite.collide_rect(self.sprite, sprite):
                return sprite
        return False

