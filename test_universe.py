from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np
import random
from typing import List
import itertools


SIZE = (2, 2, 2)
random.seed(11)

class vertex:

    def __init__(self, pos):
        self.pos = pos
        self.theta = random.choice([0, 2.0/3.0 * np.pi, 4.0/3.0 * np.pi])

    def __str__(self):
        return "Vertex {} -> position {}; {}; {} -> theta {}".format(hex(id(self)), *self.pos, self.theta)

    def __eq__(self, othr):
        if self.pos == othr.pos:
            return True
        else:
            return False

class side:

    def __init__(self, corners, id, loc):
        self._s_direction = 0
        self._corners = corners
        self._has_string = False
        self._id = id
        self._string_connection = None
        self._parents = [None, None]

        self._loc = loc

    def find_strings(self):
        prev = self._corners[0].theta
        tot = 0
        for i in [*self._corners, self._corners[0]]:
            t = i.theta
            diff = t - prev
            diff = (diff + np.pi) % ( 2 * np.pi ) - np.pi
            #print("t = ", t, "\t\tdiff = ", diff)
            if diff > np.pi:
                tot -= (diff - np.pi)
            else:
                tot += diff
            prev = t
        #print("tot = ", tot)
        #print("done")
        if tot > 2 * np.pi - 0.0001:
            # print("STRING ACW")
            self._has_string = True
        elif tot < - 2 * np.pi + 0.0001:
            # print("STRING CW")
            self._has_string = True
            self._s_direction = 1

    def advance(self):
        return self._parents[self._s_direction]

    def draw_sides(self, ax):
        x = []
        y = []
        z = []
        for i in [*self._corners, self._corners[0]]:
            _x, _y, _z = i.pos
            x.append(_x)
            y.append(_y)
            z.append(_z)
        ax.add_collection3d(Line3DCollection([list(zip(x, y, z))], colors='k', alpha=0.1, linewidths=1, linestyles='--'))

    def draw_face(self, ax):
        x = []
        y = []
        z = []
        for i in [*self._corners, self._corners[0]]:
            _x, _y, _z = i.pos
            x.append(_x)
            y.append(_y)
            z.append(_z)
        ax.add_collection3d(Poly3DCollection([list(zip(x, y, z))], color='r', alpha=0.1))

    def is_middle(self):
        s = self._string_connection
        if s is None:
            return False
        elif self is s._map[0] or self is s._map[1]:
            return False
        else:
            return True


    def draw_string(self, ax):
        if self._has_string:
            # print("DRAWING STRING")
            if self._s_direction == 1:
                marker = 'x'
            else:
                marker = 'o'
            ax.scatter(*self._loc, marker=marker)

    def __eq__(self, othr):
        if self._loc == othr._loc:
            return True
        else:
            return False

    def __hash__(self):
        return hash(id(self))

    def add_parent(self, parent, pos):
        if self._parents[pos] is not None:
            raise("DOUBLE ASSIGN PARENTS")
        self._parents[pos] = parent

class voxel:

    def __init__(self, pos: List[float]):
        self.pos = pos
        self._has_strings = False
        self._strings = []
        self._sides = []
        self.__verts = []

    def __str__(self):
        return "Voxel at position {}; {}; {}.".format(*self.pos)

    def find_strings(self):
        for side in self._sides:
            side.find_strings()
            if side._has_string:
                self._strings.append(side)
        if len(self._strings) > 0:
            self._has_strings = True

    def draw_sides(self, ax):
        for i in self._sides:
            i.draw_sides(ax)

    def draw_strings(self, ax):
        for i in self._sides:
            i.draw_string(ax)

    @property
    def _verts(self):
        pass

    @_verts.setter
    def _verts(self, verts):
        self.__verts = verts

    @_verts.getter
    def _verts(self):
        return self.__verts

    def get_all_verts(self):
        return self._verts

    def calc_sides(self, sides):
        comb = [[0, 2, 6, 4],   # z0, id    0
                [1, 5, 7, 3],   # z1        1
                [1, 5, 4, 0],   # x0        2
                [3, 7, 6, 2],   # x1        3
                [0, 2, 3, 1],   # y0        4
                [4, 6, 7, 5]]   # y1        5
        self._sides = []
        for i, id in zip(comb, range(len(comb))):
            corners = [self._verts[j] for j in i]
            loc = [(corners[2].pos[i] - corners[0].pos[i]) / 2.0 + corners[0].pos[i] for i in range(3)]
            s = sides.get(str(loc))
            if s is None:
                #print("MAKING NEW SIDE")
                s = side(corners, id, loc)
                sides[str(loc)] = s
            #else:
                #print("REUSING SIDE")
            s.add_parent(self, (id+1) % 2)
            self._sides.append(s)

    def __hash__(self):
        return hash(id(self))


def build(size, obj):
    xrow = []
    for i in range(size[0]):
        yrow = []
        for j in range(size[1]):
            zrow = []
            for k in range(size[2]):
                zrow.append(obj([i,j,k]))
            yrow.append(zrow)
        xrow.append(yrow)
    return xrow

