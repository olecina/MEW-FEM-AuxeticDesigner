import sys
from abaqus import *
from abaqusConstants import *
from auxetic_FEM import hcell, sreg, sinv, stri


design, a, b, d, xr, yr, zr, id = sys.argv[-8:]
a, b, d = map(float, [a, b, d])
xr = int(xr)
yr = int(yr)
zr = int(zr)

Mdb()

if design == "HCELL":
	design_func = hcell
if design == "SREG":
	design_func = sreg
if design == "SINV":
	design_func = sinv
if design == "STRI":
	design_func = stri

design_func(a, b, d, xr, yr, zr, id)

