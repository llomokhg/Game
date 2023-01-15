from random import random, choice, randrange
import areas
import buildings


class CountryAI:
    def __init__(self, country):
        self.country = country
        self.data = {'pact': 0.25, 'union': 0.15, 'war': 0.3}
        self.attack_generals = []
        self.defence_generals = []

    def next_turn(self):
        max_force = 0  # стране с макс силой бот предлагает вступить в союз/заключить пакт с определённой вероятностью
        country_action = None
        for country in areas.countries[:areas.countries.index(self.country)] + \
                       areas.countries[areas.countries.index(self.country) + 1:]:
            if max_force < country.power_measuring() and country not in list(self.country.pacts.keys()):
                max_force = max(country.power_measuring(), max_force)
                country_action = country

        if country_action:
            if random() <= self.data['pact']:
                country_action.make_pact(self.country)
            if random() <= self.data['union']:
                country_action.make_union(self.country)

        min_force = None
        country_action = None

        for country in self.country.neighbors:
            if ((not min_force or min_force > country.power_measuring()) and country not in
                    list(self.country.pacts.keys()) and country not in list(self.country.contracts.keys())):
                min_force = country.power_measuring()
                country_action = country

        if country_action and country_action.power_measuring() <= self.country.power_measuring() // 1.3 and \
                len(self.country.generals) > 6 and random() < self.data['war']:
            self.country.start_war(country_action)

        for country, cond in self.country.contracts.items():
            if cond == 'union':
                for enemy in [c for c, i in self.country.contracts.items() if i == 'war']:
                    country.start_war(enemy)

        # во всех областях будут управлять правители
        for area in self.country.areas:
            if not area.governor:
                area.governor = Governor(area)

        if 'war' in list(self.country.contracts.values()):
            self.war()
            for country in [k for k, i in self.country.contracts.items() if i == 'war']:
                if (self.country.power_measuring() * 2 <= country.power_measuring() or
                        sum([k.power_measuring() for k, i in self.country.contracts.items() if i == 'war']) >
                        self.country.power_measuring() and random() < self.data['pact']):
                    self.country.make_peace(country)

    def war(self):
        countries_war = [k for k, i in self.country.contracts.items() if i == 'war']
        # странами-врагами (countries_war)

        areas_war = []
        for c_areas in [c.areas for c in countries_war]:
            for area in c_areas:
                if any([a in self.country.areas for a in area.neighbors]):
                    areas_war.append(area)

        for area in areas_war:
            soldiers = min([area.characteristics['people'], round(area.characteristics['animals'] // areas.level * 1.5),
                            area.characteristics['extracted_iron'] // 0.05,
                            area.characteristics['wood'] // 0.7]) // 5  # макс кол-во солдат, которые можно нанять
            # в этой области деленные на 5 (чтобы не тратить все ресурсы)
            generals = [i for i in area.country.generals if i.area == area]  # генералы в этой области

            # кол-во генералов должно быть 2 в этой области
            if len(generals) < 2:
                for _ in range(2 - len(generals)):

                    area_neighbours = [a for a in area.neighbors if a.country == area.country and a not in areas_war]
                    # генералы на соседней этой области не на границе

                    # если в соседних областях нет генералов, то берем случайного из тыла
                    if not [i for i in area.country.generals if i.area in area_neighbours] and \
                            [i for i in area.country.generals if i.area not in areas_war]:
                        # случайный генерал, который не находится на границе с врагом
                        general = choice([i for i in area.country.generals if i.area not in areas_war])

                        # без солдат генерал может премещаться на любое расстояние по стране, а с ним он может
                        # перемещаться только в соседнюю область
                        general.update_army(-general.soldiers)
                        general.change_area(area)  # переезжает в нужную область
                        general.update_army(soldiers)  # найм солдат уже в ней
                        generals.append(general)  # добавляем генерала
                    else:
                        # случайный генерал из соседней области переходит в эту
                        if [i for i in area.country.generals if i.area in area_neighbours]:
                            general = choice([i for i in area.country.generals if i.area in area_neighbours])
                            general.change_area(area)
                            # если у него недостаточно солдат, то нанимает новых
                            if general.soldiers < 1000:
                                general.update_army(soldiers)
            else:
                # проходим по всем генералам в этой области и, если надо, нанимаем солдат
                for general in generals:
                    if general.soldiers < 1000:
                        general.update_army(soldiers)
            if generals:
                # атакующий генерал
                attack_general = max(generals, key=lambda g: g.characteristics['attack'])
                if [a for a in attack_general.area.neighbors if a.country in countries_war]:
                    attack_area = [a for a in area.neighbors if a.country in countries_war][0]
                    attack_general.change_area(attack_area)
                    attack_general.attack()
                # защищающийся генерал
                max(generals, key=lambda g: g.characteristics['defence']).defence()


class Governor:
    def __init__(self, area):
        lev = not area.country.AI  # на бота не влияет уровень сложности
        self.characteristics = {
            'loyalty': randrange(85 - (areas.level - 1) * lev * 10, 95 - (areas.level - 1) * 10 * lev),
            'intellect': randrange(75 - (areas.level - 1) * 10 * lev, 90 - (areas.level - 1) * 10 * lev),
            'honesty': randrange(85 - (areas.level - 1) * 10 * lev, 100 - (areas.level - 1) * lev * 10)}
        self.area = area

    def next_turn(self):
        if self.area:
            # условие строительства здания
            for building in [buildings.University, buildings.GoldMine, buildings.IronMine,
                             buildings.Sawmill, buildings.MetallurgicalPlant, buildings.ArmyAcademy]:
                if ((building(self.area).get_class() not in [i.get_class() for i in self.area.buildings] or
                     [a.buildings for a in self.area.country.areas].count(building(self.area).get_class()) < 3 or
                     all([self.area.country.characteristics[i] >= k for i, k in building.price.items()])) and
                        random() * 100 <= self.characteristics['intellect'] and
                        self.area.characteristics[[i for i in list(building.data.keys())
                                                   if i != 'years' and i != 'level'][0]]
                        >= building.data[[i for i in list(building.data.keys()) if i != 'year' and i != 'level'][0]]):
                    if building == buildings.ArmyAcademy:
                        if len(self.area.country.generals) < len(self.area.country.areas) // 2:
                            self.area.build_building(building(self.area))
                    else:
                        self.area.build_building(building(self.area))

            for building in self.area.buildings:  # проходимся по всем зданиям
                if building.get_class() != 'University':
                    # то, сколько минусуется ресурсов не зависит от честности правителя
                    self.area.characteristics[building.next_turn()[0]] += building.next_turn()[2]
                if building.get_class() != 'ArmyAcademy':
                    # + в добытые ресурсы, НО не все, тк это зависит от честности правителя
                    self.area.characteristics[building.next_turn()[1]] += round(abs(building.next_turn()[2]) *
                                                                                self.characteristics['honesty'] * 0.01)

            # если идет война, то с определённой вероятностью правитель предаёт страну + к вероятности - наличие границы
            # с вражеским государством
            if ('war' in list(self.area.country.contracts.values()) and random() > self.characteristics['loyalty'] +
                    sum([a.country in [i for k, i in self.area.country.contracts.items() if i == 'war'] for a in
                         self.area.neighbors]) * 0.1):
                self.area.change_country(choice([k for k, i in list(self.area.country.contracts) if i == 'war']))

    # поменять область, которой руководит правитель
    def change_area(self, area):
        self.area = area


class General:
    def __init__(self, area):
        lev = not area.country.AI
        self.characteristics = {
            'attack': 1 + randrange(20 - (areas.level - 1) * 10 * lev, 100 - (areas.level - 1) * 10 * lev) // 100,
            'defence': 1 + randrange(20 - (areas.level - 1) * 10 * lev, 100 - (areas.level - 1) * 10 * lev) // 100,
            'level': 1 + randrange(20 - (areas.level - 1) * 10 * lev, 100 - (areas.level - 1) * 10 * lev) // 100}
        self.soldiers = 0  # количество солдат армии генерала
        self.area = area
        self.country = area.country

    # обновить армию (количество солдат)
    def update_army(self, soldiers):
        if soldiers > 0:
            lev = areas.level
            if self.area.country.AI:
                lev = 1
            if (self.area.characteristics['animals'] >= soldiers * areas.level and self.area.characteristics[
                'extracted_iron']
                    > soldiers * 0.1 and self.area.characteristics['wood'] > soldiers * 0.9 and
                    self.area.characteristics['people'] > soldiers):
                self.area.characteristics['animals'] -= round(soldiers * lev // 1.5)
                self.area.characteristics['extracted_iron'] -= round(soldiers * 0.05)
                self.area.characteristics['wood'] -= round(soldiers * 0.7)
                self.area.characteristics['people'] -= soldiers
                self.soldiers += soldiers
            else:
                return 'недостаточно ресурсов'
        else:
            if self.soldiers >= abs(soldiers):
                self.area.characteristics['people'] += abs(soldiers)
                self.soldiers += soldiers
            else:
                return 'нет столько солдат'

    # усилить армию (поднять уровень)
    def powering_army(self, force):
        self.characteristics['level'] = force

    # атака, возвращает атаку (солдаты * общий коэффицент силы * коэффицент атаки)
    def attack(self):
        self.area.damage += self.characteristics['attack'] * self.soldiers * self.characteristics['level']

    # оборона, возвращает защиту (солдаты * общий коэффицент силы * коэффицент обороны)
    def defence(self):
        self.area.damage -= self.characteristics['defence'] * self.soldiers * self.characteristics['level']

    def change_area(self, area):
        if self.soldiers == 0 or True:  # если нет солдат или self.area соседняя с area
            self.area = area
