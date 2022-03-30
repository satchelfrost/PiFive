from .symbols import Variable

class Scope:
  def __init__(self, name='global', parent=None):
    self.frame = name
    self.parent : Scope = parent
    self._variables = {}
    self._functions = {}
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
    else:
      raise RuntimeError(f'Variable {var.name} already exists in the current scope!')

  def lookup_var(self, var_name : str):
    if var_name in self._variables:
      return self._variables[var_name]
    elif self.parent is not None:
      return self.parent.lookup_var(var_name)
    else:
      return None