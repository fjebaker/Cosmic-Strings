from cosmicstrings.io import StringIO
from cosmicstrings.classifiers import classify
import sys
import os

import matplotlib.pyplot as plt

os.environ["DATA_FILE"] = 'data/raw_5/20_normal_SU2_test.dat'
os.environ["PROC_SAVE_PATH"] = "data/proc/"

stringdat, dim = StringIO.load_strings()
c = classify(stringdat, dim)
c.calculate()
c.plotl2(startn=2, endn=20)
c.plotperimeter()
c.plotvol2surf()
c.plotperim2dens(maxp=30)
c.plotlength2dens(maxp=40)
c.save_data_to_file()
#l = classify()
#l.load_file_to_data("data/proc/10testproc.dat")
plt.show()