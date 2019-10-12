
class CString:

    def __init__(self, start):
        self._current = start
        self._map = [start]
        self._loop = False

    def build_string(self):
        while True:
            next_item = self._current.get_connections()[1]
            if next_item is None:
                break
            elif next_item in self._map:
                self._loop = True
                break
            self._step(next_item)

    def _step(self, next_item):
        self._map.append(next_item)
        self._current = next_item

    def draw(self, ax, c='r', alpha=0.5, **kwargs):
        x, y, z = self.get_coords()
        ax.plot(x, y, z, c=c, alpha=alpha, **kwargs)

    def is_loop(self):
        return self._loop

    def get_map(self):
        return self._map

    def get_coords(self):
        X, Y, Z = [], [], []
        _map = self._map
        if self._loop:
            _map = [*_map, _map[0]]
        for i in _map:
            x, y, z = i.pos
            X.append(x)
            Y.append(y)
            Z.append(z)
        return X, Y, Z

    def get_start(self):
        return self._map[0].pos

    def get_end(self):
        return self._map[-1].pos

    def get_conjugate_end(self, mx):
        pos = self._map[-1].pos[:]
        if 0 not in pos:
            pos2 = [i - j for i, j in zip(pos, mx)]
            index = pos2.index(0)
            mx = [-1 * i for i in mx]
        else:
            index = pos.index(0)
        pos[index] += mx[index]
        return pos


    def connect(self, b):
        return CStringL(self, b)

    def __len__(self):
        l = len(self._map)
        if not self._loop:
            l -= 1
        return l

    def __eq__(self, other):
        if self._map == other.get_map():
            return True
        else:
            return False


class CStringL(CString):
    def __init__(self, a, b):
        super().__init__(None)
        if type(a) is CStringL:
            #print('a is CL, connected with b')
            self.__dict__ = a.__dict__
            self.substrings.append(b)
            self._map += b._map
        else:
            #print('{} connected with {}'.format(a.get_end(), b.get_start()))
            self.substrings = [a, b]
            self._map = a._map + b._map

    def draw(self, ax, **kwargs):
        for s in self.substrings:
            s.draw(ax, **kwargs)

    def calc_loop(self):
        tots = [0, 0, 0]
        key = {1:[0,0,1], 0:[0,0,-1],
               3:[0,1,0], 2:[0,-1,0],
               5:[1,0,0], 4:[-1,0,0]}

        sbst = self.substrings
        for i in sbst:
            k = list(i.get_map()[-1].parents.values())[0][0]
            tots = [i + j for i, j in zip(tots, key[k])]

        self._config = tots
        if tots == [0, 0, 0]:
            self._loop = True

    def __eq__(self, other):
        if type(other) == CStringL:
            return self.substrings == other.substrings
        else:
            return other is self.substrings[0]
