import numpy as np
from functools import lru_cache
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection


class VSide:
    _comb = {0:[0,0,-1], 1:[0,0,1],
            2:[0,-1,0], 3:[0,1,0],
            4:[-1,0,0], 5:[1,0,0]}

    def __init__(self, corners, pos, su2):
        self.pos = pos
        self.parents = {}

        self._corners = corners
        self._direction = None
        self._string = None
        self._connections = [None, None]
        self._side_drawn = False

    def get_direction(self):
        return self._find_direction()

    def su2_node(self):
        sum_product = 1
        for i, j in zip([0, 1, 2, 3],
                        [1, 2, 3, 0]):
            a = self._corners[i].theta
            b = self._corners[j].theta
            sum_product *= np.dot(a, b)
        if sum_product < 0:
            self._direction = 1
        return self._direction

    @lru_cache(None)
    def _find_direction(self):
        sum_angle = 0
        prev = self._corners[0].theta
        for vertex in [*self._corners, self._corners[0]]:
            t = vertex.theta
            diff = (t - prev + np.pi) % (2 * np.pi) - np.pi
            sum_angle += diff
            prev = t
        if sum_angle > 2 * np.pi - 0.0001:
            self._direction = 0
        elif sum_angle < -2 * np.pi + 0.0001:
            self._direction = 1
        return self._direction

    def draw_sides(self, ax):
        if self._side_drawn:
            return
        ax.add_collection3d(Line3DCollection(self._get_coords(),
                            colors='k',
                            alpha=0.1,
                            linewidths=1,
                            linestyle='--'))
        self._side_drawn = True

    def draw_face(self, ax):
        ax.add_collection3d(Poly3DCollection(self._get_coords(),
                            color='r',
                            alpha='0.1'))

    def draw_connection(self, ax):
        if self._direction is not None:
            if self._direction == 1:
                marker = 'x'
            else:
                marker = 'o'
            ax.scatter(*self.pos, marker=marker)

    def add_parent(self, parent, pos, id):
        self.parents[pos] = (id, parent)

    def get_parent(self, i):
        return self.parents.get(i)

    def get_parent_center(self):
        dr = self._find_direction           # TODO wont work for SU(2)
        parent = self.parents.get(dr)
        diff = 0.5
        if parent is None:
            parent = self.parents.get(dr^1)
            shift = self._comb[parent[0]]
            vertp = parent[1].verts[0].pos
            ret = [vertp[i] + shift[i] + diff for i in range(3)]
            return ret
        else:
            corner = parent[1].verts[0]
            ret = [i + diff for i in corner.pos]
            return ret

    def connect_side(self, side):
        self._connections[0] = side
        side._connections[1] = self

    def su2_connect_side(self, side):
        self._su2_flipflop(side)
        side._su2_flipflop(self, receiver=True)

    def _su2_flipflop(self, side, receiver=False):
        i = 1; j = 0
        #if receiver:
        #    i = 1
        #    j = 0

        if self._connections[i] is None:
            self._connections[i] = side

        elif self._connections[j] is None:
            self._connections[j] = side

        else:
            raise

    def get_connections(self):
        return self._connections

    def adopt(self, side):
        for i, j in zip(range(4), range(4)):
            self._corners[i].theta = side._corners[j].theta

    def _get_coords(self):
        X, Y, Z = [], [], []
        for i in [*self._corners, self._corners[0]]:
            x, y, z = i.pos
            X.append(x)
            Y.append(y)
            Z.append(z)
        return [list(zip(X, Y, Z))]

    def __eq__(self, othr):
        if self.pos == othr.pos:
            return True
        else:
            return False

    def __str__(self):
        return "VSide pos: {} {} {}".format(*self.pos)

    def __sub__(self, othr):
        return [self.pos[i] - othr.pos[i] for i in range(3)]

    def __hash__(self):
        return hash(str(self.pos))

class tVSide(VSide):  # text VSide

    def __init__(self, pos, parent_center):
        self.pos = pos
        self._corners = None
        self._parent_center = parent_center
    
    def get_parent_center(self):
        return self._parent_center


