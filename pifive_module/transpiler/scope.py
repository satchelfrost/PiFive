from .symbols import Variable
from .symbols import Function
from .register_pool import RegPool

class Scope:
  def __init__(self, name='global', parent=None):
    self.name = name
    self.parent : Scope = parent
    self._variables : dict[str, Variable] = {}
    self._functions : dict[str, Function] = {}
    self._label_counter = -1
    self.num_children = 0
    self.scope_num = 0

    if parent:
      self.scope_num = self.parent.num_children + 1
      self.parent.num_children += 1

  def get_next_label_number(self):
    self._label_counter += 1
    return self._label_counter

  def add_var(self, var : Variable):
    '''Attempts to add variable unless it already exists'''
    try:
      self.lookup_var(var.name)
    except:
      self._variables[var.name] = var

  def add_vars(self, vars : list):
    for var in vars:
      self.add_var(var)

  def lookup_var(self, var_name : str) -> Variable:
    if var_name in self._variables:
      return self._variables[var_name]
    elif self.parent is not None:
      return self.parent.lookup_var(var_name)
    else:
      raise RuntimeError(f'Variable "{var_name}" undefined in current scope. Cannot load.')

  def deactivate_regs(self, reg_pool : RegPool):
    '''Deacvtivates the registers of all variables in the current scope, and return those registers.'''
    regs = []
    for var in self._variables.values():
      if var.reg is not None:
        regs.append(var.reg)
        var.reg_active = False
        reg_pool.free_reg(var.reg)
    return regs

  def add_func(self, name, args):
    if name not in self._functions:
      self._functions[name] = Function(name, args)
    else:
      raise RuntimeError(f'Function "{name}" already exists in the current scope!')

  def lookup_func(self, name : str) -> Function:
    if name in self._functions:
      return self._functions[name]
    elif self.parent is not None:
      return self.parent.lookup_func(name)
    else:
      raise RuntimeError(f'Function "{name}" does not exist in the current scope!')
