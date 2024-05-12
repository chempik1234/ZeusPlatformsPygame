import math
import random

import pygame

from enemy import Enemy
from runner import Runner
from sprite import MySprite, load_image

WIDTH = 1200
HEIGHT = 600
FPS = 100
GAMEPLAY, DEATH, PLAY_MENU, EXIT = 1111, 2222, 3333, 4444


def render_text(text, text_coord_x, text_coord_y, font_size, color, screen):
    font = pygame.font.Font(None, font_size)
    for line_number in range(len(text)):
        line = text[line_number]
        string_rendered = font.render(line, 1, color)
        _rect = string_rendered.get_rect()
        _rect.top = text_coord_y
        _rect.x = text_coord_x
        text_coord_y += _rect.height
        screen.blit(string_rendered, _rect)


class Game:
    def __init__(self, width=WIDTH, height=HEIGHT, fps=FPS):
        self.screen_size = (width, height)
        pygame.init()
        pygame.display.set_caption('Jump')
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.display = pygame.display

        self.background_group = pygame.sprite.Group()
        self.sprites_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.score = None

        self.window = None

        self.mixer = pygame.mixer
        self.mixer.init()
        self.menu_sound = self.mixer.Sound("sounds/menu.mp3")
        self.gameplay_music = "sounds/music.mp3"

        self.track_end = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.track_end)
        pygame.mixer.music.load(self.gameplay_music)

    def run(self):
        self.window = PLAY_MENU
        running = True
        while running:
            self.sprites_group.empty()
            self.background_group.empty()
            self.enemy_group.empty()
            self.bullets_group.empty()
            if self.window == GAMEPLAY:
                self.score = 0
                self.play_level()
            elif self.window == DEATH:
                self.play_death()
            elif self.window == PLAY_MENU:
                self.play_restart()
            elif self.window == EXIT:
                running = False

    def play_level(self):
        pygame.mixer.music.load(self.gameplay_music)
        pygame.mixer.music.play()

        bg_speed, platform_speed = 1, 10
        running = True
        runner = Runner(self.screen_size[0] * 0.2, self.screen_size[1] * 0.2, self.sprites_group, self.bullets_group)

        self.generate_backgrounds()

        platforms = self.generate_platforms()
        while running:
            if platforms[-1].rect.right <= self.screen_size[0]:
                y = None
                if self.sprites_group in platforms[-1].groups():
                    y = platforms[-1].rect.top
                platforms.append(self.generate_platform(platforms[-1].rect.right - 100,
                                                        y,
                                                        self.background_group in platforms[-1].groups()))
            if platforms[0].rect.right < 0:
                platforms[0].kill()
                platforms.pop(0)
                self.score += 1
            tick = self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == self.track_end:
                    pygame.mixer.music.load(self.gameplay_music)
                    pygame.mixer.music.play()
                if event.type == pygame.QUIT:
                    self.window = EXIT
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        runner.shoot()
                    else:
                        runner.jump()
            self.screen.fill(pygame.Color("white"))
            self.background_group.draw(self.screen)
            self.sprites_group.draw(self.screen)
            self.enemy_group.draw(self.screen)
            self.bullets_group.draw(self.screen)
            for i in platforms:
                i.rect.move_ip(-platform_speed, 0)
            for i in self.enemy_group:
                i.rect.move_ip(-platform_speed, 0)
                if pygame.sprite.collide_rect(runner.sprite, i):
                    self.window = DEATH
                    running = False
                i.parent.update()
            runner.update(tick)
            render_text([str(self.score)], self.screen_size[0] // 2 - 50, self.screen_size[1] // 15,
                        72, pygame.Color("white"), self.screen)
            if runner.sprite.rect.y > self.screen_size[1] * 0.7:
                running = False
                self.window = DEATH
            pygame.display.flip()

    def generate_backgrounds(self):
        sky_image = pygame.transform.scale(load_image("sky.png"), self.screen_size)
        for i in range(math.ceil(self.screen_size[0] / sky_image.get_rect().w)):
            MySprite(self.background_group, sky_image, i * sky_image.get_rect().w, 0)

    def generate_platforms(self):
        res, length = [], 0
        while not res or res[-1].rect.right < self.screen_size[0]:
            x = 0
            y = None
            b = False
            if length > 0:
                x = res[-1].rect.right - 100
                b = self.background_group in res[-1].groups()
                if self.sprites_group in res[-1].groups():
                    y = res[-1].rect.y
            if length > 1:
                b = b or self.background_group in res[-2].groups()
            b = b or length < 10
            res.append(self.generate_platform(x, y, b, True))
            length += 1
        return res

    def generate_platform(self, x=None, y=None, platform_required=False, enemy_forbidden=False,):
        if x is None:
            x = self.screen_size[0]
        if y is None:
            y = self.screen_size[1] * (random.randint(24, 28) / 40)
        if random.random() > 0.9 and not enemy_forbidden:
            Enemy(x, y - 150, self.sprites_group, self.enemy_group, self.bullets_group, 150)
        if random.random() > 0.7 and not platform_required :
            return MySprite(self.background_group, load_image("pit.png"), x, y)
        else:
            return MySprite(self.sprites_group, load_image("platform.png"), x, y)

    def play_death(self):
        running = True
        render_text(["Проигрыш!", "ОЧКИ: " + str(self.score)],
                    self.screen_size[0] // 2 - self.screen_size[0] // 3,
                    self.screen_size[1] // 2, 72, pygame.Color("purple"), self.screen)
        render_text(["Проигрыш!", "ОЧКИ: " + str(self.score)],
                    self.screen_size[0] // 2 - self.screen_size[0] // 3,
                    self.screen_size[1] // 2 - 2, 72, pygame.Color("white"), self.screen)
        while running:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.window = EXIT
                if event.type == pygame.KEYDOWN:
                    running = False
                    self.window = PLAY_MENU
            self.display.flip()

    def play_restart(self):
        pygame.mixer.music.stop()
        self.menu_sound.play()
        image = pygame.transform.scale(load_image("loading_screen.png"), self.screen_size)
        self.screen.blit(image, (0, 0))
        render_text(["НАЧАТЬ ИГРУ", "НАЖМИТЕ ЛЮБУЮ КЛАВИШУ", "", "", "", "стреляйте во врагов на [ПРОБЕЛ]",
                     "прыгайте на любую другую кнопку"], self.screen_size[0] // 2 - 300,
                    self.screen_size[1] * 0.1, 48, pygame.Color("white"), self.screen)
        pygame.display.flip()
        running = True
        while running:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.window = EXIT
                    running = False
                if event.type == pygame.KEYDOWN:
                    self.window = GAMEPLAY
                    self.menu_sound.play()
                    running = False


if __name__ == '__main__':
    game = Game()
    game.run()
