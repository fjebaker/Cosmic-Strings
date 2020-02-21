import numpy as np 
from cosmicstrings.classifiers.loop import LoopClassifier
from cosmicstrings.classifiers.line import LineClassifier
from cosmicstrings.classifiers.mutual import DiffMapError
from cosmicstrings.io import StringIO
import cosmicstrings.classifiers.visualise as vis
import statistics as stats
import inspect
import resource
import datetime

class Classifier():

	def __init__(self, loops=None, lines=None, dim=None):
		print("Creating Classifier...")
		self.loops = loops
		self.lines = lines
		self._data = {}
		self.dim = dim
		self._fdata = []

	def calculate(self):
		print("Starting calculate method for all strings:\n")
		print("Classifying loops...")
		self.loops.classify()
		print("Classifying lines...")
		self.lines.classify()
		print("\nCalculation complete.")
		# exit(1)

	def _save_function_data(self, *dat):
		index = str(inspect.stack()[1].function)
		self._data[index] = dat

	def save_data_to_file(self):
		time = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
		StringIO.format_new_proc_save(time)
		StringIO.save_processed_data(self._data)

	def load_file_to_data(self, file):
		self._fdata.append(StringIO.load_processed_data(file))
		print(self._fdata)

	def plotl2(self, startn=1, endn=10):
		xloops, yloops = [], []
		xlines, ylines = [], []
		x, y = [], []
		for i in range(startn, endn):
			print("plotl2: now on i = {} of {} [memory @ {}]".format(i, endn,
					resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000**2
				), end='\r')
			_y = []
			try:
				avloops = self.loops.avg_displacements(i)
				yloops.append(avloops)
			except Exception as e:
				pass
			else:
				xloops.append(i)
				_y += avloops
			try:
				avlines = self.lines.avg_displacements(i)
				ylines.append(avlines)
			except Exception as e:
				pass
			else:
				xlines.append(i)
				_y += avlines
			if len(_y) == 0:
				continue
			x.append(i)
			y.append(_y)

		yerr = [stats.stdev(i) for i in y]
		y = [stats.mean(i) for i in y]

		print("plotl2: now on i = {} of {} [memory@{}]".format(endn, endn,
					resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000**2
				))
		print("Done.")

		assert len(y) == len(yerr)
		self._save_function_data(x, y, yerr)
		vis._log_log_plot(x, y, "Length vs. Displacement", "Log (segment length)", "Log (end to end dist)", yerr=yerr)

	def plotperimeter(self):
		x, y, yerr = self._yerr(self.loops.xy_perimeter(), nonZero=True)
		# print(len(self.lines.strings[0]))
		self._save_function_data(x, y, yerr)
		vis._log_log_plot(x, y, "Loop perimeter vs length", "Log (loop perimeter)", "Log (length)", yerr=yerr)

	def plotvol2surf(self):
		x, y, yerr = self._yerr(self.loops.xy_vol2surf(), nonZero=True)
		self._save_function_data(x, y, yerr)
		vis._log_log_plot(x, y, "Loop perimeter vs vol2surf", "Log (loop perimeter)", "Log (loop vol2surf)", yerr=yerr)

	def plotperim2dens(self, maxp=None):
		x, y, yerr = self._yerr(self.loops.xy_perim2dens(maxp=maxp))
		self._save_function_data(x, y, yerr)
		vis._log_log_plot(x, y, "Loop perimeter vs density", "Log (loop perimeter)", "Log (loop density)", yerr=yerr)

	def plotlength2dens(self, maxp=None):
		x, y, yerr = self._yerr(self.loops.xy_length2dens(maxp=maxp))
		self._save_function_data(x, y, yerr)
		vis._log_log_plot(x, y, "Loop length vs density", "Log (loop length)", "Log (density)", yerr=yerr)

	def _yerr(self, vals, nonZero=False):
		x, y = vals
		data = {} # x:[[y]] -> [x], [y], [yerr]
		for i, j in zip(x, y):
			if i in data:
				data[i].append(j)
			else:
				data[i] = [j]
		xr, yr, yerr = [], [], []
		for key, val in data.items():
			_y = data[key]
			mean = stats.mean(_y)
			try:
				sd = stats.stdev(_y)
			except stats.StatisticsError as e:
				sd = 0
			xr.append(key)
			yr.append(mean)

			if sd == 0 and nonZero:
				sd = 1e-10
			yerr.append(sd)
		return xr, yr, yerr		

def classify(strings=None, dim=None):
	if strings is None and dim is None:
		return Classifier()
	elif strings is not None and dim is None:
		raise Exception()
	elif strings is None and dim is not None:
		raise Exception()
	# seperate loops and lines
	dim = [dim for i in range(3)]
	loops = []
	lines = []
	for i in strings:
		if i.is_loop():
			loops.append(i)
		else:
			lines.append(i)
	cloops = LoopClassifier(loops, dim)
	clines = LineClassifier(lines, dim)
	return Classifier(cloops, clines, dim)




