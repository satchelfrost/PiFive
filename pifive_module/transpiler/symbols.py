from enum import Enum
from .registers import Reg

class SymbolKind(Enum):
  variable = 'variable'
  function = 'function'

class Symbol:
  def __init__(self, name, kind : SymbolKind):
    self.name = name
    self.kind = kind

class Variable(Symbol):
  def __init__(self, name, type=None, reg=None, offset=None):
    super().__init__(name, kind=SymbolKind.variable)
    self.type = type
    self.reg : Reg = reg
    self.offset = offset

class Function(Symbol):
  def __init__(self, name, args, ret_reg=None):
    super().__init__(name, kind=SymbolKind.function)
    self.ret : Reg = ret_reg
    self.args : list[Variable] = args