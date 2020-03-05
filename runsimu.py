from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
import matplotlib.pyplot as plt
from cosmicstrings.structures.voxeluniverse import VUniverse
from cosmicstrings.io import StringIO
from cosmicstrings import Pipeline
import random
import os
from datetime import datetime

import sys
import argparse

def d3plot(params):
	global UNI, DIM
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.set_xlabel('X axis')
	ax.set_ylabel('Y axis')
	ax.set_zlabel('Z axis')

	ax.set_xlim3d(0, DIM)
	ax.set_ylim3d(0, DIM)
	ax.set_zlim3d(0, DIM)

	UNI.draw_strings(ax, differ_loops=True if 'differ' in params else False)

	for i in params:
		if i == 'conn':
			UNI.draw_connections(ax)
		elif i == 'voxels':
			UNI.draw_cubes(ax)

	plt.show()

parser = argparse.ArgumentParser()
parser.add_argument('--dim', type=int, default=[40], nargs=1, help="Integer dimension of the simulated Universe. Default is 40.")
parser.add_argument('--su2', action='store_true', help="Set symmetry group to SU(2).")
parser.add_argument('--periodic', action='store_true', help="Use periodic boundary conditions.")
parser.add_argument('--seed', type=int, default=[random.randrange(sys.maxsize)], nargs=1, help="PRNG seed value.")
parser.add_argument('--plot', nargs='*', choices=['voxels', 'conn', 'differ'], metavar='OPTION', help="Plot controls: 'differ' to colour closed and open strings differently, 'conn' to include connections, 'voxels' to include outlines of voxels.")
parser.add_argument('--save_dir', type=str, default=['data/raw_4'], nargs=1, help="DATA_FILE save directory. Default is '/data/raw.'")

args = parser.parse_args()

# GLOBALS
UNI = None
DIM = args.dim[0]
SU2 = args.su2
PERIODIC = args.periodic
SEED = args.seed[0]
SAVE_DIR = args.save_dir[0].strip('/')

PIPE = Pipeline()

if args.plot is not None:
	PIPE.add_end(lambda : d3plot(set(args.plot)))

def setup():
	global DIM, SU2, PERIODIC, SEED, UNI, SAVE_DIR
	random.seed(SEED)

	TIME = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
	GAUGE = 'SU2' if SU2 else 'U1'
	# TODO os.environ["LOG_FILE"] = "data/testlog.log"
	os.environ["DATA_FILE"] = "{}/{}_{}_{}_test.dat".format(SAVE_DIR, DIM, "periodic" if PERIODIC else "normal", GAUGE)

	dim = [DIM for i in range(3)]
	StringIO.format_new_string_save(TIME, SEED, DIM, PERIODIC, GAUGE)

	UNI = VUniverse(dim, su2=SU2)
	UNI.assign_vertices(periodic=PERIODIC)

	UNI.calculate_strings()
	UNI.save_state()

PIPE.add_start(setup)
PIPE()