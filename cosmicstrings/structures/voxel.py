from cosmicstrings.structures.voxelside import VSide
import random
import numpy as np

class Voxel:
    comb = [[0, 4, 6, 2],  # z0, id    0
            [1, 5, 7, 3],  # z1        1
            [1, 5, 4, 0],  # y0        2
            [3, 7, 6, 2],  # y1        3
            [0, 2, 3, 1],  # x0        4
            [4, 6, 7, 5]]  # x1        5

    def __init__(self, pos):
        self.pos = pos
        self.sides = []

        self._verts = []
        self._string_sides = []

    @property
    def verts(self):
        pass

    @verts.setter
    def verts(self, verts):
        self._verts = verts

    @verts.getter
    def verts(self):
        return self._verts

    def calc_sides(self, sides):
        self.sides = []

        for i, id in zip(self.comb, range(6)):
            corners = [self._verts[j] for j in i]
            loc = [(corners[2].pos[i] - corners[0].pos[i]) / 2.0 + corners[0].pos[i] for i in range(3)]
            s = sides.get(str(loc))
            if s is None:
                s = VSide(corners, loc)
                sides[str(loc)] = s
            s.add_parent(self, id % 2, id)
            self.sides.append(s)

        #for i, side in zip(range(6), self.sides):
        #    print("\nid = ", i , " -- ", side)
        #    for j in side._corners:
        #        print(j)

    def draw_outline(self, ax):
        for i in self.sides:
            i.draw_sides(ax)

    def draw_connections(self, ax):
        for i in self.sides:
            if i.get_direction() is not None:
                i.draw_connection(ax)

    def find_strings(self):
        for side, i in zip(self.sides, range(6)):
            if side.get_direction() is not None:
                self._string_sides.append((i, side))

    def connect_nodes(self):
        sides = {0 : [], 1 : []}
        for i, j in self._string_sides:
            index = np.abs((i+1) % 2 - j._direction)
            if j.get_connections()[index] is not None:
                continue
            sides[index].append(j)

        random.shuffle(sides[0])
        random.shuffle(sides[1])

        newly_connected = []
        for i, j in zip(sides[0], sides[1]):
            #print("conn ", i, " with ", j)
            i.connect_side(j)
            newly_connected.append(i)
            newly_connected.append(j)
        return newly_connected

    def get_string_nodes(self):
        return [i for _, i in self._string_sides]

    def __str__(self):
        return "Voxel: pos: {} {} {}".format(*self.pos)

    def __hash__(self):
        return hash(str(self.pos))

