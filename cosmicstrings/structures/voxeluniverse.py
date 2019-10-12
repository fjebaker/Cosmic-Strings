from functools import reduce
from cosmicstrings.structures.voxel import Voxel
from cosmicstrings.structures.vertex import Vertex
from cosmicstrings.structures.string import CString, CStringL
import itertools
import resource
import numpy as np


def build_3d_grid(shape, obj):
    print("\nBuidling '{}':".format(obj))
    xrow = []
    for i in range(shape[0]):
        print(" - Generating slice {} of {}".format(i, shape[0]), end='\r')
        yrow = []
        for j in range(shape[1]):
            zrow = []
            for k in range(shape[2]):
                zrow.append(obj([i, j, k]))
            yrow.append(zrow)
        xrow.append(yrow)
    print(" - Generating slice {} of {}".format(shape[0], shape[0]))
    print(" - Done!")
    return xrow

def print_memory_usage():
    print("Memory usage at {} M".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000**2))


class VUniverse:

    def __init__(self, shape):
        print("Creating universe...")
        print_memory_usage()
        self.mapping = build_3d_grid(shape, Voxel)
        self.vertices = build_3d_grid([i + 1 for i in shape], Vertex)
        self.shape = shape
        self.strings = []
        print_memory_usage()

    def assign_vertices(self, periodic=False):
        self._periodic = periodic
        print("\nAssigning vertices to voxels:")
        sides = {}
        self.limit = reduce((lambda x, y: x * y), self.shape)
        count = 0
        for i in self.ordered_all_voxels():
            print(" - Assigned {} of {} voxels".format(count, self.limit), end='\r')
            count += 1
            x, y, z = i.pos
            comb = itertools.product([x, x+1], [y, y+1], [z, z+1])
            corners = [self.vertices[s[0]][s[1]][s[2]] for s in comb]
            i.verts = corners
            i.calc_sides(sides)
        print(" - Assigned {} of {} voxels".format(count, self.limit))
        print_memory_usage()
        if periodic:
            print("\nMaking boundaries periodic...")
            self._make_periodic()
            print("Done")

    def _make_periodic(self):
        for i, j in zip(self.get_x_plane(0), self.get_x_plane(-1)):
            j.sides[5].adopt(i.sides[4])

        for i, j in zip(self.get_y_plane(0), self.get_y_plane(-1)):
            j.sides[3].adopt(i.sides[2])

        for i, j in zip(self.get_z_plane(0), self.get_z_plane(-1)):
            j.sides[1].adopt(i.sides[0])

    def draw_cubes(self, ax):
        for i in self.ordered_all_voxels():
            # print(i)
            i.draw_outline(ax)

    def draw_connections(self, ax):
        for i in self.ordered_all_voxels():
            i.draw_connections(ax)

    def calculate_strings(self):
        print("\nCalculating string connections:")
        nodes = []
        count = 0
        for i in self.ordered_all_voxels():
            print(" - Face {} of {} completed".format(count*6, self.limit*6), end='\r')
            count += 1
            i.find_strings()
            # print(i, "nodes: ", len(i._string_sides))
            if len(i._string_sides) > 0:
                nodes += i.connect_nodes()
            # print()
        print(" - Face {} of {} completed".format(count*6, self.limit*6))

        nodes = set(nodes)
        print("Found {} connections".format(len(nodes)))
        print_memory_usage()
        starts = [node for node in nodes if node.get_connections()[0] is None]

        print("\nConnecting simple strings objects together...")
        to_remove = self._build_strings(starts)     # linear strings
        print_memory_usage()

        for i in to_remove:
            nodes.remove(i)

        if self._periodic:
            print("Connecting boundary strings...")
            self._loop_periodic()
        print("Connections after removing : ", len(nodes))
        print("Connecting loop string objects together...")
        self._build_strings(nodes)           # loop strings

        print("Built {} strings.".format(len(self.strings)))
        print_memory_usage()

    def _print(self, nodes):
        for node in nodes:
            print(node.pos, end=" --> ")
            for i in node.get_connections():
                print(i, end=", ")
            print()

    def _loop_periodic(self):
        strings_deck = {}
        for i in self.strings:
            strings_deck[str(i.get_start())] = i

        strings = []
        used = []
        for i in self.strings:
            if i in used:
                continue
            while True:
                j = strings_deck[str(i.get_conjugate_end(self.shape))]
                if i == j and type(i) is CStringL:
                    break
                used.append(j)
                i = i.connect(j)
                strings_deck[str(i.get_start)] = i
            strings.append(i)

        for i in strings:
            i.calc_loop()
        self.strings = strings


    def _build_strings(self, starts):
        used_nodes = []
        count = 0
        for start in starts:
            print(" - Node {} of {} connected [memory @ {} M]".format(count, len(starts), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000**2), end='\r')
            count += 1
            if start in used_nodes:
                continue
            s = CString(start)
            s.build_string()
            self.strings.append(s)
            used_nodes += s.get_map()
        print(" - Node {} of {} connected".format(count, len(starts)))
        return used_nodes

    def draw_strings(self, ax, differ_loops=False):
        if differ_loops:
            for i in self.strings:
                if i.is_loop():
                    i.draw(ax, c='b')
                else:
                    i.draw(ax, linewidth=0.5)
        else:
            for s in self.strings:
                s.draw(ax)

    def classify_strings(self):
        loops = []
        non_loop = []
        loop_lengths = []
        non_loop_lengths = []
        for i in self.strings:
            if i.is_loop():
                loop_lengths.append(len(i))
                loops.append(i)
            else:
                non_loop_lengths.append(len(i))
                non_loop.append(i)

        loop_lengths = np.array(loop_lengths, dtype=float)
        non_loop_lengths = np.array(non_loop_lengths, dtype=float)

        print("\n\nFound        {} strings;".format(len(self.strings)))
        print("Of which     {} are loops.".format(len(loops)))
        try:
            print("")
            print("Lengths :: non-loop")
            print("             {} mean".format(np.mean(non_loop_lengths)))
            print("             {} max".format(np.max(non_loop_lengths)))
            print("             {} min".format(np.min(non_loop_lengths)))
            print("")
            print("Lengths :: loops")
            print("             {} mean".format(np.mean(loop_lengths)))
            print("             {} max".format(np.max(loop_lengths)))
            print("             {} min".format(np.min(loop_lengths)))
        except:
            pass

    def ordered_all_voxels(self):
        for i in self.mapping:
            for j in i:
                for k in j:
                    yield k

    def get_x_plane(self, index):
        for i in self.mapping[index]:
            for j in i:
                yield j

    def get_y_plane(self, index):
        for i in self.mapping:
            for j in i[index]:
                yield j

    def get_z_plane(self, index):
        for i in self.mapping:
            for j in i:
                yield j[index]

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