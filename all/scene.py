import prompt
import pygame
import all_else
import sys


def draw_region(cell_size, color, need_to_paint, window):
    for point in need_to_paint:
        pygame.draw.rect(window, color,
                         (point[1] * cell_size,
                          point[0] * cell_size,
                          cell_size, cell_size))


def redraw(window, cell_size, color_flag, selected):
    window.fill((0, 100, 240))
    for country in all_else.countries:
        for area in country.areas:
            if color_flag == 'countries':
                color = country.color
            elif color_flag == 'areas':
                color = area.color
            elif color_flag == 'ground':
                color = (0, 155, 0)
            else:
                color = (255, 226, 210)
            if color_flag == 'area_select' and area == selected:
                draw_region(cell_size, (255, 73, 45), area.points, window, )
            elif color_flag == 'area_select' and area in selected.neighbors:
                draw_region(cell_size, (255, 181, 85), area.points, window)
            elif color_flag == 'country_select' and country == selected.country:
                draw_region(cell_size, (255, 73, 45), area.points, window)
            elif color_flag == 'country_select' and country in selected.country.neighbors:
                draw_region(cell_size, (255, 181, 85), area.points, window)
            elif color_flag == 'friend_select' and country == selected.country:
                draw_region(cell_size, (13, 200, 15), area.points, window)
            elif color_flag == 'friend_select' and country in selected.country.contracts.keys() and \
                    selected.country.contracts[country] == 'union':
                draw_region(cell_size, (73, 255, 45), area.points, window)
            elif color_flag == 'enemy_select' and country == selected.country:
                draw_region(cell_size, (13, 200, 15), area.points, window)
            elif color_flag == 'enemy_select' and country in selected.country.contracts.keys() and \
                    selected.country.contracts[country] == 'war':
                draw_region(cell_size, (255, 73, 45), area.points, window)
            elif color_flag == 'near_countries_select' and country == selected.country:
                draw_region(cell_size, (255, 73, 45), area.points, window)
            elif color_flag == 'near_countries_select' and country in selected.country.near_countries:
                draw_region(cell_size, (255, 181, 85), area.points, window)
            else:
                draw_region(cell_size, color, area.points, window)
    window.blit(pygame.font.SysFont('Comic Sans MS', 30).render(color_flag, False, (255, 0, 0)), (10, 750))


