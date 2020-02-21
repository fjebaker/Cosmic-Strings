from cosmicstrings.structures.string import CString 
from cosmicstrings.structures.voxelside import tVSide
import os
import re

class StringIO:


	@staticmethod
	def save_strings(strings, save='all'):
		if save == 'smap':
			StringIO._save_smap(strings)
		elif save == 'voxel':
			StringIO._save_parent(strings)
		elif save == 'all':
			StringIO._save_all(strings)

	@staticmethod
	def format_new_string_save(time, seed, dimension, periodic, gauge):
		with open(os.environ["DATA_FILE"], 'w') as f:
			f.write("COSMIC-STRING DATA FILE CREATED {}\n".format(time))
			f.write("PRNG_SEED={} DIM={} P-BOUND={} GAUGE={}\n".format(seed, dimension, periodic, gauge))

	@staticmethod
	def format_new_proc_save(time):
		fname = "_proc.".join(os.path.split(os.environ["DATA_FILE"])[-1].split("."))
		with open(os.path.join(
				os.environ["PROC_SAVE_PATH"], fname), 
			'w') as f:
			f.write("COSMIC-STRING PROC FILE CREATED {}\n".format(time))
			f.write("ASSOCIATED DATA FILE '{}'".format(os.environ["DATA_FILE"]))

	@staticmethod
	def _save_all(strings):
		fmtr = lambda i: str(i.pos)[1:-1] + ':PC:' + str(i.get_parent_center())[1:-1] + "*"
		StringIO._save_strings(strings, "ALL", fmtr)

	@staticmethod
	def _save_parent(strings):
		fmtr = lambda i: str(i.get_parent_center())[1:-1] + "*"
		StringIO._save_strings(strings, "PARENT", fmtr)

	@staticmethod
	def _save_smap(strings):
		fmtr = lambda i: str(i.pos)[1:-1] + "*"
		StringIO._save_strings(strings, "SMAP", fmtr)

	@staticmethod
	def _save_strings(strings, stype, fmtr):
		file = os.environ["DATA_FILE"]
		print("\nSaving state to '{}'.".format(file))
		out = stype + "\n"
		for string in strings:
			desc = ""
			for i in string.get_map():
				desc += fmtr(i)
			out +=  "**" + str(int(string.is_loop())) + "*" + str(desc)[:-1]
		with open(file, 'a+') as f:
			f.write("TOTAL {}\n".format(len(strings)) + out.replace(' ', ''))

	@staticmethod
	def load_strings(file=None):
		if file is None:
			file = os.environ["DATA_FILE"]
		with open(file, 'r') as f:
			data = f.read().split('\n')
		method = data[-2]
		if method == 'ALL':
			return StringIO._load_all(data)
		elif method == 'SMAP':
			return StringIO._load_smap(data)
		elif method == 'PARENT':
			return StringIO._load_smap(data)

	@staticmethod
	def _load_all(data):
		raw_strings = [i for i in data[-1].split('**') if i is not '']
		strings = []
		for string in raw_strings:
			s = string.split('*')
			smap = []
			for i in s[1:]:
				j, k = i.split(':PC:')
				side = tVSide(
					list(map(float, j.split(','))),
					list(map(float, k.split(',')))
					)
				smap.append(side)
			cs = CString(None)
			cs._loop = bool(s[0] == '1')
			if cs._loop:
				smap.append(smap[0])
			cs._map = smap
			strings.append(cs)
		dim = int(re.search(r"DIM=(\d*)", data[1]).group(1))
		print("Read in {} strings from data file of dim={}.".format(len(strings), dim))
		return strings, dim

	@staticmethod
	def _load_smap(data):
		raw_strings = [i for i in data[-1].split('**') if i is not '']
		strings = []
		for string in raw_strings:
			s = string.split('*')
			coords = [list(map(float, i.split(','))) for i in s[1:]]
			coords = [tVSide(i, i) for i in coords]
			cs = CString(None)
			cs._loop = bool(s[0] == '1')
			if cs._loop:
				coords.append(coords[0])
			cs._map = coords
			strings.append(cs)

		dim = int(re.search(r"DIM=(\d*)", data[1]).group(1))
		print("Read in {} strings from data file of dim={}.".format(len(strings), dim))
		return strings, dim

	@staticmethod
	def save_processed_data(data: dict):
		output = "\n"
		list_to_fmt = lambda i: ",".join([j for j in str(i)[1:-1].split(", ")])
		for key, item in data.items():
			x = list_to_fmt(item[0])
			y = list_to_fmt(item[1])
			if len(item) == 3:
				yerr = list_to_fmt(item[2])
				line = "**{}*{}*{}*{}".format(key, x, y, yerr)
			else:
				line = "**{}*{}*{}".format(key, x, y)
			output += line
		fname = "_proc.".join(os.path.split(os.environ["DATA_FILE"])[-1].split("."))
		with open(os.path.join(
				os.environ["PROC_SAVE_PATH"], fname), 
			'a+') as f:
			f.write(output)

	@staticmethod
	def load_processed_data(file_path):
		retdata = {}
		str_to_list = lambda s: [float(i) for i in s.split(",")]
		with open(file_path, 'r') as f:
			data = f.read().split("\n")
		values = [i for i in data[-1].split("**") if i is not '']
		for i in values:
			i = i.split("*")
			key = i[0]
			vals = [str_to_list(i[1]), str_to_list(i[2])]	#x, y
			try:
				yerr = i[3]
			except:
				pass
			else:
				vals.append(str_to_list(yerr))
			retdata[key] = vals
		return retdata




