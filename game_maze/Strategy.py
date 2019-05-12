import random


class Strategy:
    def __init__(self, art, characters, maze):
        self.artifacts = art
        self.characters = characters
        self.maze = maze

    def step(self, coord):
        # num = 0
        # while num < 5:
        x, y = coord
        where_to_go = random.randint(0, 3)
        if where_to_go == 0:
            x -= 1
        elif where_to_go == 1:
            y -= 1
        elif where_to_go == 2:
            x += 1
        else:
            y += 1
        coord = self.change_location(coord, (x, y))
        return coord

    def change_location(self, coord, coord_to):
        x_in, y_in = coord[0], coord[1]
        x, y = coord_to[0], coord_to[1]
        x_min, y_min = min(x, x_in), min(y, y_in)
        height, width = len(self.maze), len(self.maze[0])
        if 0 <= x < width and 0 <= y < height:
            if x_in != x and (self.maze[y][x_min] == 0 or self.maze[y][x_min] == 1) \
                    or y_in != y and (self.maze[y_min][x] == 0 or self.maze[y_min][x] == 2):
                return coord
        else:
            return coord
        return coord_to

    def strategy(self, coord):
        return self.step(coord)


class MyStrategy(Strategy):
    def strategy(self, coord): pass
