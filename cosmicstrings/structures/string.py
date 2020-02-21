import code


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

    def build_su2_string(self):
        next_item = self._current.get_connections()
        #print(next_item)
        if all([i is not None for i in next_item]):
            self._loop = True

        while True:
            select = None
            for i in next_item:
                if i is None or i in self._map:
                    continue
                else:
                    select = i
            if select is None:
                break
            self._step(select)
            next_item = self._current.get_connections()

    def old_build_su2_string(self):
        next_item = self._current.get_connections()
        if next_item[0] is None:
            s = 1
            end = None
        elif next_item[1] is None:
            s = 0
            end = None
        else:
            s = 0
            print("LOOP")
            self._loop == True
            end = next_item[s^1]

        while True:
            it = next_item[s]
            print("\nOPTIONS:", next_item)
            print("SELECT:", hex(id(it)))
            input()
            if it is end:
                print("BROKE")
                break
            self._step(it)
            next_item = self._current.get_connections()
            s ^= 1

    def _step(self, next_item):
        self._map.append(next_item)
        self._current = next_item

    def draw(self, ax, c='r', alpha=0.5, **kwargs):
        x, y, z = self.get_plot_coords()
        ax.plot(x, y, z, c=c, alpha=alpha, **kwargs)

    def is_loop(self):
        return self._loop

    def get_map(self):
        return self._map

    def get_plot_coords(self):
        X, Y, Z = [], [], []
        _map = self._map
        if self._loop:
            _map = [*_map, _map[0]]
        else:
            _map = _map[:-1]
            x, y, z = _map[0].pos
            X.append(x)
            Y.append(y)
            Z.append(z)
        for i in _map:
            #parent_c = i.get_parent_center()
            parent_c = i.pos
            if parent_c is None:
                continue
            x, y, z = parent_c
            X.append(x)
            Y.append(y)
            Z.append(z)
        if not self._loop:
            x, y, z = self._map[-1].pos
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
        """ DODGY -- works when reading from text file; investigate why if you have time """
        l = len(self._map) - 1
        return l

    def __eq__(self, other):
        if self._map == other.get_map():
            return True
        else:
            return False

    def __str__(self):
        t = 'closed' if self._loop else 'open'
        return "{} with length {}".format(t, len(self))  


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
