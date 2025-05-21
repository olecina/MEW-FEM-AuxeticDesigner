import sys
import os
import math
from Strategy.print_transformation import PrintTransformation


def hcell(a, b, cts, xr, yr, zr, id):
	a = a / 1000
	b = b / 1000
	xr = 2 * xr
	yr = 2 * yr

	x_pore_size = 4 * a + 2 * b
	y_pore_size = 4 * a + 2 * b

	total_x = x_pore_size * xr
	total_y = y_pore_size * yr

	x_sep = b
	y_sep = 4 * a + b

	filename = f'hcell_{id}.gcode'

	def stabilization_lines(f, wx, ystep=0.3, speed=cts, n=5):
		f.write('; Stabilization lines\n')
		for i in range(n):
			f.write(f'G0 X{wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n')
			f.write(f'G0 X{-wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n\n')
		f.write(f'G0 Y{2 * ystep} F{speed}\n\n')

	with open(filename, 'w') as f:
		f.write(f'; h_cell design\n')
		f.write(f'; start gcode\n')
		f.write(f'; Relative positioning\n')
		f.write(f'G91\n; start at bottom-left corner\nG0 X0 Y0\n\n')

		stabilization_ystep = 0.3
		stabilization_n = 5

		def new_speed(CTS, layer):
			assert layer >= 0, 'layer must be >= 0'
			if layer <= 15:
				decreased_speed = 0.015 * layer * CTS
			else:
				decreased_speed = 0.02 * layer * CTS
			return CTS - decreased_speed

		stabilization_lines(f, total_x, ystep=0.3, speed=cts, n=5)
		for l in range(zr):
			f.write(f"\n; START layer {l + 1}/{zr}\n")
			last_j = yr - 1
			f.write(f'; START Printing horizontally\n')
			speed = new_speed(cts, l)
			for j in range(yr):
				for i in range(xr):
					f.write(f'G1 X{2 * a + b} F{speed}\n')
					f.write(f'G1 Y{- 2 * a} F{speed}\n')
					f.write(f'G1 X{2 * a + b} F{speed}\n')
					f.write(f'G1 Y{2 * a} F{speed}\n')
				f.write(f'G1 X{2 * a + b} F{speed}\n')
				f.write(f'G1 Y{b} F{speed}\n')
				for i in range(xr):
					f.write(f'G1 X{- 2 * a - b} F{speed}\n')
					f.write(f'G1 Y{2 * a} F{speed}\n')
					f.write(f'G1 X{- 2 * a - b} F{speed}\n')
					f.write(f'G1 Y{- 2 * a} F{speed}\n')
				f.write(f'G1 X{- 2 * a - b} F{speed}\n')
				f.write(f'G1 Y{y_sep} F{speed}\n')
				if j == last_j:
					f.write(f'G1 X{a + b} F{speed}\n')
					f.write(f'G1 Y{- a} F{speed}\n')
			f.write(f'; END Printing horizontally\n')
			last_i = xr - 1
			f.write(f'; START Printing vertically\n')
			f.write(f'G1 Y{- 2 * a - b} F{speed}\n')
			for i in range(xr):
				for j in range(yr):
					f.write(f'G1 X{2 * a} F{speed}\n')
					f.write(f'G1 Y{- 2 * a - b} F{speed}\n')
					f.write(f'G1 X{- 2 * a} F{speed}\n')
					f.write(f'G1 Y{- 2 * a - b} F{speed}\n')
				f.write(f'G1 X{4 * a + b} F{speed}\n')
				for j in range(yr):
					f.write(f'G1 Y{2 * a + b} F{speed}\n')
					f.write(f'G1 X{- 2 * a} F{speed}\n')
					f.write(f'G1 Y{2 * a + b} F{speed}\n')
					f.write(f'G1 X{2 * a} F{speed}\n')
				f.write(f'G1 Y{2 * a + b} F{speed}\n')
				f.write(f'G1 X{b} F{speed}\n')
				f.write(f'G1 Y{- 2 * a - b} F{speed}\n')
				if i == last_i:
					f.write(f'G1 X{a} F{speed}\n')
					f.write(f'G1 Y{- total_y} F{speed}\n')
					f.write(f'G1 X{- total_x} F{speed}\n')
					f.write(f'G1 X{- 2 * a - b} F{speed}\n')
					if l < zr - 1:
						f.write(f'G1 Y{3 * a + b} F{speed}\n')
					else:
						f.write(f'G1 Y{-2 * stabilization_ystep * stabilization_n + 0.1} F{speed}\n')
		f.write(f'G90\n')
		f.write(f'M42 P0 S0\n')
		f.write(f'G0 Z10\n')
		f.write(f'; end gcode\n')


