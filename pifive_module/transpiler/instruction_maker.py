from .registers import Reg
from enum import Enum
from colorama import Fore

class BinOp(Enum):
  ADD = 'add' 
  SUB = 'sub'
  AND = 'and'
  OR  = 'or'
  XOR = 'xor'
  MUL = 'mul'
  DIV = 'div'

  def to_english(self):
    if self.name == BinOp.ADD.name:
      return "Add"
    elif self.name == BinOp.SUB.name:
      return "Subtract"
    elif self.name == BinOp.AND.name:
      return "AND"
    elif self.name == BinOp.OR.name:
      return "OR"
    elif self.name == BinOp.XOR.name:
      return "XOR"
    elif self.name == BinOp.MUL.name:
      return "Multiply"
    elif self.name == BinOp.DIV.name:
      return "Divide"
    else:
      raise RuntimeError(f'binop {self.name} has no english equivalent.')

class InstructionMaker:
  def __init__(self, comments_on=False):
    self.comments_on = comments_on
    self.reset()

  def reset(self):
    self.instr_buffer = []

  def print(self):
    for line in self.instr_buffer:
      if "#" in line:
        print(Fore.CYAN + line)
      else:
        print(Fore.LIGHTWHITE_EX + line)

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


  #### Assembly comment section - not actual instructions! ####
  def comment(self, comment):
    if self.comments_on:
      self.instr_buffer.append(f"\t# {comment}")

  def comment_reg_free(self, reg : Reg):
    self.comment(f'Register "{reg.name}" freed')

  def comment_push_val(self, value : str):
    self.comment(f'Push value "{value}" to the stack')

  def comment_pop(self, reg : Reg):
    self.comment(f'Activate "{reg.name}" by popping stack.')

  def comment_binop(self, binop : BinOp, reg : Reg):
    self.comment(f'{binop.to_english()} result and store into "{reg.name}"')

  def comment_binop_push(self, binop : BinOp, reg : Reg):
    self.comment(f'Push {binop.to_english().lower()}-result from "{reg.name}" to stack')

  def comment_assign(self, name : str):
      self.comment(f'Target assignment variable "{name}".')

  def newline(self):
    if self.comments_on:
      self.instr_buffer.append("")