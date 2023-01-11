import sys
import buttons
import pygame
import map
import all_else
import scene
from random import random


class App:
    def __init__(self, size, cell_size):
        self.size = size
        self.cell_size = cell_size
        self.board = None
        self.now_selected = None
        self.layer = None
        self.windows = None
        self.main_screen = None
        self.saves = []
        pygame.init()
        pygame.mixer.music.load('start_fon_music.mp3')
        pygame.mixer.music.play()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Атака ботов')
        pygame.display.set_icon(pygame.image.load('icon.ico'))

    def start_screen(self):
        earth = pygame.sprite.Sprite()
        earth.rect = pygame.Rect(0, 660, 140, 140)
        cropped = pygame.Surface((140, 140))

        all_sprites = pygame.sprite.Group()

        background = pygame.sprite.Sprite()
        background.image = pygame.image.load('main_background.png')

        background_egg = pygame.sprite.Sprite()
        background_egg.image = pygame.image.load('background_egg.png')

        background.rect = background.image.get_rect()
        background_egg.rect = background_egg.image.get_rect()

        background.rect.x, background.rect.y = 0, 0
        background_egg.rect.x, background_egg.rect.y = 0, 0

        is_egg = random() <= 0.05

        all_sprites.add(background)
        if is_egg:
            all_sprites.add(background_egg)

        start_button = buttons.Button((self.size[0] // 2 - 115, 280), (255, 70), (0, 179, 88), (35, 139, 73),
                                      (98, 217, 156), 'Comic Sans MS', 40, 'Новая игра')
        load_button = buttons.Button((self.size[0] // 2 - 145, 380), (330, 70), (0, 179, 88), (35, 139, 73),
                                     (98, 217, 156), 'Comic Sans MS', 40, 'Загрузить игру')
        egg_button = buttons.Button((854, 219), (100, 20), (0, 100, 240), (0, 155, 0),
                                    (9, 255, 243), 'Comic Sans MS', 8, 'Титанов тут нет')

        running = True
        x, y = 3, 2

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.click_checking(event.pos):
                        pygame.mixer.music.load('fon_music.mp3')
                        pygame.mixer.music.play()
                        return self.make_map()
                    elif load_button.click_checking(event.pos):
                        return self.load_screen()
                    if is_egg:
                        if egg_button.click_checking(event.pos):
                            pass
                elif event.type == pygame.MOUSEMOTION:
                    start_button.holding(event.pos)
                    load_button.holding(event.pos)
                    egg_button.holding(event.pos)

            if pygame.time.get_ticks() % 50 == 0:
                all_sprites.draw(self.screen)
                start_button.drawing(self.screen)
                load_button.drawing(self.screen)
                if is_egg:
                    egg_button.drawing(self.screen)

                earth.image = pygame.image.load("earth.jpg")
                cropped.blit(earth.image, (0, 0), (30 + 133 * x, 25 + 158 * y, 140, 140))
                earth.image = cropped
                sprites = pygame.sprite.Group()
                sprites.add(earth)
                sprites.draw(self.screen)
                x -= 1
                if x == -1:
                    x = 3
                    y -= 1
                if y == -1:
                    y = 2

            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def load_screen(self):
        self.screen.fill((0, 100, 240))
        self.screen.blit(pygame.font.SysFont('Comic Sans MS', 30).render('Нажмите ESC для выхода в главное меню',
                                                                         False, (98, 217, 156)), (210, 700))
        load_buttons = []
        text = 'Полная ячейка'
        for i in range(1, 6):
            if i > len(self.saves):
                text = 'Пустая ячейка'
            load_buttons.append(buttons.Button((self.size[0] // 2 - 145, 50 + 100 * i), (350, 70), (0, 179, 88),
                                               (35, 139, 73), (98, 217, 156), 'Comic Sans MS', 40, text + f' {i}'))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                for load_button_number in range(len(load_buttons)):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if load_buttons[load_button_number].click_checking(event.pos):
                            all_else.countries = []
                            self.board = map.Board(*self.size)
                            self.board.board = self.saves[load_button_number][1]
                            for country in self.saves[load_button_number][0]:
                                all_else.countries.append(all_else.Country(country['name'], country['number'],
                                                                           country['color']))
                                all_else.countries[country['number']].center = country['center']
                                all_else.countries[country['number']].contracts = country['AI']
                                for region in country['areas']:
                                    all_else.countries[country['number']].\
                                        add_area(all_else.Area(all_else.countries[country['number']],
                                                               region['number'], region['points'],
                                                               region['name'], region['color']))
                            return self.main_screen.main_screen()
                    elif event.type == pygame.MOUSEMOTION:
                        load_buttons[load_button_number].holding(event.pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.start_screen()

            for load_button in load_buttons:
                load_button.drawing(self.screen)

            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def escape_screen(self):
        running = True
        continue_button = buttons.Button((self.size[0] // 2 - 135, 300), (300, 70), (0, 179, 88),
                                         (35, 139, 73),
                                         (98, 217, 156), 'Comic Sans MS', 40, 'Продолжить')

        exit_button = buttons.Button((self.size[0] // 2 - 80, 400), (150, 70), (0, 179, 88),
                                     (35, 139, 73),
                                     (98, 217, 156), 'Comic Sans MS', 40, 'Выйти')
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button.click_checking(event.pos):
                        pygame.mixer.music.load('start_fon_music.mp3')
                        pygame.mixer.music.play()
                        save = self.main_screen.save()
                        self.saves.append(save)
                        return self.start_screen()
                    elif continue_button.click_checking(event.pos):
                        return self.main_screen.main_screen()
                elif event.type == pygame.MOUSEMOTION:
                    exit_button.holding(event.pos)
                    continue_button.holding(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.main_screen.main_screen()

            exit_button.drawing(self.screen)
            continue_button.drawing(self.screen)
            pygame.display.flip()

    def make_map(self):
        all_else.countries = []
        self.board = map.Board(*self.size)
        self.board.make_the_world(number_of_countries=20, number_of_regions=10)
        self.now_selected = all_else.countries[0].areas[0]
        self.layer = 'countries'
        self.windows = []
        self.main_screen = scene.Main_Scene(self)
        return self.main_screen.main_screen()
