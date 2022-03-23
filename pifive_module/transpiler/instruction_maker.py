from .registers import Reg
from enum import Enum

class Binop(Enum):
  ADD = 'add' 
  SUB = 'sub'
  AND = 'and'
  OR  = 'or'
  XOR = 'xor'
  MUL = 'mul'
  DIV = 'div'

class InstructionMaker:
  def __init__(self, comments_on=False):
    self.comments_on = comments_on
    self.reset()

  def reset(self):
    self.instr_buffer = []

  def print(self):
    print("\n".join(self.instr_buffer))
  
  def load_imm(self, reg : Reg, value):
    self.instr_buffer.append(f"\tli {reg.name}, {value}")

  def mv(self, dest_reg : Reg, src_reg : Reg):
    self.instr_buffer.append(f"\tmv {dest_reg.name}, {src_reg.name}")

  def push(self, reg : Reg, value : str):
    self.instr_buffer.append(f"\taddi sp, sp, -8")
    self.instr_buffer.append(f"\tli {reg.name}, {value}")
    self.instr_buffer.append(f"\tsd {reg.name}, 0(sp)")
  
  def push_reg(self, reg : Reg):
    self.instr_buffer.append(f"\taddi sp, sp, -8")
    self.instr_buffer.append(f"\tsd {reg.name}, 0(sp)")

  def pop(self, reg : Reg):
    self.instr_buffer.append(f"\tld {reg.name}, 0(sp)")
    self.instr_buffer.append(f"\taddi sp, sp, 8")

  def binop(self, binop : str, dst : Reg, src_1 : Reg, src_2 : Reg):
    self.instr_buffer.append(f"\t{binop} {dst.name}, {src_1.name}, {src_2.name}")
  
  def comment(self, comment):
    if self.comments_on:
      self.instr_buffer.append(f"\t# {comment}")

  def newline(self):
    if self.comments_on:
      self.instr_buffer.append("")

