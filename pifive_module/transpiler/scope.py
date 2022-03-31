from .symbols import Variable
from .symbols import Function

class Scope:
  def __init__(self, name='global', parent=None):
    self.frame = name
    self.parent : Scope = parent
    self._variables : dict[str, Variable] = {}
    self._functions : dict[str, Function] = {}
    self._label_counter = -1
    if parent is not None:
      self.scope_id = self.parent.scope_id + 1
    else:
      self.scope_id = 0

  def get_next_label_number(self):
    self._label_counter += 1
    return self._label_counter

  def add_var(self, var : Variable):
    if var.name not in self._variables:
      self._variables[var.name] = var

  def add_vars(self, vars : list):
    for var in vars:
      self.add_var(var)

  def lookup_var(self, var_name : str):
    if var_name in self._variables:
      return self._variables[var_name]
    elif self.parent is not None:
      return self.parent.lookup_var(var_name)
    else:
      raise RuntimeError(f'Variable "{var_name}" undefined in current scope. Cannot load.')

  def get_regs_in_use(self):
    regs_in_use = []
    for var in self._variables.values():
      if var.reg is not None:
        regs_in_use.append(var.reg)
    return regs_in_use

  def add_func(self, name, args):
    if name not in self._functions:
      self._functions[name] = Function(name, args)
    else:
      raise RuntimeError(f'Function {name} already exists in the current scope!')
  
  def lookup_func(self, name : str):
    if name in self._functions:
      return self._functions[name]
    elif self.parent is not None:
      return self.parent.lookup_func(name)
    else:
      raise RuntimeError(f'Function {name} already exists in the current scope!')
