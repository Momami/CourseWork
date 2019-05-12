import game_maze.Character as Chr
import game_maze.Artefacts as Art
import game_maze.GenerationMaze as GenMaze
import game_maze.Strategy as St
import random as rn
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

    def __init__(self, width, height, player, player_2, fl=True):
        num = rn.randint(0, 3)
        self.maze = GenMaze.Maze(width, height, num)
        self.player = player
        self.player_2 = player_2
        self.cur_pl = None
        self.next_pl = None
        self.auto = fl
        self.counter = 0
        self.elements = []
        self.character = []
        self.coord_not_free = [self.player.coordinates, self.player_2.coordinates]
        self.free_cell_up = []
        self.free_cell_upgrade()
        self.var1_level()

    def generate_character(self, count):
        ht, wd = self.maze.height, self.maze.width
        for _ in range(count):
            karma = rn.randint(-100, 100)
            # icon = 'P' if karma >= 0 else 'M'
            icon = 'P'
            attack = rn.randint(0, 30)
            coord = self.free_cell()
            life = rn.randint(0, 50)
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

    def generate_money(self, count):
        for _ in range(count):
            icon = '€'
            coord = self.free_cell()
            self.elements.append(Art.Thing(icon, coord))

    def generate_elements(self, dim):
        k = dim // 10
        count = rn.randint(0, k)
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
        if coord == self.player.coordinates:
            return self.player.icon
        if coord == self.player_2.coordinates:
            return self.player_2.icon
        for ch in self.character:
            if coord == ch.coordinates:
                return ch.icon
        for art in self.elements:
            if coord == art.coordinates:
                return art.icon
        if coord == self.point_to:
            return '۝'
        return ' '

    def var1_level(self):
        ht, wd = self.maze.height, self.maze.width
        self.generate_elements(ht * wd)
        self.point_to = self.free_cell()

    def var2_level(self, count):
        ht, wd = self.maze.height, self.maze.width
        self.point_to = self.free_cell()
        self.generate_money(count * 2 - 1)
        self.counter = count
        counter = ht * wd // 10 - count
        if counter > 0:
            cntr_artif = rn.randint(0, counter)
            self.generate_elements(cntr_artif)
            self.generate_character(counter - cntr_artif)

    def change_loc_character(self, coord1, coord2):
        self.coord_not_free.append(coord2)
        self.coord_not_free.remove(coord1)

    def interaction_with_artifact(self):
        for elem in self.elements:
            if self.cur_pl.coordinates == elem.coordinates:
                elem.action(self.cur_pl)
                self.coord_not_free.remove(elem.coordinates)
                self.elements.remove(elem)
                t = type(elem)
                if t == Art.Portal or t == Art.Surprise:
                    self.interaction_with_artifact()
                    self.interaction_with_chr()
                break
        return self.end_because_zero_life(self.cur_pl, self.next_pl)

    def check_mylife(self, pl1):
        if pl1.life <= 0:
            if pl1.artifacts.get('extralife', 0) > 0:
                pl1.artifacts['extralife'] -= 1
                pl1.change_life(100)
            else:
                return True
        return False

    def end_because_zero_life(self, pl1, pl2):
        if self.check_mylife(pl1):
            print("\nПобедил " + pl2.name)
            print(pl1)
            return True
        return False

    # Исправлено
    def war(self, elem):
        elem.ability.action(elem, self.cur_pl)
        if self.end_because_zero_life(self.cur_pl, self.next_pl):
            return True
        while True:
            self.cur_pl.hit(elem)
            if elem.life <= 0:
                break
            elem.hit(self.cur_pl)
            if self.end_because_zero_life(self.cur_pl, self.next_pl):
                return True
        return False

    def interaction_with_chr(self):
        is_end = False
        for elem in self.character:
            if self.cur_pl.coordinates == elem.coordinates:
                if self.cur_pl.karma * elem.karma >= 0:
                    elem.ability.action(elem, self.cur_pl)
                else:
                    is_end = self.war(elem)
                self.coord_not_free.remove(elem.coordinates)
                self.character.remove(elem)
        return is_end

    # ЗАХОДЯТ НА ЗАНЯТЫЕ КЛЕТКИ
    def go_character(self):
        for elem in self.character:
            coord = elem.coordinates
            elem.step(self.maze)
            self.coord_not_free.remove(coord)
            self.coord_not_free.append(elem.coordinates)

    def is_end(self, fl):
        if self.cur_pl.coordinates == self.point_to:
            if not fl or self.cur_pl.artifacts.get('money', 0) \
                    and self.cur_pl.artifacts['money'] >= self.counter:
                return True
            return False
        return False

    def interaction_players(self):
        if self.cur_pl.coordinates == self.next_pl.coordinates:
            self.next_pl.hit(self.cur_pl)
            if self.end_because_zero_life(self.cur_pl, self.next_pl):
                return True, False
            self.cur_pl.hit(self.next_pl)
            if self.end_because_zero_life(self.next_pl, self.cur_pl):
                return True, False
        return False, True

    def game(self):
        self.var2_level(4)
        self.cur_pl = self.player
        self.next_pl = self.player_2
        self.maze.print_maze(self, self.cur_pl)
        print(self.cur_pl)
        ends = self.is_end(True)
        if self.auto:
            self.manual(ends)
        else:
            self.automatic(ends)

    def automatic(self, ends):
        self.player.add_strategy(St.Strategy([], [], self.maze))
        self.player_2.add_strategy(St.Strategy([], [], self.maze))
        while not ends:
            fl = self.interaction_with_chr()
            if fl:
                break
            coord = self.cur_pl.coordinates
            self.cur_pl.coordinates = self.cur_pl.strategy.strategy(coord)
            ends, fl = self.main_check_game(coord, ends)
            if fl:
                break
        if ends:
            print('\nПобедил ' + self.cur_pl.name + '\n')

    def manual(self, ends):
        while not ends:
            fl = self.interaction_with_chr()
            if fl:
                break
            listener = kb.Listener(on_release=on_release)
            listener.start()
            listener.join()
            coord = self.cur_pl.coordinates
            self.cur_pl.new_location(self.maze, pressKey)
            ends, fl = self.main_check_game(coord, ends)
            if fl:
                break
        if ends:
            print('\nПобедил ' + self.cur_pl.name + '\n')

    def main_check_game(self, coord, ends):
        fl, ends = self.interaction_players()
        if fl:
            return ends, fl
        fl = self.interaction_with_chr()
        if fl:
            return ends, True
        self.change_loc_character(coord, self.cur_pl.coordinates)
        fl = self.interaction_with_artifact()
        if fl:
            return ends, True
        fl = self.interaction_with_chr()
        if fl:
            return ends, True
        self.go_character()
        fl = self.interaction_with_chr()
        if fl:
            return ends, True
        self.maze.print_maze(self, self.cur_pl)
        self.cur_pl, self.next_pl = self.next_pl, self.cur_pl
        print(self.cur_pl)
        return self.is_end(True), False


if __name__ == "__main__":
    player = Chr.Player('D', 'Doctor Strange', (0, 0), 0, 10, 50)
    player_2 = Chr.Player('J', 'John Snow', (9, 4), 0, 10, 50)
    game = Game(10, 5, player, player_2, False)
    game.game()
