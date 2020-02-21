from cosmicstrings.classifiers.mutual import _BaseClass
from cosmicstrings.classifiers.mutual import _LC

class LineClassifier(_BaseClass):

	def __init__(self, strings, shape):
		self.strings = [_LC(string, shape) for string in strings]
		self._type = "LINE"
