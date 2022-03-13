class Variable:
  def __init__(self, name, type, reg, offset):
    self.name = name
    self.type = type
    self.reg = reg
    self.offset = offset

class Scope:
  def __init__(self, parent_scope=None):
    self.parent_scope : Scope = parent_scope
    self._variables = {}
    self._functions = {} 
  
  def add_var(self, var : Variable):
    if var.name not in self._variables:
      self._variables[var.name] = var
  
  def lookup_var(self, var_name : str):
    if var_name in self._variables:
      return self._variables[var_name]
    elif self.parent_scope is not None:
      return self.parent_scope.lookup_var(var_name)
    else:
      raise(f"Variable {var_name} does not exist in the current scope!")