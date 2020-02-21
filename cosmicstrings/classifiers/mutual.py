import builtins
import numpy as np
import resource
import os
from functools import lru_cache
import statistics as stats

class DiffMapError(Exception):
	def __init__(self, msg):
		super().__init__(msg)


class _BaseClass:

	def __init__(self):
		pass

	def classify(self):
		i = 0
		for string in self.strings:
			i += 1
			print("{} of {} done... [memory @ {}]".format(i, len(self.strings),
				resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000**2), end='\r')
			# MAIN CALCULATE METHOD
			string._calculate()
		
		print("{} of {} done... [memory @ {}]".format(i, len(self.strings),
			resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1000**2))
		print()

	def avg_displacement(self, n):
		disp = self.avg_displacements(n)
		return stats.mean(disp), stats.stdev(disp)

	def avg_displacements(self, n):
		disp = []
		j = 0
		while True:
			# print("{}: shift param = {}          ".format(self._type, j), end='\r')
			val = []
			for i in range(len(self.strings)):
				try:
					val.append(self.strings[i].displacement(n, start=j))
				except DiffMapError as e:
					continue
			if len(val) == 0:
				break
			disp += val
			j += 1
		return disp

class _LC:
	
	def __init__(self, string, shape):
		self.string = string
		self.shape = [i - 1 for i in shape]
		self._smap = self.string.get_map()

	def __len__(self):
		return len(self.string)

	def _adjust_periodic(self, coords):
		for i in range(3):
			if abs(coords[i]) >= self.shape[i]:
				# print("NON PERIODIC", coords)
				if coords[i] >= self.shape[i]:
					coords[i] += 1 - self.shape[i]
				elif coords[i] <= -self.shape[i]:
					coords[i] += self.shape[i] - 1
				coords[i] *= -1
				# print("ADJUSTED TO", coords)
		return coords

	def _calc_diffmap(self):
		"""
		
		diffmap[i] is node[i+1] - node[i]
		
		diffmap[0] is the difference vector from origin to the first point
		diffmap[n] is the difference vector from the endpoint to the first point
			for loops, implies a check == 0
			for opens, implies a check >> 0
			either way, is a null data point

		len(diffmap) == len(map)

		"""
		smap = self.string.get_map()
		diffmap = []
		cdiff = lambda p1, p2: self._adjust_periodic([p1p - p2p for p1p, p2p in zip(p1, p2)])
		for i in range(len(smap)-1):
			a, b = smap[i+1].get_parent_center(), smap[i].get_parent_center()
			diff = cdiff(a, b)
			diffmap.append(diff)
		diffmap.append(cdiff(
			smap[-1].get_parent_center(), smap[0].get_parent_center())
		)
		# print(diffmap)
		self._diff_map = diffmap

	def l2_dist(self, n, start=0):
		# essentially just a linear count, but also a check
		if n + start > len(self._diff_map) - 1:
			raise DiffMapError("Trying to index check condition")
		n += start
		innersum = 0
		for i in range(start, n):
			# print("nval: ", self._diff_map[i])
			innersum += np.sqrt(sum(map(lambda x: x**2, self._diff_map[i])))
		return innersum

	def displacement(self, n, start=0):
		if n + start > len(self._diff_map) - 1:
			raise DiffMapError("Trying to index check condition")
		n += start
		innersum = [0,0,0]
		for i in range(start, n):
			innersum = [p1 + p2 for p1, p2 in zip(innersum, self._diff_map[i])]
		innersum = sum([i**2 for i in innersum])
		return np.sqrt(innersum)

	def _calculate(self):
		self._calc_diffmap()
		pass




