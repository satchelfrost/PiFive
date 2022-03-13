from .registers import Reg

class InstructionMaker:
  def __init__(self):
    self.reset()
  
  def reset(self):
    self.instr_buffer = []
  
  def print(self):
    print("\n".join(self.instr_buffer))
  
  def load_imm(self, reg : Reg, value):
    self.instr_buffer.append(f"\tli {reg.name}, {value}")
  
  def mv(self, dest_reg : Reg, src_reg : Reg):
    self.instr_buffer.append(f"\tmv {dest_reg.name}, {src_reg.name}")
