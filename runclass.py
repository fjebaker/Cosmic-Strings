from cosmicstrings.io import StringIO
from cosmicstrings.classifiers import classify
from cosmicstrings.classifiers import PMerge
from cosmicstrings.classifiers.visualise import MPlot
import sys
import os

import argparse

from cosmicstrings import Pipeline

def mkfls(lst):
	all_files = []
	for item in lst:
		if os.path.isdir(item):
			all_files += [os.path.join(item, i) for i in os.listdir(item) if '.dat' in i]
		else:
			all_files.append(item)
	return all_files

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--data_file', nargs='+', type=str, required=True, help="DATA_FILE to classify. May be a directory to be unpacked.")
parser.add_argument('-l', '--load', action='store_true', help="Enable 'proc' data file load mode.")

parser.add_argument('-a', action='store_true', help="Run all classification routines.")

parser.add_argument('-o', '--output_dir', type=str, help="Output directory for the save file. Will not save if this flag is not set.")

parser.add_argument('--l2R', action='store_true', help="Length l against displacement R.")
parser.add_argument('--perimeter', action='store_true', help="Perimeter of closed strings P vs length l.")
parser.add_argument('--vol2surf', action='store_true', help="Volume against surface area.")
parser.add_argument('--p2dens', action='store_true', help="Perimeter P vs density.")
parser.add_argument('--l2dens', action='store_true', help="Length l vs density.")
parser.add_argument('--hist', action='store_true', help="Histogram of string length.")
parser.add_argument('--maxl', nargs=1, type=int, default=[20], help="Maximum length of string to use.")
parser.add_argument('--minl', nargs=1, type=int, default=[2], help="Minimum length of string to use.")

parser.add_argument('--plot', action='store_true', help="Show plots after calculation.")

args = parser.parse_args()

# globals
OUT = args.output_dir
CLASS = None
ENDN = args.maxl[0]
MINL = args.minl[0]

def pipeconfig(PIPE):
	global CLASS, OUT
	if args.a:
		PIPE.add(lambda: CLASS.plotl2(startn=MINL, endn=ENDN))
		PIPE.add(lambda: CLASS.plotperimeter())
		PIPE.add(lambda: CLASS.plotvol2surf())
		PIPE.add(lambda: CLASS.plotperim2dens(maxp=ENDN))
		PIPE.add(lambda: CLASS.plotlength2dens(maxp=ENDN))
		PIPE.add(lambda: CLASS.lhist_lines())
		PIPE.add(lambda: CLASS.lhist_loops())
	else:
		if args.l2R:
			PIPE.add(lambda: CLASS.plotl2(startn=MINL, endn=ENDN))
		if args.perimeter:
			PIPE.add(lambda: CLASS.plotperimeter())
		if args.vol2surf:
			PIPE.add(lambda: CLASS.plotvol2surf())
		if args.p2dens:
			PIPE.add(lambda: CLASS.plotperim2dens(maxp=ENDN))
		if args.l2dens:
			PIPE.add(lambda: CLASS.plotlength2dens(maxp=ENDN))
		if args.hist:
			PIPE.add(lambda: CLASS.lhist_lines())
			PIPE.add(lambda: CLASS.lhist_loops())

	if OUT is not None:
		PIPE.add(lambda: CLASS.save_data_to_file())

	if args.plot:
		import matplotlib.pyplot as plt
		PIPE.add_end(lambda: plt.show())

def run_merge():
	global CLASS

	PM = PMerge()
	for i in mkfls(args.data_file):
		PM.add_source(i)

	CLASS = MPlot(PM)

	PIPE = Pipeline()
	PIPE.add_start(lambda: PM.merge())
	pipeconfig(PIPE)
	PIPE()

def run_class():
	PIPE = Pipeline()
	def setup():
		global PATH, CLASS
		os.environ["DATA_FILE"] = PATH
		if OUT is not None:
			os.environ["PROC_SAVE_PATH"] = OUT

		stringdat, dim = StringIO.load_strings()
		CLASS = classify(stringdat, dim)
		CLASS.calculate()

	PIPE = Pipeline()
	PIPE.add_start(setup)

	pipeconfig(PIPE)
	PIPE()

if __name__ == '__main__':
	if args.load:
		run_merge()
	else:
		for file in mkfls(args.data_file):
			print("Classifying file '{}'...\n".format(file))
			PATH = file
			run_class()
