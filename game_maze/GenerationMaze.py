import random


# Алгоритмы генерации лабиринта
# Стек, реализованный через списки
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_not_empty(self):
        return self.items != []


# Структура для хранения данных о ячейке лабиринта
# (для более понятного доступа к координатам)
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Структура для хранения данных о ячейке(содержимое и посещение)
class Vis:
    def __init__(self, num, vis):
        self.num = num
        self.vis = vis


# главный класс лабиринтов
class Maze:
    S, E = 1, 2

    def __init__(self, width, height, num_algo):
        self.width = width
        self.height = height
        self.maze = []
        self.choose_algo(num_algo)

    def __len__(self):
        return self.height

    def __getitem__(self, i):
        return self.maze[i]

    # выбор алгоритма генерации
    def choose_algo(self, num_algo):
        if num_algo == 0:
            self.maze = MazeEller(self.width, self.height).generation_maze()
        elif num_algo == 1:
            self.maze = MazeGraph(self.height, self.width).generation_maze()
        elif num_algo == 2:
            self.maze = Sidewinder(self.width, self.height).generation_maze()
        elif num_algo == 3:
            self.maze = MazeWilson(self.width, self.height).generation_maze()

    # вывод построчно
    def row_tostr(self, mas, level, player):

        for i, row in enumerate(self.maze):
            s = "|"
            u = "|"

            if i < len(self.maze) - 1:
                next_cell = self.maze[i + 1]
            else:
                next_cell = None

            for index, cell in enumerate(row):
                south = (cell & self.S != 0)  # нет снизу стены
                next_south = (index + 1 < len(row) and row[index + 1] & self.S != 0)
                east = (cell & self.E != 0)  # нет правой стены
                west = next_cell is not None and next_cell[index] & self.E != 0  # нет стены снизу
                fl = (index + 1) // len(row) == 0
                u += (" " if south else "-")

                coord = (index, i)
                if coord in level.coord_not_free:
                    s += level.icon_elements(coord)
                else:
                    s += " "

                if east:
                    s = s + " "
                    if not south:  # or not next_south:
                        if next_cell is not None and not west:
                            u += '+'
                        elif not next_south:
                            u += '-'
                        else:
                            u += ' '
                    elif not next_south:
                        if next_cell is not None and not west:
                            u += '+'
                        else:
                            u += ' '
                    else:
                        u += ' '
                else:
                    s = s + "|"
                    if (not south or not next_south) and fl:
                        u += '+'
                    else:
                        u += '|'
            mas.append(s)
            if i == self.height - 1:
                u = "+" + "-" * (self.width * 2 - 1) + '+'
            mas.append(u)

    # вывод лабиринта в консоль
    def print_maze(self, level, player):
        print("+" + "-" * (self.width * 2 - 1) + '+')
        mas = []

        self.row_tostr(mas, level, player)
        for row in mas:
            print(row)


# дополнительный класс для алгоритма Эллера
class State:
    def __init__(self, width, next_set=-1):
        self.width = width
        self.next_set = next_set
        self.sets = dict()
        self.cells = {}

    # переход к следующей строке лабиринта
    def next(self):
        return State(self.width, self.next_set)

    # создание множеств для пустых ячеек
    def populate(self):
        for cell in range(self.width):
            if not cell in self.cells:
                self.next_set += 1
                set = self.next_set
                self.sets.setdefault(set, []).append(cell)
                self.cells[cell] = set
        return self

    # слияние ячеек в одно множество
    def merge(self, sink_cell, target_cell):
        sink, target = self.cells[sink_cell], self.cells[target_cell]
        self.sets.setdefault(sink, []).extend(self.sets.setdefault(target, []))
        for cell in self.sets.get(target, []):
            self.cells[cell] = sink
        if target in self.sets:
            del (self.sets[target])

    # В одном множестве ячейки?
    def same_is(self, cell1, cell2):
        return self.cells[cell1] == self.cells[cell2]

    # добавление нового множества в общий список
    def add(self, cell, set):
        self.cells[cell] = set
        self.sets.setdefault(set, []).append(cell)


