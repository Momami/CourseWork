import game_maze.Character as Chr
import game_maze.Artefacts as Art
import game_maze.GenerationMaze as GenMaze
import game_maze.Levels as Level
import random as rn
import os
import sys
from pynput import keyboard as kb

keys = [kb.Key.down, kb.Key.right, kb.Key.left, kb.Key.up]
pressKey = None

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    # print('{0} released'.format(key))
    if key in keys:
        global pressKey
        pressKey = key
        # Stop listener
        return False
    else:
        print('Используйте клавиши стрелок, чтобы управлять персонажем\n')


class Game:

    def __init__(self, width, height, player):
        num = rn.randint(0, 3)
        self.maze = GenMaze.Maze(width, height, num)
        self.player = player
        self.elements = []
        self.character = []
        self.coord_not_free = [self.player.coordinates]
        self.free_cell_up = []
        self.free_cell_upgrade()
        self.var1_level()

    def generate_character(self, count):
        ht, wd = self.maze.height, self.maze.width
        for _ in range(count):
            karma = rn.randint(-100, 100)
            icon = 'P' if karma >= 0 else 'M'
            attack = rn.randint(0, 100)
            coord = self.free_cell()
            life = rn.randint(0, 100)
            ability = Chr.Ability(karma)
            self.character.append(Chr.Character(icon, coord, karma, attack, life, ability))

    def generate_artifact(self, count):
        ht, wd = self.maze.height, self.maze.width
        for _ in range(count):
            num = rn.randint(0, 5)
            el = None
            if num == 0:
                icon = '♥'
                coord = self.free_cell()
                el = Art.ExtraLife(icon, coord)
            elif num == 1:
                icon = '€'
                coord = self.free_cell()
                el = Art.Thing(icon, coord)
            elif num == 2:
                icon = '֍'
                coord = self.free_for_strange()
                el = Art.Portal(icon, coord, self.free_cell())
            elif num == 3:
                icon = '♡'
                coord = self.free_cell()
                el = Art.Life(icon, coord, rn.randint(0, 55))
            elif num == 4:
                icon = 'ջ'
                coord = self.free_cell()
                el = Art.Attack(icon, coord, rn.randint(0, 50))
            else:
                icon = '¿'
                coord = self.free_for_strange()
                el = Art.Surprise(icon, coord, ht, wd)
            self.elements.append(el)
    # ¥ ҁ

    def generate_elements(self, dim):
        k = dim // 10
        count = rn.randint(1, k)
        counter = k - count
        self.generate_artifact(count)
        self.generate_character(counter)

    def free_cell_upgrade(self):
        ht, wd = self.maze.height, self.maze.width
        if self.maze[0][0] == 1 or self.maze[0][0] == 2:
            self.free_cell_up.append((0, 0))
        # дописать нормально проверку
        for i in range(1, ht):
            for j in range(1, wd):
                up = self.maze[i - 1][j] == 0 or self.maze[i - 1][j] == 2
                left = self.maze[i][j - 1] == 0 or self.maze[i][j - 1] == 1
                this = self.maze[i][j]
                if this == 0 and (up or left) or this != 3 and up and left:
                    self.free_cell_up.append((j, i))
        for i in range(1, ht):
            up = self.maze[i - 1][0] == 0 or self.maze[i - 1][0] == 2
            this = self.maze[i][0]
            if this != 3 and up or this == 0:
                self.free_cell_up.append((0, i))
        for j in range(1, wd):
            left = self.maze[0][j - 1] == 0 or self.maze[0][j - 1] == 1
            this = self.maze[0][j]
            if this == 0 or this != 3 and left:
                self.free_cell_up.append((j, 0))

    def in_free_up(self, coord):
        if self.free_cell_up == [] or coord in self.free_cell_up:
            return True
        return False

    def free_for_strange(self):
        ht, wd = self.maze.height - 1, self.maze.width - 1
        coord = (rn.randint(0, wd), rn.randint(0, ht))
        while not self.free(coord) or not self.in_free_up(coord):
            coord = (rn.randint(0, wd), rn.randint(0, ht))
        self.coord_not_free.append(coord)
        self.free_cell_up.remove(coord)
        return coord

    def free_cell(self):
        ht, wd = self.maze.height - 1, self.maze.width - 1
        coord = (rn.randint(0, wd), rn.randint(0, ht))
        while not self.free(coord):
            coord = (rn.randint(0, wd), rn.randint(0, ht))
        self.coord_not_free.append(coord)
        return coord

    def free(self, coord):
        if coord in self.coord_not_free:
            return False
        return True

    # НАЙТИ ПОДХОДЯЩИЕ ИКОНКИ
    def icon_elements(self, coord):
        for ch in self.character:
            if coord == ch.coordinates:
                return ch.icon
        for art in self.elements:
            if coord == art.coordinates:
                return art.icon
        if coord == self.player.coordinates:
            return '۝'
        if coord == self.point_to:
            return '0'
        return ' '

    def var1_level(self):
        ht, wd = self.maze.height, self.maze.width
        self.generate_elements(ht * wd)
        # self.point_in = self.free_cell()
        self.point_to = self.free_cell()

    def var2_level(self, count):
        ht, wd = self.maze.height, self.maze.width
        self.point_in = self.point_to = self.free_cell()
        self.generate_artifact(count)
        self.counter = ht * wd // 10 - count
        self.generate_character(self.counter)

    def change_loc_character(self, coord1, coord2):
        self.coord_not_free.append(coord2)
        self.coord_not_free.remove(coord1)

    def interaction_with_artifact(self):
        for elem in self.elements:
            if self.player.coordinates == elem.coordinates:
                elem.action(self.player)
                self.coord_not_free.remove(elem.coordinates)
                self.elements.remove(elem)
                break

    def check_mylife(self):
        if self.player.life <= 0:
            if self.player.artifacts.get('extralife', 0) > 0:
                self.player.artifacts['extralife'] -= 1
                self.player.change_life(100)
            else:
                return True
        return False

    # Исправлено
    def war(self, elem):
        elem.ability.action(elem, self.player)
        if self.check_mylife():
            return True
        while True:
            self.player.hit(elem)
            if elem.life <= 0:
                break
            elem.hit(self.player)
            if self.check_mylife():
                return True
        return False

    def interaction_with_chr(self):
        is_end = False
        for elem in self.character:
            if self.player.coordinates == elem.coordinates:
                if self.player.karma * elem.karma >= 0:
                    elem.ability.action(elem, self.player)
                else:
                    is_end = self.war(elem)
                self.coord_not_free.remove(elem.coordinates)
                self.character.remove(elem)
                break
        return is_end

    # ЗАХОДЯТ НА ЗАНЯТЫЕ КЛЕТКИ
    def go_character(self):
        for elem in self.character:
            coord = elem.coordinates
            elem.step(self.maze)
            self.coord_not_free.remove(coord)
            self.coord_not_free.append(elem.coordinates)

    def is_end(self, fl):
        if self.player.coordinates == self.point_to:
            if fl and self.player.artifacts['money'] >= self.counter or not fl:
                return True
            return False
        return False

    def game(self):
        self.var1_level()
        self.maze.print_maze(self, self.player)
        print(self.player)
        ends = self.is_end(False)
        while not ends:
            listener = kb.Listener(on_release=on_release)
            listener.start()
            listener.join()
            coord = self.player.coordinates
            self.player.new_location(self.maze, pressKey)
            self.change_loc_character(coord, self.player.coordinates)
            self.interaction_with_artifact()
            fl = self.interaction_with_chr()
            if fl:
                print("\nПоражение!\n")
                print(self.player)
                break
            self.go_character()
            fl = self.interaction_with_chr()
            if fl:
                print("\nПоражение!\n")
                print(self.player)
                break
            #clear()
           # os.system('clear')
            self.maze.print_maze(self, self.player)
            print(self.player)
            ends = self.is_end(False)
        if ends:
            print('\nВЫ ПОБЕДИЛИ!\n')


def clear():
    sys.stdout.write('\033[1J')
    sys.stdout.write('\033[;H')

if __name__ == "__main__":
    maps = {1: 3, 2: 4}
    print(maps.popitem(), maps)
    player = Chr.Player('', (0, 0), 0, 10, 50)
    game = Game(10, 5, player)
    game.game()
    player = Chr.Player('%', (0, 0), 0, 10, 50)
