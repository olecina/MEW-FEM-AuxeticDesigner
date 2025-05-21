import math

class PrintingStrategy():
  #***** Printing strategies ******
  STRATEGY_NONE = 1
  STRATEGY_PAUSE = 2
  STRATEGY_UTURN = 3
  STRATEGY_CLOVERLEAF = 4
  STRATEGY_CLOVERLEAF2 = 5

  # current position and speed
  strategy = STRATEGY_NONE
  prev_dx = 0 # [mm]
  prev_dy = 0 # [mm]
  default_speed = 0 # [mm/min]

  pause_msec = 0 # [msec]
  uturn_length = 0 # [mm]
  uturn_speed = 0 # [mm/min]
  cloverleaf_radius = 0 # [mm]
  cloverleaf_speed = 0 # [mm/min]

  def __init__(self, file):
    self.file = file

  def set_pause(self, msec):
    if msec > 1e-9:
      self.pause_msec = msec
      self.strategy = self.STRATEGY_PAUSE

  def set_uturn(self, length, uturn_speed=None):
    if length > 1e-9:
      self.uturn_length = length
      self.strategy = self.STRATEGY_UTURN
      if uturn_speed:
        self.uturn_speed = uturn_speed

  def set_cloverleaf_radius(self, radius, cloverleaf_speed=None):
    if radius > 1e-9:
      self.cloverleaf_radius = radius
      self.strategy = self.STRATEGY_CLOVERLEAF
      if cloverleaf_speed:
        self.cloverleaf_speed = cloverleaf_speed

  def move(self, code:str, strategy:int=None):
    # pre processing
    code = code.strip()

    if not strategy:
      strategy = self.strategy

    # parse x and y position
    splited_code = code.split(' ')
    assert len(splited_code) >= 2
    assert splited_code[0][0] == 'G'

    dx = 0
    dy = 0
    next_speed = None
    for i in range(1, len(splited_code)):
      prefix = splited_code[i][0].upper()
      val = float(splited_code[i][1:])
      if prefix == 'X':
        dx = val
      elif prefix == 'Y' or prefix == 'U':
        dy = val
      elif prefix == 'F':
        next_speed = val
    if not next_speed:
      next_speed = self.default_speed

    # post processing
    if strategy == self.STRATEGY_PAUSE:
      self.file.write(code+'\n')
      self.file.write(f'G4 P{self.pause_msec}\n')
    elif strategy == self.STRATEGY_UTURN:
      theta = math.atan2(dy,dx)
      L = math.sqrt(dx**2 + dy**2)
      
      L_forward = L + self.uturn_length
      dx_forward = L_forward * math.cos(theta)
      dy_forward = L_forward * math.sin(theta)
      dx_backward = -self.uturn_length * math.cos(theta)
      dy_backward = -self.uturn_length * math.sin(theta)
      
      forward_code = splited_code[0]
      backward_code = splited_code[0]
      
      if abs(dx_forward) > 1e-9:
        forward_code += f' X{dx_forward:.6f}'
      if abs(dy_forward) > 1e-9:
        forward_code += f' Y{dy_forward:.6f}'

      forward_code += f' F{next_speed:.0f}\n'
      self.file.write(forward_code)

      if abs(dx_backward) > 1e-9:
        backward_code += f' X{dx_backward:.6f}'
      if abs(dy_backward) > 1e-9:
        backward_code += f' Y{dy_backward:.6f}'
        
      uturn_speed = self.uturn_speed if self.uturn_speed > 0 else next_speed
      backward_code += f' F{uturn_speed:.0f}\n'
      self.file.write(backward_code)
    
    elif strategy == self.STRATEGY_CLOVERLEAF or strategy == self.STRATEGY_CLOVERLEAF2:
      prev_dx = self.prev_dx
      prev_dy = self.prev_dy
      if abs(prev_dx) > 0 or abs(prev_dy) > 0:
        theta = math.atan2(dy,dx)
        prev_theta = math.atan2(prev_dy, prev_dx)
        x1 = self.cloverleaf_radius * math.cos(prev_theta)
        y1 = self.cloverleaf_radius * math.sin(prev_theta)
        x2 = self.cloverleaf_radius * math.cos(theta)
        y2 = self.cloverleaf_radius * math.sin(theta)
        x3 = -x2 - x1
        y3 = -y2 - y1
        cross_product = (prev_dx*dy - prev_dy*dx)
        dir_code = 'G3' if cross_product <= 0 else 'G2'
        speed = self.cloverleaf_speed if self.cloverleaf_speed > 0 else next_speed
        
        if strategy == self.STRATEGY_CLOVERLEAF:
          self.write(f'{dir_code} I{x1 + 0.5*x3:.6f} J{y1 + 0.5*y3:.6f} F{speed:.0f}')
        else:
          self.write(f'G1 X{x1:.6f} Y{y1:.6f} F{self.default_speed:.0f}')
          self.write(f'{dir_code} X{x3:.6f} Y{y3:.6f} I{-x1:.6f} J{-y1:.6f} F{speed:.0f}')
          self.write(f'G1 X{x2:.6f} Y{y2:.6f} F{self.default_speed:.0f}')
          self.write(code)
        
        self.write(code)
      else:
        self.write(code) 
    else:
      self.write(code)

    self.prev_dx = dx
    self.prev_dy = dy

  def move_with_pause(self, code:str, msec):
    prev_pause = self.pause_msec
    self.pause_msec = msec
    self.move(code, strategy=self.STRATEGY_PAUSE)
    self.set_pause(prev_pause)

  def move_with_uturn(self, code:str, length):
    prev_uturn = self.uturn_length
    self.uturn_length = length
    self.move(code, strategy=self.STRATEGY_UTURN)
    self.set_uturn(prev_uturn)

  def move_with_cloverleaf(self, code:str, radius):
    prev_cloverleaf_radius = self.cloverleaf_radius
    self.cloverleaf_radius = radius
    self.move(code, strategy=self.STRATEGY_CLOVERLEAF)
    self.set_cloverleaf_radius(prev_cloverleaf_radius)

  def write(self, code:str):
    code = code.strip()
    self.file.write(code+'\n')

  def __str__(self):
    if self.strategy == self.STRATEGY_NONE:
      return 'none'
    elif self.strategy == self.STRATEGY_PAUSE:
      return f'pause ({self.pause_msec:.6f}ms)'
    elif self.strategy == self.STRATEGY_UTURN:
      return f'uturn ({self.uturn_length}mm, {self.uturn_speed:.0f}mm/min)'
    elif self.strategy == self.STRATEGY_CLOVERLEAF:
      return f'cloverleaf ({self.cloverleaf_radius}mm)'
    return ''
  
  def suffix_for_filename(self):
    if self.strategy == self.STRATEGY_NONE:
      return '_s-none_'
    elif self.strategy == self.STRATEGY_PAUSE:
      return f'_s-pause{self.pause_msec*1000:.0f}us)_'
    elif self.strategy == self.STRATEGY_UTURN:
      return f'_s-uturn{self.uturn_length*1000:.0f}um-{self.uturn_speed:.0f}_'
    elif self.strategy == self.STRATEGY_CLOVERLEAF:
      return f'_s-cloverleaf{self.cloverleaf_radius*1000:.0f}um_'
    return ''