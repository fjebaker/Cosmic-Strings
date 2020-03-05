from cosmicstrings.io import StringIO
import os
import statistics

class PMerge:
	def __init__(self):
		self._dim = 0
		self._data = {}
		self._proc_data = {}

	@property
	def dim(self):
		return self._dim

	@dim.setter
	def dim(self, val):
		if self._dim == val or self._dim == 0:
			self._dim = val
		else:
			raise Exception("DIM not equal.")
	
	def add_source(self, src):
		data = StringIO.load_processed_data(src)
		for key, v in data.items():
			if key in self._data:
				x, ys = self._data[key]
				y = [None for _ in x]
				for x2, y2 in zip(*v):
					try:
						ind = x.index(x2)
					except ValueError as e:
						x.append(x2)
						y.append(None)
						for others in ys:
							others.append(None)
						ind = -1
					y[ind] = y2
				ys.append(y)
				self._data[key] = (x, ys)
			else:
				self._data[key] = (v[0], [v[1]])	# [x1, x2 ..] [[1y1, 1y2, ..], [2y1, 2y2, ..]]

	@staticmethod
	def _none_avg(data):
		means = []
		stds = []
		for ind in range(len(data[0])):
			temp = []
			for row in data:
				i = row[ind]
				if i is not None:
					temp.append(i)
			assert len(temp) != 0 
			if len(temp) == 1:
				stds.append(0)
				means.append(temp[0])
			else:
				stds.append(statistics.stdev(temp))
				means.append(statistics.mean(temp))
		stds = [i if i != 0 else 0.0001 for i in stds]
		return (means, stds)

	def merge(self):
		for key, v in self._data.items():
			x, y = v
			proc = PMerge._none_avg(y)
			self._proc_data[key] = (x, proc)
		self._data = {}

	def retrieve(self, key):
		return self._proc_data[key]