class string:

    def __init__(self, start):
        print("starting new string at {} {} {}".format(*start._loc))
        print(self)
        self._current = start
        self._map = [start]
        self._vox_map = []
        self._loop = False


    def map(self, cls):
        vox = self._current.advance()
        print("PARENT IS ", vox, vox.__repr__())
        print("DIRECTION IS ", self._current._s_direction, " PARENTS ARE ", self._current._parents)
        if vox is None:
            print(self._map)
            if len(self) <= 0:
                return 1
            print("RETURN 0 ", vox)
            return 0
        else:
            self._vox_map.append(vox)

        s_sides = vox._strings[:]
        if len(s_sides) > 2:
            random.shuffle(s_sides)

        next_side = None
        for i in s_sides:
            print(i._loc, i._id, i._s_direction)
            if i in self._map:
                print("ALREADY IN MAP")
                continue
            elif i.is_middle():
                print("IS MIDDLE")
                continue
            elif i._id%2 is i._s_direction:
                next_side = i
                break

        print("next side is ", next_side)
        if next_side is not None:
            if self._current._string_connection is None:
                self._current._string_connection = self
            self._advance(next_side)
        else:
            return 0

        if self._current is None:
            return 1
        else:
            return self.map(cls)

    def _advance(self, side):
        print("advanced to side at {} {} {}".format(*side._loc))
        print("connection is -> ", side._string_connection)
        if side._string_connection is None:
            self._map.append(side)
            side._string_connection = self
            self._current = side
        else:
            side._string_connection.merge(self)
            self._current = None

    def merge(self, string):
        print("called merge from ", string, " to ", self)
        for i in string._map:
            i._string_connection = self
        self._map = string._map + self._map
        if id(string) == id(self):
            print("FOUND A LOOP")
            self._loop = True
        else:
            string.map = []
        print("new map is ", self._map)

    def draw(self, ax):
        xs, ys, zs = [], [], []
        for i in self._map:
            x, y, z = i._loc
            xs.append(x)
            ys.append(y)
            zs.append(z)
        ax.plot(xs, ys, zs, c='r', alpha=0.5)


    def __len__(self):
        return len(self._map) - 1


class cube_universe:
    mapping = [[[]]]
    vertices = [[[]]]
    dim = ()

    def __init__(self, map):
        self.mapping = map
        self.dim = (len(map), len(map[0]), len(map[0][0]))
        self._index_vertices()
        self._assign_vertices()
        self._strings = []
        self._string_voxels = []

    def _index_vertices(self):
        dim = (self.dim[0]+1, self.dim[1]+1, self.dim[2]+1)
        self.vertices = build(dim, vertex)

    def _assign_vertices(self):
        vcts = self.vertices
        sides = {}
        for i in self.mapping:
            for j in i:
                for k in j:
                    x, y, z = k.pos
                    combinations = itertools.product([x, x+1], [y, y+1], [z, z+1])
                    corners = [vcts[s[0]][s[1]][s[2]] for s in combinations]

                    #print(x,y,z)
                    #for i in corners:
                    #    print(i)

                    #print(" next ")
                    k._verts = corners
                    k.calc_sides(sides)


        # self.vertices[1][1][1].theta = 1

    def __getitem__(self, item):
        # select as x, y, z
        # todo: slicing doesn't work
        if type(item) == tuple:
            if len(item) == 3:
                return self.mapping[item[0]][item[1]][item[2]]
            elif len(item) == 2:
                return self.mapping[item[0]][item[1]]
            else:
                raise Exception("Trying to index a dimension above three (i.e. too many arguments).")
        else:
            return self.mapping[item]

    def calc_strings(self):
        string_voxels = []
        for i in self.mapping:
            for j in i:
                for k in j:
                    k.find_strings()
                    if k._has_strings:
                        string_voxels.append(k)
                        #print(k.pos, k._strings)

        print("# voxel strings before set = {}".format(len(string_voxels)))
        all_strings_ = set(string_voxels[:])
        print("# voxel strings after set = {}".format(len(all_strings_)))
        #for i in all_strings_:
            #print(i)
        self._string_voxels = string_voxels

    def _map_strings(self):
        strings = []
        done = []
        for vox in self._string_voxels:
            for i in vox._strings:
                if id(i) in done or i._string_connection is not None:
                    #print("\t -- skipping")
                    continue
                print("\n")
                #print("NOW ON ", i, i._loc)
                s = string(i)
                key = s.map(self)
                print("KEY IS ", key)
                if key == 0:
                    print("added string ", s, " with length ", len(s))
                    strings.append(s)
                done.append(id(i))

        print("pre sort # strings = ", len(strings))
        self._strings = strings
        for s in strings:
            print(id(s), len(s))
            #if len(s) > 0:
                #self._strings.append(s)

        print("Mapped {} strings".format(len(self._strings)))

    def draw_vertices(self, ax):
        xs, ys, zs = [], [], []
        cmaps = []
        for i in self.vertices:
            for j in i:
                for k in j:
                    x, y, z = k.pos
                    xs.append(x)
                    ys.append(y)
                    zs.append(z)
                    cmaps.append(k.theta)
        ax.scatter(xs, ys, zs, c=cmaps, s=0.5, alpha=0.2)

    def draw_cubes(self, ax):
        for i in self.mapping:
            for j in i:
                for k in j:
                    k.draw_sides(ax)

    def draw_strings_verts(self, ax):
        for i in self.mapping:
            for j in i:
                for k in j:
                    k.draw_strings(ax)

uni = cube_universe(build(SIZE, voxel))
#for i in uni[1]:
#    for j in i:
#       print(j)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#print(uni.dim)

uni.calc_strings()
uni.draw_vertices(ax)
uni.draw_cubes(ax)
uni.draw_strings_verts(ax)
#print("Strings: ", uni[0, 0, 1].pos)
#for i in uni[0,0,1]._strings:
#    print("painting", i)
#    i.draw_face(ax)

uni._map_strings()
for i in uni._strings:
    i.draw(ax)

ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
plt.gray()

#for side, i in zip(uni[0,0,0]._sides, range(6)):
    #print("SIDE ID = ", i)
    #for j in side._corners:
    #    print(j)
    #print("\n")

plt.show()


