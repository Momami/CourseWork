from pynput.keyboard import *
import random


# Способность персонажа
class Ability:
    ability = ''

    def __init__(self, karma):
        self.coeff = abs(karma // 3) * \
                     (0 if karma == 0 else karma // abs(karma))
        self.is_ability(karma)

    # Выбор способности
    def is_ability(self, karma):
        coefficient = karma / 100
        if abs(coefficient) > 0.5:
            self.ability = 'life'
        elif abs(coefficient) > 0:
            self.ability = 'artifact'

    # Действие
    def action(self, player_in, player_to):
        if self.ability == 'life':
            self.life_change(player_in, player_to)
        elif self.ability == 'artifact':
            self.artifact_change(player_to)

    def life_change(self, player_in, player_to):
        if player_to.karma * self.coeff >= 0:
            player_to.change_life(abs(self.coeff))
        else:
            player_to.change_life(-player_in.attack)
        player_to.change_karma(self.coeff)

    def artifact_change(self, player):
        if player.karma * self.coeff >= 0:
            rand = random.randint(0, 1)
            if rand:
                player.add_things('money')
            else:
                player.add_things('extralife')
        else:
            if player.count_art():
                player.remove_things()
        player.change_karma(self.coeff)


# Персонаж
class Character:
    def __init__(self, icon, coordinates, karma, attack, life, ability):
        self.icon = icon
        self.coordinates = coordinates
        self.karma = karma
        self.attack = attack
        self.life = life
        self.ability = ability

    # Удар
    def hit(self, player):
        player.change_life(-self.attack)

    # Изменение кармы
    def change_karma(self, count):
        self.karma += count
        if self.karma > 100:
            self.karma = 100
        elif self.karma < -100:
            self.karma = -100

    # Изменение жизни
    def change_life(self, count):
        self.life += count
        if self.life > 100:
            self.life = 100
        elif self.life < 0:
            self.life = 0

    # Ход в случайную клетку
    def step(self, maze):
        num = 0
        while num < 5:
            x, y = self.coordinates
            where_to_go = random.randint(0, 3)
            if where_to_go == 0:
                x -= 1
            elif where_to_go == 1:
                y -= 1
            elif where_to_go == 2:
                x += 1
            else:
                y += 1
            self.change_location((x, y), maze)
            if self.coordinates == (x, y):
                break
            num += 1

    def change_location(self, coord_to, maze):
        x_in, y_in = self.coordinates[0], self.coordinates[1]
        x, y = coord_to[0], coord_to[1]
        x_min, y_min = min(x, x_in), min(y, y_in)
        height, width = len(maze), len(maze[0])
        if 0 <= x < width and 0 <= y < height:
            if x_in != x and (maze[y][x_min] == 0 or maze[y][x_min] == 1)\
                    or y_in != y and (maze[y_min][x] == 0 or maze[y_min][x] == 2):
                return
        else:
            return
        self.coordinates = coord_to


# Игрок
class Player(Character):
    def __init__(self, icon, name, coordinates, karma, attack, life, strat=None):
        Character.__init__(self, icon, coordinates, karma, attack, life, '')
        self.artifacts = dict()
        self.ability = 'life'
        self.name = name
        self.strat = strat

    def add_strategy(self, strat):
        self.strategy = strat

    def __str__(self):
        s = 'Игрок: {3}\nКарма: {0}\nЖизнь: {1}\nАтака: {2}\nАртефакты: '\
            .format(self.karma, self.life, self.attack, self.name)
        for key, val in self.artifacts.items():
            s += key + ' - ' + str(val) + '; '
        return s

    # методы для артефактов
    def count_art(self):
        return len(self.artifacts)

    def remove_things(self):
        key, value = self.artifacts.popitem()
        value -= 1
        self.artifacts[key] = value

    # изменение атаки
    def change_attack(self, attack):
        self.attack += attack
        if self.attack > 100:
            self.attack = 100

    # добавление артефакты
    def add_things(self, thing):
        self.artifacts[thing] = self.artifacts.get(thing, 0) + 1

    # смена координат
    def change_location_for_portal(self, coord):
        self.coordinates = coord

    # новая позиция по кнопке
    def new_location(self, maze, key):
        x, y = self.coordinates[0], self.coordinates[1]
        if key == Key.left:
            x -= 1
        elif key == Key.up:
            y -= 1
        elif key == Key.right:
            x += 1
        elif key == Key.down:
            y += 1
        self.change_location((x, y), maze)
