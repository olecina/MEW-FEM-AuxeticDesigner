import math

sin = lambda deg : math.sin(math.radians(deg))
cos = lambda deg : math.cos(math.radians(deg))

class PrintTransformation:

  ROTATIONAL_AXIS_NAME = 'U'
  rename_axis_list = []
  base_angle = 0 # [degree]

  def __init__(self, file):
    self.file = file

  def swapxy(self, enable:bool):
    # axis = 0: Y
    # axis = 1: X
    swap_list = [('X', 'W'), ('Y', 'X'), ('W', 'Y')]
    if enable:
      self.rename_axis_list.extend(swap_list)
    else:
      for pair in swap_list:
        if self.rename_axis_list.count(pair):
          self.rename_axis_list.remove(pair)

  def set_rotational_axis(self, axis:str):
    if axis == 'X' or axis == 'Y':
      self.rename_axis_list.append((axis, self.ROTATIONAL_AXIS_NAME))
    else:
      ValueError('Invalid axis')

  def set_rotate_angle(self, deg):
    self.base_angle = deg

  def rotate(self, x=0, y=0):
    x = float(x) if x else 0.0
    y = float(y) if y else 0.0
    x_new = x * cos(self.base_angle) - y * sin(self.base_angle)
    y_new = x * sin(self.base_angle) + y * cos(self.base_angle)
    return x_new, y_new
  
  def write(self, code):
    code = code.strip()
    # parse x and y position
    splited_code = code.split(' ')
    if len(splited_code) >= 2 and splited_code[0][0] == 'G':
      x = None
      y = None
      circle_i = None
      circle_j = None
      speed = None
      for i in range(1, len(splited_code)):
        prefix = splited_code[i][0].upper()
        val = float(splited_code[i][1:])
        if prefix == 'X':
          x = val
        elif prefix == 'Y':
          y = val
        elif prefix == 'F':
          speed = val
        elif prefix == 'I':
          circle_i = val
        elif prefix == 'J':
          circle_j = val
      x, y = self.rotate(x, y)
      if circle_i or circle_j:
        circle_i, circle_j = self.rotate(circle_i, circle_j)
        code = f'{splited_code[0]} X{x:.3f} Y{y:.3f} I{circle_i:.3f} J{circle_j:.3f}'
      else:
        code = f'{splited_code[0]} X{x} Y{y}'
      
      if speed:
        code += f' F{speed:.2f}'
    # transform the axis
    for rename_pair in self.rename_axis_list:
      assert len(rename_pair) >= 2
      code = code.replace(rename_pair[0], rename_pair[1])
    
    self.file.write(code+'\n')

  def __str__(self):
    return "PrintTransformation()"
