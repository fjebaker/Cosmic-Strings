import numpy as np
import scipy.odr as ODR
import matplotlib.pyplot as plt

def _log_log_plot(x, y, title="", xlabel="", ylabel="", xerr=None, yerr=None):
	if all(i == 0 for i in yerr):
		yerr = None

	# PLOTTING CODE
	x = np.log10(x)
	y = np.log10(y)

	plt.figure()

	if title is not "":
		print("Title = '{}'".format(title))
		plt.title(title)

	if yerr is not None or xerr is not None:
		yerr = np.array(yerr)
		yerr = 1./(y * np.log(10)) * yerr

		f = lambda B, x: B[0] * x + B[1]
		model = ODR.Model(f)
		data = ODR.RealData(x, y, sy=yerr)
		odr = ODR.ODR(data, model, beta0 = [.1, .1])
		out = odr.run()
		msd, csd = out.sd_beta
		m, c = out.beta.copy()
		print("m = {0:.5} err {2:.5}\nc = {1:.5} err {3:.5}".format(m, c, msd, csd))
		d = 1/float(m)
		A = 10**(-c/float(m))
		print("d = {0:.5} err {1:.5}".format(d, m**(-2) * msd))
		print("A = {0:.5}".format(A))
		#plt.errorbar(x, y, ms=3, fmt='x', yerr=yerr, capsize=3, c='r')
		plt.scatter(x, y, s=3, marker='x')

	else:
		m, c = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
		print("m = {0:.5}, c = {1:.5}".format(m, 10**c))
		d = 1/float(m)
		A = 10**(-c/float(m))
		print("d = {0:.5}".format(d))
		print("A = {0:.5}".format(A))
		plt.scatter(x, y, s=3, marker='x')

	if xlabel is not "":
		plt.xlabel(xlabel)
	if ylabel is not "":
		plt.ylabel(ylabel)
	plt.plot(x, m*x + c, 'r', label="m={0:.2f}, d=1/m={1:.2f}".format(m, d), lw=1)
	plt.legend()