# Алгоритм Эллера
class MazeEller:
    S, E = 1, 2

    def __init__(self, width, height):
        self.height = height
        self.width = width

    # --------------------------------------------------------------------
    # Шаг алгоритма Эллера
    # --------------------------------------------------------------------

    def step(self, state, finish=False):
        connected_sets = []
        connected_set = [0]

        # ---
        # горизонтальный набор
        # ---
        for c in range(state.width - 1):
            if state.same_is(c, c + 1) or (not finish and random.randrange(0, 2) > 0):
                connected_sets.append(connected_set)
                connected_set = [c + 1]
            else:
                state.merge(c, c + 1)
                connected_set.append(c + 1)
        connected_sets.append(connected_set)
        # ---
        # вертикальный набор
        # ---
        verticals = []
        next_state = state.next()

        if not finish:
            for id, set1 in state.sets.items():
                random.shuffle(set1)
                cells_to_connect = set1[0:1 + random.randint(0, len(set1) - 1)]
                verticals += cells_to_connect
                for cell in cells_to_connect:
                    next_state.add(cell, id)

        # ---
        # строка для хранения и вывода
        # ---
        row = []
        for connected_set in connected_sets:
            for index, cell in enumerate(connected_set):
                last = (index + 1 == len(connected_set))
                map = 0 if last else self.E
                if cell in verticals:
                    map |= self.S
                row.append(map)
        next_state = next_state.populate()
        return next_state, row

    # генерация определенного кол-ва строк лабиринта
    def generation_maze(self):
        maze = []
        state = State(self.width)
        state.populate()
        row_count = 0
        while row_count < self.height - 1:
            state, row = self.step(state)
            row_count += 1
            maze.append(row)
        state, row = self.step(state, True)
        row_count += 1
        maze.append(row)
        return maze


# алгоритм генерации с помощью поиска в глубину
class MazeGraph:

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.maze = []
        self.create_begin_matrix()

    # создание начальной матрицы
    def create_begin_matrix(self):
        for i in range(self.height):
            self.maze.append([])
            for j in range(self.width):
                self.maze[i].append(Vis(0, 0))

    # основной алгоритм
    def generation_maze(self):
        check = True
        stack = Stack()
        current_cell = Cell(0, 0)
        self.maze[current_cell.y][current_cell.x].vis = 1
        while check:
            mas = self.get_neighbors(current_cell)
            if mas:
                rand_number = random.randrange(0, len(mas))
                next_cell = mas[rand_number]
                stack.push(current_cell)
                self.remove_wall(current_cell, next_cell)
                current_cell = next_cell
                self.maze[current_cell.y][current_cell.x].vis = 1
                mas.clear()
            elif stack.is_not_empty():
                current_cell = stack.pop()
            else:
                cell_unvisited = self.unvisited_cells()
                rand_number = random.randrange(0, len(cell_unvisited))
                current_cell = cell_unvisited[rand_number]
                self.maze[current_cell.y][current_cell.x].vis = 1
                cell_unvisited.clear()
            check = len(self.unvisited_cells()) != 0
        for i in range(self.height):
            for j in range(self.width):
                self.maze[i][j] = self.maze[i][j].num
        return self.maze

    # поиск непосещенных ячеек
    def unvisited_cells(self):
        mas = []
        for i in range(self.height):
            for j in range(self.width):
                if not self.maze[i][j].vis:
                    mas.append(Cell(i, j))
        return mas

    # поиск соседних вершин
    def get_neighbors(self, cell):
        dist = 1
        up = Cell(cell.x, cell.y - dist)
        right = Cell(cell.x + dist, cell.y)
        down = Cell(cell.x, cell.y + dist)
        left = Cell(cell.x - dist, cell.y)

        mas_dir = [down, right, up, left]
        mas_result = []
        for i in range(4):
            if 0 <= mas_dir[i].x < self.width and \
                    0 <= mas_dir[i].y < self.height:
                maze_curr = self.maze[mas_dir[i].y][mas_dir[i].x]
                if not maze_curr.vis:
                    mas_result.append(mas_dir[i])
        return mas_result

    # удаление стены
    def remove_wall(self, first, second):
        x_diff, y_diff = second.x - first.x, second.y - first.y

        if x_diff != 0:
            if x_diff < 0:
                self.maze[second.y][second.x].num += 2
            else:
                self.maze[first.y][first.x].num += 2
        elif y_diff != 0:
            if y_diff < 0:
                self.maze[second.y][second.x].num += 1
            else:
                self.maze[first.y][first.x].num += 1


