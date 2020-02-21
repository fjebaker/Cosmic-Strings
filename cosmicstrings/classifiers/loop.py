from cosmicstrings.classifiers.mutual import _BaseClass
from cosmicstrings.classifiers.mutual import _LC
from functools import lru_cache

class LoopClassifier(_BaseClass):
	
	def __init__(self, strings, shape):
		self.strings = [_LC(string, shape) for string in strings]
		self.shape = shape
		self.N3 = self.shape[0] * self.shape[1] * self.shape[2]
		self._type = "LOOP"

	def xy_perimeter(self):
		x, y = [], []
		for i in self.strings:
			x.append(len(i))
			y.append(sum(LoopClassifier.extent_v(i)))
		#print("AA")
		#print(x, y)
		return x, y

	def xy_vol2surf(self):
		x, y = [], []
		for i in self.strings:
			n1, n2, n3 = LoopClassifier.extent_v(i)
			x.append(n1 + n2 + n3)
			v2s = (n1 * n2 * n3) / (2 * ((n1 * n2) + (n1 * n3) + (n2 * n3)))
			y.append(v2s)
		return x, y

	def xy_perim2dens(self, maxp=None):
		func = lambda i: int(sum(LoopClassifier.extent_v(i)))
		return self._xy_func2dens(func, maxp=maxp)

	def _xy_func2dens(self, func, maxp=0):
		counter = {}
		for i in self.strings:
			R = func(i)
			if R in counter:
				counter[R] += 1
			else:
				if maxp is not None:
					if R > maxp:
						continue
				counter[R] = 1

		x = list(counter.keys())
		y = counter.values()
		
		y = [i/self.N3 for i in y]
		return x, y

	def xy_length2dens(self, maxp=None):
		func = lambda i: len(i)
		return self._xy_func2dens(func, maxp=maxp)

	@staticmethod
	@lru_cache(None)
	def extent_v(loop_LC):
		""" EXTENT VECTOR """
		minimal, maximal = [0,0,0], [0,0,0]
		trace = [0,0,0]
		for i in loop_LC._diff_map[:-1]:
			trace = [p1 + p2 for p1, p2 in zip(trace, i)]
			maximal = [max(p1, p2) for p1, p2 in zip(maximal, trace)]
			minimal = [min(p1, p2) for p1, p2 in zip(minimal, trace)]
		extent = [p1 - p2 + 1 for p1, p2 in zip(maximal, minimal)]
		# print(extent)
		return extent