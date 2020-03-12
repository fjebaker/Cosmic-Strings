import numpy as np
import scipy.odr as ODR
import matplotlib.pyplot as plt
import inspect

def _log_log_plot(x, y, title="", xlabel="", ylabel="", xerr=None, yerr=None):
	if all(i == 0 for i in yerr):
		yerr = None
	else:
		y = np.array(y)
		yerr = np.array(yerr)
		yerr = np.log10(np.abs(y)) / (y * np.log(10)) * yerr


	# PLOTTING CODE
	x = np.log10(x)
	y = np.log10(y)

	#yerr = np.log10(np.abs(y)) / (y * np.log(10)) * yerr

	plt.figure()

	label=""
	print("-"*50)
	if title is not "":
		print(title)
		plt.title(title)
	if yerr is not None or xerr is not None:
		yerr = np.array(yerr)
		yerr = 1./(y * np.log(10)) * yerr

		f = lambda B, x: B[0] * x + B[1]
		model = ODR.Model(f)

		# adapt
		xd = np.array(x)
		yd = np.array(y)
		ind = np.where(np.logical_and(np.greater_equal(xd, 0.602), np.less_equal(xd, 1.6)))
		xd = xd[ind]
		yd = yd[ind]
		yerrd=yerr[ind]

		data = ODR.RealData(xd, yd, sy=yerrd)
		odr = ODR.ODR(data, model, beta0 = [1, 1])
		out = odr.run()
		msd, csd = out.sd_beta
		m, c = out.beta.copy()
		print("m  = {0:.4} \t+/-   {2:.4}\nc  = {1:.4} \t+/-   {3:.4}".format(m, c, msd, csd))
		d = 1/float(m)
		A = 10**(-c*d)
		sd = m**(-1) * msd
		print("d  = {0:.4} \t+/-   {1:.4}".format(d, sd))
		print("A  = {0:.4} \t+/-   {1:.4}\t(inverse rel)".format(A, A**2 * np.sqrt(c**2 * sd**2 + d**2 * csd**2)))
		print("A2 = {0:.4} \t+/-   {1:.4}\t(normal rel)".format(10**c, A**2 * csd))
		plt.errorbar(x, y, ms=3, fmt='x', yerr=yerr, capsize=3, c='k', lw=1, alpha=.8)

		#label = "m={0:.2f}, c={1:.2f}".format(m, c, A, d)

	else:
		m, c = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
		print("m = {0:.4}, c = {1:.4}".format(m, 10**c))
		d = 1/float(m)
		A = 10**(-c/float(m))
		print("d = {0:.4}".format(d))
		print("A = {0:.4}".format(A))
		plt.scatter(x, y, s=3, marker='x')
		#label = "m={0:.2f}, c={1:.2f}".format(m, c)

	print("-"*50)

	if xlabel is not "":
		plt.xlabel(xlabel)
	if ylabel is not "":
		plt.ylabel(ylabel)
	plt.plot(x, m*x + c, 'r', label=label, lw=1)
	plt.grid()
	#plt.legend()

def histogram(x1, y1, yerr1, x2, y2, yerr2, bins=10):
	plt.figure()
	ax = plt.gca()
	ax.set_xscale('log')
	ax.set_yscale('log')
	plt.grid()
	limx = (min(x1+x2)/1.3, max(x1+x2)*1.1)
	limy = (min(y1+y2)/1.3, max(y1+y2)*1.1)
	ax.set_xlim(limx)
	ax.set_ylim(limy)
	plt.errorbar(x1, y1, ms=4, fmt='x', yerr=yerr1, alpha=0.5, capsize=3, c='r', lw=1, label='open')
	plt.errorbar(x2, y2, ms=4, fmt='o', yerr=yerr2, alpha=0.5, capsize=3, c='b', lw=1, label='closed')
	#plt.scatter(x1, y1, s=4, marker='x', alpha=0.8, c='r', label='open')
	#plt.scatter(x2, y2, s=4, marker='o', alpha=0.8, c='b', label='closed')
	plt.title("String count for a given length")
	plt.xlabel(r"Length $l$")
	plt.ylabel(r"String count")
	plt.legend()


class MPlot:
	def __init__(self, pmerger):
		self.pm = pmerger
		self.hist_data = None
	
	def plotl2(self, *a, startn, endn):
		x, dat = self.pm.retrieve(str(inspect.stack()[0][3]))
		y, yerr = dat
		_log_log_plot(x[startn:endn], y[startn:endn], r"Length $l$ vs. Displacement $R$", "Log (segment length)", "Log (end to end dist)", yerr=yerr[startn:endn])

	def plotperimeter(self, *a, **kw):
		x, dat = self.pm.retrieve(str(inspect.stack()[0][3]))
		y, yerr = dat
		_log_log_plot(x, y, r"Loop perimeter $P$ vs length $l$", "Log (loop perimeter)", "Log (length)", yerr=yerr)

	def plotvol2surf(self, *a, **kw):
		x, dat = self.pm.retrieve(str(inspect.stack()[0][3]))
		y, yerr = dat
		_log_log_plot(x, y, r"Loop perimeter $P$ vs $V/S$", "Log (loop perimeter)", r"Log (loop $V/S$)", yerr=yerr)

	def plotperim2dens(self, *a, **kw):
		x, dat = self.pm.retrieve(str(inspect.stack()[0][3]))
		y, yerr = dat
		_log_log_plot(x, y, r"Loop perimeter $P$ vs density $n$", "Log (loop perimeter)", "Log (loop density)", yerr=yerr)

	def plotlength2dens(self, *a, **kw):
		x, dat = self.pm.retrieve(str(inspect.stack()[0][3]))
		y, yerr = dat
		_log_log_plot(x, y, r"Loop length $l$ vs density $n$", "Log (loop length)", "Log (density)", yerr=yerr)

	def lhist_lines(self, *a, **kw):
		x1, dat1 = self.pm.retrieve("lhist_lines")
		y1, yerr1 = dat1
		x2, dat2 = self.pm.retrieve("lhist_loops")
		y2, yerr2 = dat2
		histogram(x1, y1, yerr1, x2, y2, yerr2)

	def lhist_loops(self):
	 	pass


	