def sreg(a, b, cts, xr, yr, zr, id):
	a = a / 1000
	b = b / 1000
	xr = 2 * xr
	yr = 2 * yr

	pore_size = 4 * a

	uturn_length = 6 * a
	uturn_radius = 4 * a

	total_x = pore_size * xr

	filename = f'sreg_{id}.gcode'

	def stabilization_lines(f, wx, ystep=0.3, speed=cts, n=5):
		f.write('; Stabilization lines\n')
		for i in range(n):
			f.write(f'G0 X{wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n')
			f.write(f'G0 X{-wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n\n')
		f.write(f'G0 Y{2 * ystep} F{speed}\n\n')

	with open(filename, 'w') as f:
		f.write(f'; sreg design\n')
		f.write(f'; start gcode\n')
		f.write(f'; Relative positioning\n')
		f.write(f'G91\n; start at bottom-left corner\nG0 X0 Y0\n\n')

		stabilization_ystep = 0.3
		stabilization_n = 5

		def new_speed(CTS, layer):
			assert layer >= 0, 'layer must be >= 0'
			if layer <= 15:
				decreased_speed = 0.015 * layer * CTS
			else:
				decreased_speed = 0.02 * layer * CTS
			return CTS - decreased_speed

		stabilization_lines(f, total_x, ystep=0.3, speed=cts, n=5)
		for l in range(zr):
			f.write(f"\n; START layer {l + 1}/{zr}\n")
			last_j = round(yr / 2) - 1
			f.write(f'; START Printing horizontally\n')
			speed = new_speed(cts, l)
			for j in range(round(yr / 2)):
				for i in range(xr):
					f.write(f'G1 X{a} Y{-b} F{speed}\n')
					f.write(f'G1 X{a} Y{b} F{speed}\n')
					f.write(f'G1 X{a} Y{b} F{speed}\n')
					f.write(f'G1 X{a} Y{-b} F{speed}\n')
				f.write(f'G1 X{uturn_length} F{speed}\n')
				f.write(f'G3 Y{pore_size} I{uturn_radius} J{pore_size/2} F{speed}\n')
				f.write(f'G1 X{-uturn_length} F{speed}\n')
				for i in range(xr):
					f.write(f'G1 X{-a} Y{b} F{speed}\n')
					f.write(f'G1 X{-a} Y{-b} F{speed}\n')
					f.write(f'G1 X{-a} Y{-b} F{speed}\n')
					f.write(f'G1 X{-a} Y{b} F{speed}\n')
				f.write(f'G1 X{-uturn_length} F{speed}\n')
				f.write(f'G2 Y{pore_size} I{-uturn_radius} J{pore_size / 2} F{speed}\n')
				f.write(f'G1 X{uturn_length} F{speed}\n')
				if j == last_j:
					for i in range(xr):
						f.write(f'G1 X{a} Y{-b} F{speed}\n')
						f.write(f'G1 X{a} Y{b} F{speed}\n')
						f.write(f'G1 X{a} Y{b} F{speed}\n')
						f.write(f'G1 X{a} Y{-b} F{speed}\n')
			f.write(f'; END Printing horizontally\n')
			f.write(f'G1 X{uturn_length} F{speed}\n')
			f.write(f'G1 Y{uturn_length} F{speed}\n')
			f.write(f'G1 X{-uturn_length} F{speed}\n')
			f.write(f'G1 Y{-uturn_length} F{speed}\n')
			f.write(f'; START Printing vertically\n')
			last_i = round(xr / 2) - 1
			for i in range(round(xr / 2)):
				for j in range(round(yr)):
					f.write(f'G1 X{-b} Y{-a} F{speed}\n')
					f.write(f'G1 X{b} Y{-a} F{speed}\n')
					f.write(f'G1 X{b} Y{-a} F{speed}\n')
					f.write(f'G1 X{-b} Y{-a} F{speed}\n')
				f.write(f'G1 Y{-uturn_length} F{speed}\n')
				f.write(f'G2 X{-pore_size} I{-pore_size / 2} J{-uturn_radius} F{speed}\n')
				f.write(f'G1 Y{uturn_length} F{speed}\n')
				for j in range(round(yr)):
					f.write(f'G1 X{b} Y{a} F{speed}\n')
					f.write(f'G1 X{-b} Y{a} F{speed}\n')
					f.write(f'G1 X{-b} Y{a} F{speed}\n')
					f.write(f'G1 X{b} Y{a} F{speed}\n')
				f.write(f'G1 Y{uturn_length} F{speed}\n')
				f.write(f'G3 X{-pore_size} I{-pore_size / 2} J{uturn_radius} F{speed}\n')
				f.write(f'G1 Y{-uturn_length} F{speed}\n')
				if i == last_i:
					for j in range(round(yr)):
						f.write(f'G1 X{-b} Y{-a} F{speed}\n')
						f.write(f'G1 X{b} Y{-a} F{speed}\n')
						f.write(f'G1 X{b} Y{-a} F{speed}\n')
						f.write(f'G1 X{-b} Y{-a} F{speed}\n')
					f.write(f'G1 Y{-uturn_length}\n')
					f.write(f'G1 X{-uturn_length}\n')
					f.write(f'G1 Y{uturn_length}\n')
					f.write(f'G1 X{uturn_length}\n')
		f.write(f'G0 Y-3.6 X-3 F{speed}\n')
		f.write(f'G90\n\n')
		f.write(f'M42 P0 S0\n')
		f.write(f'G0 Z10\n')
		f.write(f'; end gcode\n')


