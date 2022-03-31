from .instruction_maker import InstructionMaker
from .symbols import Symbol, SymbolKind
from .registers import Reg

class SymbolTable:
  def __init__(self):
    self.reset()
  
  def reset(self):
    '''frame -> symbol_list'''
    self.symbol_table : dict[str,list[Symbol]] = {}

  def save_and_free_reg(self, frame : str, instr : InstructionMaker) -> Reg:
    pass

  def save_and_free_all_regs(self, frame : str, instr : InstructionMaker):
    pass

  def lookup_symbol(self, symbol_name : str, frame : str, kind : SymbolKind):
    if frame not in self.symbol_table:
      raise RuntimeError(f"frame {frame} does not exist!")

    for symbol in self.symbol_table[frame]:
      if symbol.name == symbol_name and symbol.kind == kind:
        return symbol

    raise RuntimeWarning(f'Symbol "{symbol_name}" does not exist in frame "{frame}"')

  def add_symbol(self, frame : str, symbol : Symbol):
    if frame not in self.symbol_table:
      self.symbol_table[frame] = [symbol]
    else:
      self.symbol_table[frame].append(symbol)