# алгоритм SideWinder
class Sidewinder:

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.maze = []

    # создание начальной матрицы
    def create_grid(self):
        for y in range(0, self.height):
            self.maze.append([])
            for x in range(0, self.width):
                self.maze[y].append(0)

    # Генерация
    def generation_maze(self):
        self.create_grid()
        self.sidewinder()
        return self.maze

    # основной алгоритм
    def sidewinder(self):
        cx = 0
        for y in range(self.height):
            for x in range(self.width):
                if y != 0:
                    if random.randint(0, 1) == 0 and x != self.width - 1:
                        self.maze[y][x] += 2
                    else:
                        cx_tmp, x_tmp = min(cx, x), max(cx, x)
                        self.maze[y - 1][random.randint(cx_tmp, x_tmp)] += 1

                        if x != self.width - 1:
                            cx = x + 1
                        else:
                            cx = 0
                elif x != self.width - 1:
                    self.maze[y][x] += 2


# Алгоритм Уилсона
class MazeWilson:
    DIRS = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.maze = []

    # создание начальной матрицы
    def create_grid(self):
        for y in range(0, self.height):
            self.maze.append([])
            for x in range(0, self.width):
                self.maze[y].append(Vis(0, 0))

    # генерация
    def generation_maze(self):
        self.create_grid()
        self.wilson()
        for i in range(self.height):
            for j in range(self.width):
                self.maze[i][j] = self.maze[i][j].num
        return self.maze

    # поиск непосещенных вершин
    def unvisited_cells(self):
        unvisited = []
        for y, row in enumerate(self.maze):
            for x, value in enumerate(row):
                if not value.vis:
                    unvisited.append((x, y))
        return unvisited

    # основной алгоритм
    def wilson(self):
        cells_mas = self.unvisited_cells()  # Вершины, не находящиеся в дереве
        dirs_stack = []  # Стек направлений

        # Создаем дерево
        key = cells_mas[0]
        cells_mas.pop(0)
        random.shuffle(cells_mas)
        self.maze[key[1]][key[0]].vis = 1

        while cells_mas:  # Пока есть необработанные вершины, работает
            key = cells_mas[0]  # Получаем координаты клетки
            # cellsHash.remove(key)
            start_x, start_y = key[0], key[1]
            ix, iy = start_x, start_y
            dirs_stack.append(("", key))
            # dsSize += 1
            while not self.maze[iy][ix].vis:  # Ходим, пока не найдем относящуюся к дереву клетку
                direction = self.DIRS[random.randint(0, 3)]
                move = False

                # Смещение
                if direction == "UP" and iy - 1 >= 0:
                    iy -= 1
                    move = True
                elif direction == "DOWN" and iy + 1 < self.height:
                    iy += 1
                    move = True
                elif direction == "LEFT" and ix - 1 >= 0:
                    ix -= 1
                    move = True
                elif direction == "RIGHT" and ix + 1 < self.width:
                    ix += 1
                    move = True

                if move:  # Если мы можем двигаться, тогда проверяем на циклы
                    stack_reverse = [el for dir, el in dirs_stack]
                    key_to = (ix, iy)
                    if key_to in stack_reverse or key_to == (start_x, start_y):  # Удаление циклов
                        i = len(dirs_stack) - 1
                        elem = dirs_stack[i][1]
                        while elem != key_to:
                            dirs_stack.pop(i)
                            i -= 1
                            elem = dirs_stack[i][1]
                    else:
                        dirs_stack.append((direction, key_to))

            for j in range(0, len(dirs_stack)):  # Прокапывание пути
                self.maze[start_y][start_x].vis = 1
                direction = dirs_stack[j][0]

                if direction == "UP":
                    self.maze[start_y - 1][start_x].num += 1
                    start_y -= 1

                elif direction == "DOWN":
                    self.maze[start_y][start_x].num += 1
                    start_y += 1

                elif direction == "LEFT":
                    self.maze[start_y][start_x - 1].num += 2
                    start_x -= 1

                elif direction == "RIGHT":
                    self.maze[start_y][start_x].num += 2
                    start_x += 1
                try:
                    cells_mas.remove((start_x, start_y))
                except:
                    pass

            dirs_stack = []  # Обнуление стека направлений

