from .registers import Reg, RegType
from .symbols import Variable

class RegPool:
  def __init__(self):
    self.reset()

  def reset(self):
    '''resets all registers to available'''
    self.available_regs = [True for i in range(len(Reg))]
    self.bound_regs = [None for i in range(len(Reg))]

  def get_next_reg(self, reg_type : RegType):
    '''Get next available register of a particular type'''
    for reg in reg_type.value:
      if self.available_regs[reg.value]:
        self.available_regs[reg.value] = False
        # self.mru_reg = reg
        return reg
    return None

  def bind_reg(self, reg : Reg, var : Variable):
    '''Bind a register to a variable'''
    self.bound_regs[reg.value] = var
    var.reg = reg

  def unbind_reg(self, reg : Reg):
    '''Unbind a register from a variable'''
    var = self.bound_regs[reg.value]
    var.reg = None
    self.bound_regs[reg.value] = None

  def lookup_bound_variable(self, reg : Reg) -> Variable:
    '''Lookup a bound variable by register'''
    return self.bound_regs[reg.value]

  def is_reg_type_available(self, reg_type : RegType) -> bool:
    '''Checks if register of a particular type is available'''
    for reg in reg_type.value:
      if self.available_regs[reg.value]:
        return True
    return False

  def is_reg_available(self, reg : Reg) -> bool:
    '''Checks if a register is available'''
    return self.available_regs[reg.value]
  
  def free_reg(self, reg : Reg):
    '''Make a register available again'''
    self.available_regs[reg.value] = True
  
  def free_regs(self, regs):
    '''Make a list of registers available again'''
    for reg in regs:
      self.free_reg(reg)

  def take_reg(self, reg : Reg):
    '''Make a register unavailable'''
    self.available_regs[reg.value] = False