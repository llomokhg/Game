from random import randrange, random, choice
import npc

level = 1  # уровень сложности
countries = []


class Area:  # область
    def __init__(self, country, number, points, name, color):  # страна к которой относится, ресурсы
        self.number = number
        self.name = name
        self.points = points
        self.color = color
        self.country = country
        self.buildings = []
        self.governor = None
        self.neighbors = []
        self.damage = 0

        lev = level  # уровень сложности не влияет на ботов
        if self.country.AI:
            lev = 1

        # вероятность появления, пределы распространенности
        self.probabilities = {'gold': [0.1, 100, 1000], 'forest': [0.85, 500, 40_000], 'soil': [0.9, 10, 40],
                              'black_earth': [0.25, 40, 100], 'iron': [0.2, 500, 5000],
                              'animals': [0.9, 5_000, 15_000], 'people': [0.95, 1000, 70_000]}
        self.characteristics = {'science': round(50 / lev), 'wood': round(500 / lev), 'animals': 0,
                                'extracted_iron': round(50 / lev), 'extracted_gold': round(35 / lev),
                                'processed_iron': round(50 / lev)}
        # базовое количество добываемых ресурсов (необходимые для построек) определяется уровнем (больше уровень -
        # меньше базовых ресурсов)

        self.set_characteristic()

    def set_characteristic(self):  # рандомная генерация данных об области
        for key, el in self.probabilities.items():
            if key != 'black_earth':  # black_earth - вероятность появления чернозёма
                if random() <= el[0]:  # эта вещь будет
                    self.characteristics[key] = randrange(*el[1:])  # есть - рандомное кол-во предмета
                    if random() <= self.probabilities['black_earth'][0] and key == 'soil':
                        self.characteristics[key] = randrange(*self.probabilities['black_earth'][1:])
                else:
                    self.characteristics[key] = 0  # иначе - 0\

    def set_neighbors(self, board):
        for point in self.points:
            for neighbor_y in range(-1, 2):
                for neighbor_x in range(-1, 2):
                    neighbor_point = board.board[point[0] + neighbor_y][point[1] + neighbor_x]
                    if neighbor_point != 0 and countries[neighbor_point[0]].areas[neighbor_point[1]] != self and \
                            countries[neighbor_point[0]].areas[neighbor_point[1]] not in self.neighbors:
                        self.neighbors.append(countries[neighbor_point[0]].areas[neighbor_point[1]])

    def next_turn(self):  # обновление данных области
        for key, el in self.characteristics.items():
            if key == 'forest':
                self.characteristics[key] = round(self.characteristics[key] * 1.05)
            elif key == 'animals':
                if self.characteristics[key] > round(self.characteristics['people'] * 0.01):
                    self.characteristics[key] -= round(self.characteristics['people'] * 0.01)
                else:
                    self.characteristics[key] = randrange(1000, 3000)
                self.characteristics[key] = round(self.characteristics[key] * 1.1)
            elif key == 'people':
                self.characteristics[key] = round(self.characteristics[key] * (1.005 + self.characteristics['animals'] *
                                                                               self.characteristics['soil']
                                                                               // 300_000))
        if self.governor:
            self.governor.next_turn()
        else:
            # если нет правителя, то автоматически только ПОТРЕБЛЯЮТСЯ ресурсы для зданий
            for building in self.buildings:  # проходимся по всем зданиям
                if building.get_class() != 'University':
                    self.characteristics[building.next_turn()[0]] += building.next_turn()[2]

    # ручной сбор налогов
    def get_taxes(self):
        for building in self.buildings:  # проходимся по всем зданиям
            if building.get_class() != 'ArmyAcademy':
                # + в добытые ресурсы
                self.characteristics[building.next_turn()[1]] += abs(building.next_turn()[2])

    def build_building(self, building):  # добавить здание: класс здания
        # ограничение кол-ва зданий одного типа в одной области - 3 и кол-ва зданий - 6
        if [i.get_class() for i in self.buildings].count(building.get_class()) < 3 and len(self.buildings) < 6:
            # первые три здания одного типа в стране - бесплатно
            if [i.get_class() for x in self.country.areas for i in x.buildings].count(building.get_class()) <= 2:
                self.buildings.append(building)
            elif all([self.country.characteristics[i] >= round(k * 1.1) for i, k in building.price.items()]) and \
                    all([len([x for x in self.country.areas if x.characteristics[key] >
                                                               round(i * 1.1) // len(self.country.areas)])
                         for key, i in building.price.items()]):  # достаточно ресурсов

                for key, i in building.price.items():  # проход по необходимым ресурсам
                    if self.characteristics[key] < i:  # в области недостаточно ресурсов
                        i -= self.characteristics[key]
                        self.characteristics[key] = 0  # минус все ресурсы этого типа в областе

                        # все остальное берем из ресурсов страны (из всех областей поровну), но в большем количестве
                        for area in self.country.areas:

                            if len([x for x in self.country.areas if x.characteristics[key] > round(i * 1.1) //
                                                                     len(self.country.areas)]) != 0 \
                                    and area.characteristics[key] > round(i * 1.1) // len([x for x in self.country.areas
                                                                                           if x.characteristics[key]
                                                                                              > round(i * 1.1) //
                                                                                              len(self.country.areas)]):
                                area.characteristics[key] -= round(i * 1.1) // len([x for x in self.country.areas
                                                                                    if x.characteristics[key]
                                                                                    > round(i * 1.1) //
                                                                                    len(self.country.areas)])
                    else:
                        self.characteristics[key] -= i  # ресурсов этого типа достаточно - вычитаем цену

                self.buildings.append(building)
            else:
                return 'недостаточно ресурсов'  # сообщение об ошибке
        else:
            return 'недостаточно ресурсов'

    def del_building(self, building):
        self.buildings = self.buildings[:self.buildings.index(building)] + self.buildings[
                                                                           self.buildings.index(building) + 1:]
        for k, i in building.price.items():
            self.characteristics[k] += i // 2

    def get_characteristics(self):
        return self.characteristics

    # смена страны, в составе которой находится область
    def change_country(self, country, board):
        self.country.del_area(self, board)
        self.country = country
        country.add_area(self)
        self.number = len(country.areas) - 1
        for point in self.points:
            board.board[point[0]][point[1]] = (country.number, self.number)
        # при переходе области из состава одной страны в другую кол-во ресурсов сокращается
        for resource in list(self.characteristics.keys()):
            self.characteristics[resource] = round(self.characteristics[resource] * 0.95)