class Main_Scene:
    def __init__(self, app):
        self.app = app
        self.board = app.board
        self.layer = app.layer
        self.windows = app.windows
        self.cell_size = app.cell_size
        self.now_selected = app.now_selected
        self.screen = app.screen

    def save(self):
        saved = []
        for country in all_else.countries:
            country_arg = {}
            for country_key in country.__dict__.keys():
                if country_key == 'areas':
                    areas = []
                    for region in country.__dict__[country_key]:
                        area = {}
                        for region_key in region.__dict__.keys():
                            if region_key == 'country':
                                area[region_key] = region.__dict__[region_key].number
                            else:
                                area[region_key] = region.__dict__[region_key]
                        areas.append(area)
                    country_arg[country_key] = areas
                elif country_key == 'neighbors':
                    country_arg[country_key] = [neighbor.number for neighbor in country.__dict__[country_key]]
                else:
                    country_arg[country_key] = country.__dict__[country_key]
            saved.append(country_arg)
        return [saved, self.board.board]

    def main_screen(self):
        pygame.display.flip()
        bad_place = []

        try:
            for country in all_else.countries:
                for area in country.areas:
                    area.set_neighbors(self.board.board)
                country.set_neighbors()
                country.set_near_countries(self.board.board)
        except IndexError:
            pass

        running = True
        while running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    board_pos = \
                        self.board.board[self.board.get_cell(event.pos)[1]][self.board.get_cell(event.pos)[0]]
                    if self.windows:
                        for window in self.windows:
                            for y in range(window.height // self.cell_size):
                                for x in range(window.width // self.cell_size):
                                    bad_place.append([window.pos[1] // self.cell_size + y,
                                                      window.pos[0] // self.cell_size + x])
                    if [self.board.get_cell(event.pos)[1], self.board.get_cell(event.pos)[0]] not in bad_place:
                        bad_place = []
                        if event.button == 1:
                            if board_pos != 0:
                                self.now_selected = all_else.countries[board_pos[0]].areas[board_pos[1]]

                        if event.button == 3:
                            if self.layer == 'countries' or self.layer == 'country_select' or \
                                    self.layer == 'near_countries_select' or \
                                    self.layer == 'friend_select' or self.layer == 'enemy_select':
                                if board_pos != 0:
                                    huge_text = all_else.countries[board_pos[0]].name
                                    text = ''.join(str([i.name for i in
                                                        all_else.countries[board_pos[0]].areas])[1:-1]
                                                   .split('\'')).split(', ')
                                else:
                                    huge_text = 'Water'
                                    text = 'It\'s water, just water'

                            elif self.layer == 'areas' or self.layer == 'area_select':
                                if board_pos != 0:
                                    huge_text = all_else.countries[board_pos[0]].name + ' ' + \
                                                all_else.countries[board_pos[0]].areas[board_pos[1]].name
                                    text = all_else.countries[board_pos[0]].areas[board_pos[1]].buildings
                                else:
                                    huge_text = 'Water'
                                    text = 'It\'s water, just water'
                            else:
                                if board_pos != 0:
                                    huge_text = 'Ground'
                                    text = 'It\'s ground, just ground'
                                else:
                                    huge_text = 'Water'
                                    text = 'It\'s water, just water'
                            self.windows.append(prompt.Window(event.pos, (500, 300), huge_text, text, self.layer))
                    else:
                        bad_place = []

                    if event.button == 2:
                        self.windows.clear()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1 or event.key == pygame.K_1:
                        self.layer = 'countries'
                    elif event.key == pygame.K_F2 or event.key == pygame.K_2:
                        self.layer = 'areas'
                    elif event.key == pygame.K_F3 or event.key == pygame.K_3:
                        self.layer = 'country_select'
                    elif event.key == pygame.K_F4 or event.key == pygame.K_4:
                        self.layer = 'area_select'
                    elif event.key == pygame.K_F5 or event.key == pygame.K_5:
                        self.layer = 'near_countries_select'
                    elif event.key == pygame.K_F6 or event.key == pygame.K_6:
                        self.layer = 'friend_select'
                    elif event.key == pygame.K_F7 or event.key == pygame.K_7:
                        self.layer = 'enemy_select'
                    elif event.key == pygame.K_F8 or event.key == pygame.K_8:
                        self.layer = 'ground'
                    elif event.key == pygame.K_r:
                        for country in all_else.countries:
                            country.next_turn()
                    elif event.key == pygame.K_c:
                        self.windows.clear()
                    elif event.key == pygame.K_ESCAPE:
                        return self.app.escape_screen()

                grabbed = []
                for window_id in range(len(self.windows)):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if self.windows[window_id].grabbed(event.pos):
                                grabbed.append(window_id)

                if grabbed:
                    max_grab = 0
                    for grab in grabbed:
                        if grab > max_grab:
                            max_grab = grab
                    self.windows[max_grab].begin_grabbing(event.pos)
                    self.windows.insert(len(self.windows), self.windows.pop(max_grab))

                for window_id in range(len(self.windows)):
                    if event.type == pygame.MOUSEBUTTONUP:
                        self.windows[window_id].grab = False
                    if event.type == pygame.MOUSEMOTION:
                        self.windows[window_id].grabbing(event.pos)

                    if not self.windows[window_id].exist:
                        self.windows.pop(window_id)
                        break

            redraw(self.screen, self.cell_size, self.layer, self.now_selected)

            if self.windows:
                for window in self.windows:
                    window.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()
