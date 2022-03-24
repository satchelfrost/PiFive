from .registers import Reg, RegType

class RegPool:
  def __init__(self):
    self.reset()
    # self.mru_reg : Reg = None

  def reset(self):
    '''resets all registers to available'''
    self.available_regs = [True for i in range(len(Reg))]

  def get_next_reg(self, reg_type : RegType):
    '''Get next available register of a particular type'''
    for reg in reg_type.value:
      if self.available_regs[reg.value]:
        self.available_regs[reg.value] = False
        # self.mru_reg = reg
        return reg
    return None

  def is_reg_type_avilable(self, reg_type : RegType) -> bool:
    '''Checks if register of a particular type is available'''
    for reg in reg_type.value:
      if self.available_regs[reg.value]:
        return True
    return False
  
  def free_reg(self, reg : Reg):
    '''Make a register available again'''
    self.available_regs[reg.value] = True

  def take_reg(self, reg : Reg):
    '''Make a register unavailable'''
    self.available_regs[reg.value] = False
