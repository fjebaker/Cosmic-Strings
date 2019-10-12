from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import matplotlib.pyplot as plt
from cosmicstrings.structures.voxeluniverse import VUniverse
import random

random.seed(6)
dim = [20 for i in range(3)]

uni = VUniverse(dim)
uni.assign_vertices(periodic=True)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

ax.set_xlim3d(0, max(dim))
ax.set_ylim3d(0, max(dim))
ax.set_zlim3d(0, max(dim))

#uni.draw_cubes(ax)
#uni.draw_connections(ax)
uni.calculate_strings()
uni.draw_strings(ax, differ_loops=True)
uni.classify_strings()

plt.show()