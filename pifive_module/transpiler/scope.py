class Variable:
  def __init__(self, name, type=None, reg=None, offset=None):
    self.name = name
    self.type = type
    self.reg = reg
    self.offset = offset

class Scope:
  def __init__(self, name, parent_scope=None):
    self.name = name
    self.parent_scope : Scope = parent_scope
    self._variables = {}
    self._functions = {} 
  
  def nm_scope(self):
    # Return name mangled scope
    if self.parent_scope:
      return f"{self.parent_scope.nm_scope()}/{self.name}"
    else:
      return self.name

  def add_var(self, var : Variable):
    if var.name not in self._variables:
      self._variables[var.name] = var
    return self._variables[var.name]
  
  def lookup_var(self, var_name : str):
    if var_name in self._variables:
      return self._variables[var_name]
    elif self.parent_scope is not None:
      return self.parent_scope.lookup_var(var_name)
    else:
      return None