import game_maze.Artefacts
from pynput.keyboard import *
import random


class Ability:
    ability = ''

    def __init__(self, karma):
        self.coeff = abs(karma // 3) * (0 if karma == 0 else karma // abs(karma))
        self.is_ability(karma)

    def is_ability(self, karma):
        coefficient = karma / 100
        if abs(coefficient) > 0.5:
            self.ability = 'life'
        elif abs(coefficient) > 0:
            self.ability = 'artifact'

    def action(self, player_in, player_to):
        if self.ability == 'life':
            self.life_change(player_in, player_to)
        elif self.ability == 'artifact':
            self.artifact_change(player_to)

    def life_change(self, player_in, player_to):
        player_to.change_karma(self.coeff)
        # num = abs(player_in.karma) // 3
        if player_to.karma * self.coeff >= 0:
            player_to.change_life(abs(self.coeff))
        else:
            player_to.change_life(-player_in.attack)

    def artifact_change(self, player):
        player.change_karma(self.coeff)
        if player.karma * self.coeff >= 0:
            rand = random.randint(0, 1)
            if rand:
                thing = game_maze.Artefacts.Thing('', (0, 0))
            else:
                thing = game_maze.Artefacts.ExtraLife('', (0, 0))
            player.add_things(thing)
        else:
            if player.count_art():
                rand = random.randint(0, player.count_art())
                player.remove_things(rand, 1)


class Character:
    def __init__(self, icon, coordinates, karma, attack, life, ability):
        self.icon = icon
        self.coordinates = coordinates
        self.karma = karma
        self.attack = attack
        self.life = life
        self.ability = ability

    def hit(self, player):
        player.change_life(self.attack)

    def change_karma(self, count):
        self.karma += count
        if self.karma > 100:
            self.karma = 100
        elif self.karma < -100:
            self.karma = -100

    def change_life(self, count):
        self.life += count
        if self.life > 100:
            self.life = 100
        elif self.life < 0:
            self.life = 0

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

    # def kill(self): pass


class Player(Character):
    def __init__(self, icon, coordinates, karma, attack, life):
        Character.__init__(self, icon, coordinates, karma, attack, life, '')
        self.artifacts = dict()
        self.ability = 'life'

    def __str__(self):
        s = 'Карма: {0}\nЖизнь: {1}\nАтака: {2}\nАртефакты: '\
            .format(self.karma, self.life, self.attack)
        for key, val in self.artifacts.items():
            s += key + ' - ' + str(val) + '; '
        return s
    def count_art(self):
        return len(self.artifacts)

    def remove_things(self, num):
        cnt = 0 if self.artifacts[num] == 0 else self.artifacts[num] - 1
        self.artifacts[num] = cnt

    def change_attack(self, attack):
        self.attack += attack
        if self.attack > 100:
            self.attack = 100

    def add_things(self, thing):
        self.artifacts[thing] = self.artifacts.get(thing, 0) + 1

    def change_location_for_portal(self, coord):
        self.coordinates = coord



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