def sinv(a, b, cts, xr, yr, zr, id):
	a = a / 1000
	b = b / 1000
	xr = 4 * xr
	yr = 4 * yr

	pore_size = 2 * a

	uturn_length = 4 * a
	uturn_radius = 2 * a

	total_x = pore_size * xr
	total_y = pore_size * yr

	filename = f'sinv_{id}.gcode'

	def stabilization_lines(f, wx, ystep=0.3, speed=cts, n=5):
		f.write('; Stabilization lines\n')
		for i in range(n):
			f.write(f'G0 X{wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n')
			f.write(f'G0 X{-wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n\n')
		f.write(f'G0 Y{2 * ystep} F{speed}\n\n')

	with open(filename, 'w') as f:
		f.write(f'; sinv design\n')
		f.write(f'; start gcode\n')
		f.write(f'; Relative positioning\n')
		f.write(f'G91\n; start at bottom-left corner\nG0 X0 Y0\n\n')

		stabilization_ystep = 0.3
		stabilization_n = 5

		def new_speed(CTS, layer):
			assert layer >= 0, 'layer must be >= 0'
			if layer <= 15:
				decreased_speed = 0.015 * layer * CTS
			else:
				decreased_speed = 0.02 * layer * CTS
			return CTS - decreased_speed

		stabilization_lines(f, total_x, ystep=0.3, speed=cts, n=5)
		for l in range(zr):
			f.write(f"\n; START layer {l + 1}/{zr}\n")
			speed = new_speed(cts, l)
			last_j = round(yr / 2) - 1
			f.write(f'; START Printing horizontally\n')
			for j in range(round(yr / 2)):
				for i in range(round(xr / 2)):
					f.write(f'G1 X{a} Y{-b:.6f} F{speed}\n')
					f.write(f'G1 X{a} Y{b:.6f} F{speed}\n')
					f.write(f'G1 X{a} Y{b:.6f} F{speed}\n')
					f.write(f'G1 X{a} Y{-b:.6f} F{speed}\n')
				f.write(f'G1 X{uturn_length} F{speed}\n')
				f.write(f'G3 Y{pore_size} I{uturn_radius} J{pore_size / 2} F{speed}\n')
				f.write(f'G1 X{-uturn_length} F{speed}\n')
				for i in range(round(xr / 2)):
					f.write(f'G1 X{-a} Y{-b:.6f} F{speed}\n')
					f.write(f'G1 X{-a} Y{b:.6f} F{speed}\n')
					f.write(f'G1 X{-a} Y{b:.6f} F{speed}\n')
					f.write(f'G1 X{-a} Y{-b:.6f} F{speed}\n')
				f.write(f'G1 X{-uturn_length} F{speed}\n')
				f.write(f'G2 Y{pore_size} I{-uturn_radius} J{pore_size / 2} F{speed}\n')
				f.write(f'G1 X{uturn_length} F{speed}\n')
				if j == last_j:
					for i in range(round(xr / 2)):
						f.write(f'G1 X{a} Y{-b:.6f} F{speed}\n')
						f.write(f'G1 X{a} Y{b:.6f} F{speed}\n')
						f.write(f'G1 X{a} Y{b:.6f} F{speed}\n')
						f.write(f'G1 X{a} Y{-b:.6f} F{speed}\n')
			f.write(f'; END Printing horizontally\n')
			f.write(f'G1 X{uturn_length} F{speed}\n')
			f.write(f'G1 Y{uturn_length} F{speed}\n')
			f.write(f'G1 X{-uturn_length} F{speed}\n')
			f.write(f'G1 Y{-uturn_length} F{speed}\n')
			f.write(f'; START Printing vertically\n')
			last_i = round(xr / 2) - 1
			for i in range(round(xr / 2)):
				for j in range(round(yr / 2)):
					f.write(f'G1 X{-b:.6f} Y{-a} F{speed}\n')
					f.write(f'G1 X{b:.6f} Y{-a} F{speed}\n')
					f.write(f'G1 X{b:.6f} Y{-a} F{speed}\n')
					f.write(f'G1 X{-b:.6f} Y{-a} F{speed}\n')
				f.write(f'G1 Y{-uturn_length} F{speed}\n')
				f.write(f'G2 X{-pore_size} I{-pore_size / 2} J{-uturn_radius} F{speed}\n')
				f.write(f'G1 Y{uturn_length} F{speed}\n')
				for j in range(round(yr / 2)):
					f.write(f'G1 X{-b:.6f} Y{a} F{speed}\n')
					f.write(f'G1 X{b:.6f} Y{a} F{speed}\n')
					f.write(f'G1 X{b:.6f} Y{a} F{speed}\n')
					f.write(f'G1 X{-b:.6f} Y{a} F{speed}\n')
				f.write(f'G1 Y{uturn_length} F{speed}\n')
				f.write(f'G3 X{-pore_size} I{-pore_size / 2} J{uturn_radius} F{speed}\n')
				f.write(f'G1 Y{-uturn_length} F{speed}\n')
				if i == last_i:
					for j in range(round(yr / 2)):
						f.write(f'G1 X{-b:.6f} Y{-a} F{speed}\n')
						f.write(f'G1 X{b:.6f} Y{-a} F{speed}\n')
						f.write(f'G1 X{b:.6f} Y{-a} F{speed}\n')
						f.write(f'G1 X{-b:.6f} Y{-a} F{speed}\n')
					f.write(f'G1 Y{-uturn_length}\n')
					f.write(f'G1 X{-uturn_length}\n')
					f.write(f'G1 Y{uturn_length}\n')
					f.write(f'G1 X{uturn_length}\n')
		f.write(f'G0 Y-3.6 X-3 F{speed}\n')
		f.write(f'G90\n\n')
		f.write(f'M42 P0 S0\n')
		f.write(f'G0 Z10\n')
		f.write(f'; end gcode\n')


