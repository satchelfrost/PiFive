from .symbol_table import SymbolTable
from .symbols import Variable

class Scope:
  def __init__(self, name='global', parent_scope=None):
    self.frame = name
    self.parent_scope : Scope = parent_scope
    self._variables = {}
    self._functions = {}

  def add_var(self, var : Variable):
    if var.name not in self._variables:
      self._variables[var.name] = var
    else:
      raise RuntimeError(f'Variable {var.name} already exists in the current scope!')

  def lookup_var(self, var_name : str):
    if var_name in self._variables:
      return self._variables[var_name]
    elif self.parent_scope is not None:
      return self.parent_scope.lookup_var(var_name)
    else:
      return None