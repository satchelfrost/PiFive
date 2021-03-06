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

class BranchOp(Enum):
  BEQ = 'beq'
  BNE = 'bne'
  BLT = 'blt'
  BLE = 'ble'
  BGT = 'bgt'
  BGE = 'bge'

  def to_english(self):
    if self.name == BranchOp.BEQ.name:
      return "Equal"
    elif self.name == BranchOp.BNE.name:
      return "Not Equal"
    elif self.name == BranchOp.BLT.name:
      return "Less Than"
    elif self.name == BranchOp.BLE.name:
      return "Less Than or Equal"
    elif self.name == BranchOp.BGT.name:
      return "Greater Than"
    elif self.name == BranchOp.BGE.name:
      return "Greater Than or Equal"
    else:
      raise RuntimeError(f'branchop {self.name} has no english equivalent.')

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

  #### Assembly instruction section ####
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

  def set_true(self, reg : Reg):
    self.load_imm(reg, 1)

  def set_false(self, reg : Reg):
    self.load_imm(reg, 0)

  def label(self, label):
    if label == "main":
      self.instr_buffer.append(f"\t.globl main")
    self.instr_buffer.append(f"{label}:")

  def print_int_label(self):
    self.label("print_int")
    self.comment("String to print our integer")
    self.instr_buffer.append('\t.string "%d\\n"')

  def load_label(self, reg : Reg, label : str):
    self.instr_buffer.append(f"\tlla {reg.name}, {label}")

  def pop(self, reg : Reg):
    self.instr_buffer.append(f"\tld {reg.name}, 0(sp)")
    self.instr_buffer.append(f"\taddi sp, sp, 8")

  def binop(self, binop : BinOp, dst : Reg, src_1 : Reg, src_2 : Reg):
    self.instr_buffer.append(f"\t{binop.value} {dst.name}, {src_1.name}, {src_2.name}")

  def branchop(self, branchop : BranchOp, left : Reg, right : Reg, label : str):
    self.instr_buffer.append(f"\t{branchop.value} {left.name}, {right.name}, {label}")

  def branch_zero(self, reg : Reg, label : str):
    self.instr_buffer.append(f"\tbeqz {reg.name}, {label}")

  def jump_label(self, label : str):
    self.instr_buffer.append(f"\tj {label}")

  def call(self, label : str):
    self.instr_buffer.append(f"\tcall {label}")

  def prologue(self, extra_stack_space : int = 0):
    self.instr_buffer.append(f"\taddi sp, sp, -{16 + extra_stack_space * 8}")
    self.instr_buffer.append(f"\tsd ra, {8 + extra_stack_space * 8}(sp)")
    self.instr_buffer.append(f"\tsd fp, {0 + extra_stack_space * 8}(sp)")
    self.instr_buffer.append(f"\taddi fp, sp, {16 + extra_stack_space * 8}")

  def epilogue(self, extra_stack_space : int = 0):
    self.instr_buffer.append(f"\tld ra, {8 + extra_stack_space * 8}(sp)")
    self.instr_buffer.append(f"\tld fp, {0 + extra_stack_space * 8}(sp)")
    self.instr_buffer.append(f"\taddi sp, sp, {16 + extra_stack_space * 8}")
    self.ret()

  def store_reg(self, reg : Reg, offset : int):
    self.instr_buffer.append(f"\tsd {reg.name}, -{(offset + 1) * 8 + 16}(fp)")

  def load_reg(self, reg : Reg, offset : int):
    self.instr_buffer.append(f"\tld {reg.name}, -{(offset + 1) * 8 + 16}(fp)")

  def ret(self):
    self.instr_buffer.append("\tret")

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

  def comment_branchop(self, branchop : BranchOp, left : Reg, right : Reg):
    self.comment(f'Test if "{left.name}" is {branchop.to_english()} "{right.name}"')

  def comment_binop_push(self, binop : BinOp, reg : Reg):
    self.comment(f'Push {binop.to_english().lower()}-result from "{reg.name}" to stack')

  def comment_reg_push(self, reg : Reg, var : str):
    self.comment(f'Push variable "{var}" in register "{reg.name}" to stack')

  def comment_assign(self, name : str):
      self.comment(f'Target assignment variable "{name}".')

  def comment_condition(self, reg : Reg):
    self.comment(f'Set register "{reg.name}" to one if condition is true.')

  def comment_branchop_push(self, branchop : BranchOp, reg : Reg):
    self.comment(f'Push "{branchop.to_english()}"-result from "{reg.name}" to stack')

  def comment_branchop_result(self, branchop : BranchOp, result : bool):
    if result:
      self.comment(f'Set "{branchop.to_english()}"-result to true initially.')
    else:
      self.comment(f'Set "{branchop.to_english()}"-result to false if branch not taken.')

  def comment_prologue(self, name : str):
    self.comment(f'Prologue for "{name}"')

  def comment_epilogue(self, name : str):
    self.comment(f'Epilogue for "{name}"')

  def newline(self):
    if self.comments_on:
      self.instr_buffer.append("")