from random import randrange
import all_else
from generate_name import generate


class Board:
    def __init__(self, W, H, left=0, top=0, cell=2):
        self.board = [[0] * W for _ in range(H)]
        self.left = left
        self.top = top
        self.not_for_country = []
        self.cell_size = cell
        self.width = W // cell
        self.height = H // cell

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def get_cell(self, pos):
        pos = list(pos)
        pos[0], pos[1] = (pos[0] - self.left) // self.cell_size, (pos[1] - self.top) // self.cell_size
        if pos[0] not in range(self.width) or pos[1] not in range(self.height):
            return None
        return tuple(pos)

    def make_region(self, pos, local_region_number, country_number, max_region_size):
        to_draw = [list(pos)]
        need_to_paint = []
        for region_size in range(max_region_size):

            try:
                for neighbor_y in range(-1, 2):
                    for neighbor_x in range(-1, 2):

                        if randrange(0, 100, 1) >= 70 or region_size <= max_region_size // 10:
                            if self.board[to_draw[0][1] + neighbor_y][to_draw[0][0] + neighbor_x] == 0:
                                to_draw.append([to_draw[0][0] + neighbor_x, to_draw[0][1] + neighbor_y])
                                self.board[to_draw[0][1] + neighbor_y][to_draw[0][0] + neighbor_x] = \
                                    (country_number, local_region_number)
                                need_to_paint.append([to_draw[0][1] + neighbor_y, to_draw[0][0] + neighbor_x])
                del to_draw[0]
            except IndexError:
                pass
        if len(need_to_paint) >= 200:
            all_else.countries[country_number].add_area(
                all_else.Area(all_else.countries[country_number], local_region_number, need_to_paint,
                              generate(),
                              (randrange(100, 155),
                               randrange(100, 155),
                               randrange(100, 155))))

            local_region_number += 1
        else:
            for bad_region in need_to_paint:
                self.board[bad_region[0]][bad_region[1]] = 0
        return local_region_number

    def make_country(self, number_of_regions, country_number):
        local_region_number = 0
        while True:
            dot_x, dot_y = randrange(50, self.width - 50), randrange(50, self.height - 50)
            count = 0
            if (dot_x, dot_y) not in self.not_for_country:
                for i in range(-40, 40):
                    for j in range(-40, 40):
                        if self.board[dot_y + i][dot_x + j] != 0:
                            count += 1
                if count / 6400 <= 0.26:
                    for i in range(-20, 20):
                        for j in range(-20, 20):
                            self.not_for_country.append((dot_x + j, dot_y + i))
                    break
        while local_region_number <= number_of_regions:
            local_region_number = self.make_region((dot_x + randrange(-30, 30),
                                                    dot_y + randrange(-30, 30)), local_region_number, country_number,
                                                   300 + randrange(-30, 30))
        return dot_y, dot_x

    def make_the_world(self, number_of_regions=7, number_of_countries=7):
        for country_number in range(number_of_countries):
            all_else.countries.append(all_else.Country(generate(), country_number,
                                                       (randrange(100, 255), randrange(100, 255), randrange(100, 255))))
            center = self.make_country(number_of_regions + randrange(-3, 2), country_number)
            all_else.countries[country_number].set_center(center)