class Country:
    def __init__(self, name, number, color, bot=True):
        self.number = number
        self.color = color
        self.name = name  # название страны - строка
        self.areas = []  # список всех областей этой страны
        self.characteristics = {}  # хар-ки страны - сумма хар-к всех областей
        self.pacts = {}
        self.contracts = {}
        self.generals = []
        self.neighbors = []
        self.center = None
        self.AI = None

        if bot:
            self.AI = npc.CountryAI(self)
        else:
            self.governors = []

    def set_center(self, center):
        self.center = center

    def set_neighbors(self):
        for area in self.areas:
            for neighbor in area.neighbors:
                if neighbor.country not in self.neighbors and neighbor.country != self:
                    self.neighbors.append(neighbor.country)

    def add_area(self, area):  # добавление территории в страну
        self.areas.append(area)
        if len(self.areas) == 1:  # если до этого территорий было ноль
            # хар-ка области - хар-ка страны
            for ind in list(area.get_characteristics().keys()):
                self.characteristics[ind] = area.get_characteristics()[ind]
        else:
            for ind in list(area.characteristics.keys()):  # суммируем хар-ки области и страны
                self.characteristics[ind] += area.characteristics[ind]
            self.characteristics['soil'] //= len(self.areas)

    def del_area(self, area, board):  # удалить область из страны (захватили)
        self.areas = self.areas[:self.areas.index(area)] + self.areas[self.areas.index(area) + 1:]
        for another_area in self.areas:
            if another_area.number > area.number:
                for point in another_area.points:
                    board.board[point[0]][point[1]] = (self.number, another_area.number - 1)
        for ind, el in area.characteristics:
            self.characteristics[ind] -= area.characteristics[ind]

    def next_turn(self):  # следующий ход
        for pact in list(self.pacts.keys()):
            if self.pacts[pact]:
                self.pacts[pact] -= 1

        # если эта страна - бот, то ИИ делает ход
        if self.AI:
            self.AI.next_turn()

        # обнуление хар-к страны
        for ind in list(self.areas[0].characteristics.keys()):
            self.characteristics[ind] = 0

        # следующий ход для каждой области
        for area in self.areas:
            area.next_turn()
            for ind in list(area.characteristics.keys()):  # обновление хар-к страны
                self.characteristics[ind] += area.characteristics[ind]
        self.characteristics['soil'] //= len(self.areas)

    def get_characteristics(self):
        return self.characteristics

    # измерение силы страны влияет: население, наука, лес, залежи руды, кол-во зданий, кол-во областей
    def power_measuring(self):
        if self.characteristics['iron'] == 0:
            return (self.characteristics['people'] * self.characteristics['science'] * self.characteristics['forest']
                    * sum([1 for area in self.areas for _ in area.buildings]) *
                    len(self.areas))
        return (self.characteristics['people'] * self.characteristics['science'] * self.characteristics['forest']
                * self.characteristics['iron'] * sum([1 for area in self.areas for _ in area.buildings]) *
                len(self.areas))

    def make_pact(self, country):
        if (country not in list(self.pacts.keys()) or self.pacts[country] == 0 and (country not in
                list(self.contracts.keys()) or self.contracts[country] != 'war')):
            # разница сил небольшая
            if (self.power_measuring() < country.power_measuring() or
                    abs(country.power_measuring() - self.power_measuring()) < self.power_measuring() // 20):
                self.pacts[country] = 15
                country.pacts[self] = 15
                self.contracts[country] = 'peace'
                country.contracts[self] = 'peace'

    def make_union(self, country):
        # если союз не заключен и нет противоречий в союзах
        if (country not in list([k for k, i in self.contracts.items() if i != 'peace']) and
                self not in list([k for k, i in country.contracts.items() if i != 'peace']) and
                all([i == country.contracts[k] or i == 'peace' or country.contracts[k] == 'peace' for k, i in
                     self.contracts.items() if k in list(country.contracts.keys())])):
            self.contracts[country] = 'union'
            country.contracts[self] = 'union'
            # союзник союзника - союзник, а враг союзника - враг => добавляем союзников и противников союзникам
            for c, cond in country.contracts.items():
                if cond == 'war' and (c not in list(self.contracts.keys()) or self.contracts[c] != 'war'):
                    self.start_war(c)
            for c, cond in self.contracts.items():
                if cond == 'war' and (c not in list(country.contracts.keys()) or country.contracts[c] != 'war'):
                    country.start_war(c)

    def start_war(self, country):
        if (country not in [k for k, i in self.contracts.items() if i != 'peace'] +
                [k for k, i in self.pacts.items() if i > 0] and
                self not in [k for k, i in country.contracts.items() if i != 'peace'] +
                [k for k, i in country.pacts.items() if i > 0]):
            self.contracts[country] = 'war'
            country.contracts[self] = 'war'
            for c in [k for k, i in self.contracts.items() if i == 'union']:
                if country not in list(c.contracts.keys()) or c.contracts[country] != 'war':
                    c.start_war(country)
            for c in [k for k, i in country.contracts.items() if i == 'union']:
                if self not in list(c.contracts.keys()) or c.contracts[self] != 'war':
                    c.start_war(self)

    def make_peace(self, country):
        if self.AI:
            if self.power_measuring() * 1.2 <= country.power_measuring():
                self.contracts[country] = 'peace'  # заключение мира равнозначно подписанию пакта
                self.pacts[country] = 15

                country.contracts[self] = 'peace'
                country.pacts[self] = 15
        else:
            pass  # нужно получить ответ от игрока
