class Pipeline:

	def __init__(self):
		self.start = []
		self.pipe = []
		self.end = []

	def add_start(self, fun):
		self.start.append(fun)

	def add_end(self, fun):
		self.end.append(fun)

	def add(self, fun):
		self.pipe.append(fun)

	def __call__(self):
		phases = [self.start, self.pipe, self.end]
		for phase in phases:
			for i in phase:
				try:
					i()
				except Exception as e:
					print("PIPE ERROR")
					print("\t[!] function = '{}'".format(i))
					print("\t[-] error: {}".format(str(e)))
					print("\t[+] error not fatal.")
					
					