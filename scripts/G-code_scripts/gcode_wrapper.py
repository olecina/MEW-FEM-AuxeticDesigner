import sys
from auxetic_gcode import hcell, sreg, sinv, stri


design, a, b, d, xr, yr, zr, id = sys.argv[-8:]
a, b, d = map(float, [a, b, d])
xr = int(xr)
yr = int(yr)
zr = int(zr)

cts = 150  # modify this value as needed

if design == "HCELL":
	design_func = hcell
if design == "SREG":
	design_func = sreg
if design == "SINV":
	design_func = sinv
if design == "STRI":
	design_func = stri

design_func(a, b, cts, xr, yr, zr, id)


