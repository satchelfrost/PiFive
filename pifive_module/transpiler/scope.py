from .symbols import Variable
from .symbols import Function
from .register_pool import RegPool
from .registers import RegType

class Scope:
  def __init__(self, name='global', parent=None, locals_count=0):
    self.name = name
    self.parent : Scope = parent
    self._variables : dict[str, Variable] = {}
    self._functions : dict[str, Function] = {}
    self._label_counter = -1
    self.num_children = 0
    self.scope_num = 0
    self.locals_count = locals_count

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
      var.offset = len(self._variables)
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
  
  def in_scope(self, var_name : str) -> bool:
    if var_name in self._variables:
      return True
    elif self.parent is not None:
      return self.parent.in_scope(var_name)
    else:
      return False

  def deactivate_regs(self, reg_pool : RegPool):
    '''Deacvtivates the registers of all variables in the current scope, and return those registers.'''
    regs = []
    for var in self._variables.values():
      if var.reg is not None:
        regs.append(var.reg)
        var.reg_active = False
        reg_pool.free_reg(var.reg)
    return regs

  def get_active_vars(self, reg_type : RegType) -> list:
    '''Returns a list of all variables in the current scope that are active'''
    active_vars = []
    for var in self._variables.values():
      if var.reg_active and var.reg in reg_type.value:
        active_vars.append(var)

    # Check for active variables in parent scope
    if self.name == self.parent.name:
      active_vars += self.parent.get_active_vars(reg_type)

    return active_vars

  def get_next_var(self, reg_type : RegType):
    '''Returns the next available variable in the current scope'''
    # First check the immediate scope
    for var in self._variables.values():
      if var.reg_active:
        if var.reg in reg_type.value:
          return var
 
    # Then check the parent scope
    if self.name == self.parent.name:
      return self.parent.get_next_var()

    # If all else fails throw an exception
    raise RuntimeError('No available variables in current scope!')

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
