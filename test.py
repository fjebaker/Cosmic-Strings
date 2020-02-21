from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import matplotlib.pyplot as plt
from cosmicstrings.structures.voxeluniverse import VUniverse
from cosmicstrings.io import StringIO
import random
import os
from datetime import datetime

import sys

SEED = random.randint(1, 100) #41
DIM = 10
SU2 = True
PERIODIC = True

if len(sys.argv) == 3:
	if sys.argv[1] == 'dim':
		DIM = int(sys.argv[2])

TIME = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
GAUGE = 'SU2' if SU2 else 'U1'

# TODO os.environ["LOG_FILE"] = "data/testlog.log"
os.environ["DATA_FILE"] = "data/raw_5/{}_{}_{}_test.dat".format(DIM, "periodic" if PERIODIC else "normal", GAUGE)

random.seed(SEED)
dim = [DIM for i in range(3)]

StringIO.format_new_string_save(TIME, SEED, DIM, PERIODIC, GAUGE)

uni = VUniverse(dim, su2=SU2)
uni.assign_vertices(periodic=PERIODIC)

def d3plot():
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
	uni.draw_strings(ax, differ_loops=True)

uni.calculate_strings()
uni.save_state()

#C = uni.make_classifier()
#C.calculate()
#C.plotl2()

d3plot()
plt.show()