def stri(a, b, cts, xr, yr, zr, id):
	# Import PrintStrategy
	sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

	a = a / 1000
	b = b / 1000
	xr = 2 * xr
	yr = 2 * yr

	zero_degrees_length = 8 * a
	sixty_dg_length = 12 * a

	triangle_side = 4 * a
	sin = lambda deg: math.sin(math.radians(deg))
	cos = lambda deg: math.cos(math.radians(deg))
	triangle_dx = cos(60) * triangle_side
	triangle_dy = sin(60) * triangle_side

	if yr % 2 == 0:
		odd_Y = False  # Y_repetitions is an even number
	else:
		odd_Y = True  # Y_repetitions is an odd number

	if xr % 2 == 0:
		odd_X = False  # X_repetitions is an even number
	else:
		odd_X = True  # X_repetitions is an odd number

	if int(yr / 2) % 2 == 0:
		odd_y = False  # half of Y_repetitions is an even number
	else:
		odd_y = True  # half of Y_repetitions is an odd number

	xy_ratio = xr / int(yr / 2)  # 1 if X=Y / <1 if X<Y / >1 if X>Y

	total_x = triangle_side * xr

	filename = f'stri_{id}.gcode'

	def zero_degrees_printing(b=b, speed=cts):
		f.write(f'; START Printing horizontally\n')
		index_j = int(yr / 2) + 1 if odd_Y else int(yr / 2)
		for j in range(index_j):
			for i in range(xr):
				f.write(f'G1 X{a} Y{-b} F{speed}\n')
				f.write(f'G1 X{a} Y{b} F{speed}\n')
				f.write(f'G1 X{a} Y{b} F{speed}\n')
				f.write(f'G1 X{a} Y{-b} F{speed}\n')
			f.write(f'G0 X{zero_degrees_length} F{speed}\n')
			f.write(f'G0 Y{triangle_dy} F{speed}\n')
			f.write(f'G0 X{-zero_degrees_length + triangle_dx} F{speed}\n')
			for i in range(xr):
				f.write(f'G1 X{-a} Y{b} F{speed}\n')
				f.write(f'G1 X{-a} Y{-b} F{speed}\n')
				f.write(f'G1 X{-a} Y{-b} F{speed}\n')
				f.write(f'G1 X{-a} Y{b} F{speed}\n')
			f.write(f'G0 X{-zero_degrees_length - triangle_dx} F{speed}\n')
			f.write(f'G0 Y{triangle_dy} F{speed}\n')
			f.write(f'G0 X{zero_degrees_length} F{speed}\n')
		if odd_Y:
			f.write(f'G0 X{triangle_side * (xr - 1)} F{speed}\n')
			f.write(f'G0 X{triangle_dx} Y{-triangle_dy} F{speed}\n')
		else:
			for i in range(xr):
				f.write(f'G1 X{a} Y{-b} F{speed}\n')
				f.write(f'G1 X{a} Y{b} F{speed}\n')
				f.write(f'G1 X{a} Y{b} F{speed}\n')
				f.write(f'G1 X{a} Y{-b} F{speed}\n')
		f.write(f'; END Printing horizontally\n')

	def relocate_A(speed=cts):
		f.write(f'; move to top-left corner\n')
		f.write(f'G0 X{- zero_degrees_length} F{speed}\n')
		f.write(f'G0 Y{triangle_dy * (yr + 1)} F{speed}\n')
		if odd_Y:
			f.write(f'G0 X{zero_degrees_length + triangle_side} F{speed}\n')
		else:
			f.write(f'G0 X{zero_degrees_length + triangle_side + triangle_dx} F{speed}\n')
		f.write(f'G0 X{-triangle_dx} Y{-triangle_dy} F{speed}\n')

	def relocate_B(sign, speed=cts):
		f.write(f'; move to bottom-left corner\n')
		if sign < 0:
			f.write(f'G0 Y{- zero_degrees_length} F{speed}\n')
			f.write(f'G0 X{- triangle_side * xr - zero_degrees_length} F{speed}\n')
			f.write(f'G0 Y{zero_degrees_length} F{speed}\n')
			f.write(f'G0 X{zero_degrees_length} F{speed}\n')
		else:
			f.write(f'G0 X{zero_degrees_length} F{speed}\n')
			f.write(f'G0 Y{- zero_degrees_length} F{speed}\n')
			f.write(f'G0 X{- triangle_side * xr - 2 * zero_degrees_length - triangle_dx} F{speed}\n')
			f.write(f'G0 Y{zero_degrees_length - triangle_dy} F{speed}\n')
			f.write(f'G0 X{zero_degrees_length} F{speed}\n')

	def sixty_degrees_printing_A(b, speed=cts):
		f.write(f'; START Printing -60deg\n')
		t = PrintTransformation(f)
		t.set_rotate_angle(-60)

		def extra_lines(case):
			if case == '':
				f.write('; ERROR\n')
			else:
				f.write(f'; extra line {case}\n')
				if case == 'up':
					x = sign * -sixty_dg_length + sign * triangle_dx
				if case == 'right':
					x = sign * -sixty_dg_length + sign * triangle_dx + sign * triangle_side
				if case == 'up_corner':
					x = sign * -sixty_dg_length + sign * triangle_dx - sign * triangle_side
				if case == 'bottom_corner':
					x = sign * -sixty_dg_length + sign * triangle_dx
				if case == 'left':
					x = sign * -sixty_dg_length + sign * triangle_dx - 2 * sign * triangle_side
				if case == 'bottom':
					x = sign * -sixty_dg_length + sign * triangle_dx - sign * triangle_side
				t.write(f'G0 X{x} F{speed}\n')

		total_i = int(yr / 2) + xr
		last_i = total_i

		diagonal_length = 2 * xr + 1 if xy_ratio < 1 else yr

		loop_range = range(1, total_i + 1)

		for i in loop_range:
			f.write(f'; Printing -60deg lines: {i}/{total_i}\n')

			sign = -1 if i % 2 == 0 else 1

			if odd_Y:
				start_limit = 2 * i
			else:
				start_limit = 2 * i - 1

			end_limit = int(yr / 2) if xy_ratio >= 1 else xr

			inner_step = start_limit if start_limit < diagonal_length else diagonal_length

			if i > last_i - end_limit:
				if diagonal_length % 2 == 0:
					inner_step -= 2 * (i - (last_i - end_limit) - 1)
				else:
					inner_step -= 2 * (i - (last_i - end_limit)) - 1

			f.write(f'; inner step: {inner_step}\n')
			for j in range(inner_step):
				t.write(f'G1 X{sign * a} Y{sign * -b} F{speed}\n')
				t.write(f'G1 X{sign * a} Y{sign * b} F{speed}\n')
				t.write(f'G1 X{sign * a} Y{sign * b} F{speed}\n')
				t.write(f'G1 X{sign * a} Y{sign * -b} F{speed}\n')

			# Print extra-scaffold lines
			t.write(f'G0 X{sign * sixty_dg_length } F{speed}\n')

			offset_factor = 13 / 15
			t.write(f'G0 Y{- 4 * a * offset_factor} F{speed}\n')

			if i % 2 == 0:
				odd_i = False
			else:
				odd_i = True

			case = ''

			if xy_ratio < 1:
				if i < xr and i < int(yr / 2):
					case = 'right' if odd_i else 'up'
				elif i == xr:
					if odd_X:
						case = 'right'
					else:
						case = 'up_corner' if odd_Y else 'up'
				elif xr < i < int(yr / 2):
					case = 'right' if odd_i else 'left'
				elif i == int(yr / 2):
					case = 'bottom_corner' if odd_y else 'left'
				else:
					case = 'bottom' if odd_i else 'left'

			else:  # xy_ratio >= 1:
				if i < xr and i < int(yr / 2):
					case = 'right' if odd_i else 'up'
				elif i == int(yr / 2):
					case = 'up'
				elif int(yr / 2) < i < xr:
					case = 'bottom' if odd_i else 'up'
				elif i == xr:
					if odd_X:
						case = 'bottom'
					else:
						case = 'up_corner' if odd_Y else 'up'
				else:
					case = 'bottom' if odd_i else 'left'

			extra_lines(case)

		# [End] print extra-scaffold lines
		f.write(f'; END Printing -60deg\n\n')

	def sixty_degrees_printing_B(b, speed=cts):
		f.write(f'; START Printing +60deg\n')
		t = PrintTransformation(f)
		t.set_rotate_angle(60)

		def extra_lines(case):
			if case == '':
				f.write('; ERROR\n')
			else:
				f.write(f'; extra line {case}\n')
				if case == 'up':
					x = sign * -sixty_dg_length + sign * triangle_dx
				if case == 'right':
					x = sign * -sixty_dg_length + sign * triangle_dx - 2 * sign * triangle_side
				if case == 'up_corner':
					x = sign * -sixty_dg_length + sign * triangle_dx - sign * triangle_side
				if case == 'bottom_corner':
					x = sign * -sixty_dg_length + sign * triangle_dx
				if case == 'left':
					x = sign * -sixty_dg_length + sign * triangle_dx + sign * triangle_side
				if case == 'bottom':
					x = sign * -sixty_dg_length + sign * triangle_dx - sign * triangle_side
				t.write(f'G0 X{x} F{speed}\n')

		total_i = int(yr / 2) + xr if not odd_Y else int(yr / 2) + xr + 1
		last_i = total_i

		diagonal_length = 2 * xr + 1 if xy_ratio < 1 else yr

		loop_range = range(1, total_i + 1)

		for i in loop_range:
			f.write(f'; Printing +60deg lines: {i}/{total_i}\n')

			sign = 1 if i % 2 == 0 else -1

			if odd_Y:
				start_limit = 2 * i - 1
			else:
				start_limit = 2 * i

			end_limit = int(yr / 2) if xy_ratio >= 1 else xr

			inner_step = start_limit if start_limit < diagonal_length else diagonal_length

			if i > last_i - end_limit:
				if diagonal_length % 2 == 0:
					inner_step -= 2 * (i - (last_i - end_limit)) - 1
				else:
					inner_step -= 2 * (i - (last_i - end_limit))

			f.write(f'; inner step: {inner_step}\n')
			for j in range(inner_step):
				t.write(f'G1 X{sign * a} Y{sign * -b} F{speed}\n')
				t.write(f'G1 X{sign * a} Y{sign * b} F{speed}\n')
				t.write(f'G1 X{sign * a} Y{sign * b} F{speed}\n')
				t.write(f'G1 X{sign * a} Y{sign * -b} F{speed}\n')

			# Print extra-scaffold lines
			offset_factor = 13 / 15
			if i != last_i:
				t.write(f'G0 X{sign * sixty_dg_length} F{speed}\n')
				t.write(f'G0 Y{- 4 * a * offset_factor} F{speed}\n')

			if i % 2 == 0:
				odd_i = False
			else:
				odd_i = True

			case = ''

			if xy_ratio < 1:
				if i < xr and i < int(yr / 2):
					case = 'left' if odd_i else 'up'
				elif i == xr:
					if odd_X:
						case = 'left'
					else:
						case = 'up' if odd_Y else 'up_corner'
				elif xr < i < int(yr / 2):
					case = 'left' if odd_i else 'right'
				elif i == int(yr / 2):
					if not odd_y:
						case = 'right'
					else:
						case = 'left' if odd_Y else 'bottom'
				else:
					case = 'bottom' if odd_i else 'right'

			else:  # elif xy_ratio >= 1:
				if i < xr and i < int(yr / 2):
					case = 'left' if odd_i else 'up'
				elif i == int(yr / 2):
					if odd_y:
						case = 'left' if odd_Y else 'bottom'
					else:
						case = 'up'
				elif int(yr / 2) < i < xr:
					case = 'bottom' if odd_i else 'up'
				elif i == xr:
					if odd_X:
						case = 'bottom'
					else:
						case = 'up' if odd_Y else 'up_corner'
				else:
					case = 'bottom' if odd_i else 'right'

			if i != last_i:
				extra_lines(case)
			else:
				relocate_B(sign)

	def stabilization_lines(f, wx, ystep=0.3, speed=cts, n=5):
		f.write('; Stabilization lines\n')
		for i in range(n):
			f.write(f'G0 X{wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n')
			f.write(f'G0 X{-wx} F{speed}\n')
			f.write(f'G0 Y{ystep} F{speed}\n\n')
		f.write(f'G0 Y{2 * ystep} F{speed}\n\n')

	with open(filename, 'w') as f:
		f.write(f'; stri design\n')
		f.write(f'; start gcode\n')
		f.write(f'; Relative positioning\n')
		f.write(f'G91\n; start at bottom-left corner\nG0 X0 Y0\n\n')

		stabilization_ystep = 0.3
		stabilization_n = 5

		def new_speed(CTS, layer):
			assert layer >= 0, 'layer must be >= 0'
			if layer <= 15:
				decreased_speed = 0.015 * layer * CTS
			else:
				decreased_speed = 0.02 * layer * CTS
			return CTS - decreased_speed

		stabilization_lines(f, total_x, ystep=0.3, speed=cts, n=5)
		for l in range(zr):
			f.write(f"\n; START layer {l + 1}/{zr}\n")
			speed = new_speed(cts, l)
			zero_degrees_printing(b, speed)
			sixty_degrees_printing_A(b, speed)
			relocate_A()
			sixty_degrees_printing_B(b, speed)
		f.write(f'G1 Y{-2 * stabilization_ystep * (stabilization_n + 1)} F{cts}\n')
		f.write(f'G90\n\n')
		f.write(f'M42 P0 S0\n')
		f.write(f'G0 Z10\n')
		f.write(f'; end gcode\n')
