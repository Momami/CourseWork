import random
#import GenerationMaze


class Artifact:
    def __init__(self, icon, coordinates):
        self.icon = icon
        self.coordinates = coordinates

    def action(self, person):
        pass

class Life(Artifact):
    def __init__(self, icon, coordinates, count):
        super().__init__(icon, coordinates)
        self.count = count

    def action(self, person):
        person.change_life(self.count)

class Attack(Artifact):
    def __init__(self, icon, coordinates, count):
        super().__init__(icon, coordinates)
        self.count = count

    def action(self, person):
        person.change_attack(self.count)

class Thing(Artifact):
    def action(self, person):
        person.add_things('money')

class Portal(Artifact):
    def __init__(self, icon, coordinates, coordinates_to):
        super().__init__(icon, coordinates)
        self.coordinates_to = coordinates_to

    def action(self, player):
        player.change_location_for_portal(self.coordinates_to)


class ExtraLife(Artifact):
    def __init__(self, icon, coordinates):
        super().__init__(icon, coordinates)

    def action(self, person):
        person.add_things('extralife')


class Surprise(Artifact):
    def __init__(self, icon, coordinates, ht, wt):
        super().__init__(icon, coordinates)
        self.ht = ht
        self.wt = wt

    def action(self, person):
        number = random.randint(0, 11)
        ic, coord = '', (0, 0)
        if number < 4:
            life = random.randint(-person.life, 100)
            Life(ic, coord, life).action(person)
        elif number < 8:
            attack = random.randint(-person.attack, 100)
            Attack(ic, coord, attack).action(person)
        elif number < 12:
            x, y = random.randint(0, self.wt - 1), random.randint(0, self.ht - 1)
            Portal(ic, coord, (x, y)).action(person)
        else:
            person.easter_egg()

