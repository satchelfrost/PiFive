import unittest
from ..transpiler.transpiler import RISCV_Transpiler
from ast import parse

class TestTranspiler(unittest.TestCase):
  rv = RISCV_Transpiler()

  def transforms(self, src_in, src_out):
    self.rv.reset()
    node = parse("\n".join(src_in))
    try:
      self.rv.transpile(node)
    except Exception as e:
      print(e)
      self.fail("Transpiler failed")
    if self.rv.instr.instr_buffer:
      self.assertEqual(src_out, self.rv.instr.instr_buffer)
    else:
      self.fail("Instruction buffer was empty")

  def test_single_assign(self):
    src_in = ["x = 42"]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 42",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_successive_assign(self):
    src_in = [
      "a = 1",
      "b = 2"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 1",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 2",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_reassign(self):
    src_in = [
      "a = 1",
      "b = 2",
      "a = b"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 1",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 2",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
    ]
    self.transforms(src_in, src_out)

  def test_add_binop(self):
    src_in, src_out = self.simple_binop("1", "+", "41", "add")
    self.transforms(src_in, src_out)

  def test_mul_binop(self):
    src_in, src_out = self.simple_binop("1", "*", "41", "mul")
    self.transforms(src_in, src_out)

  def test_div_binop(self):
    src_in, src_out = self.simple_binop("1", "/", "41", "div")
    self.transforms(src_in, src_out)

  def test_sub_binop(self):
    src_in, src_out = self.simple_binop("1", "-", "41", "sub")
    self.transforms(src_in, src_out)

  def test_and_binop(self):
    src_in, src_out = self.simple_binop("1", "&", "41", "and")
    self.transforms(src_in, src_out)

  def test_or_binop(self):
    src_in, src_out = self.simple_binop("1", "|", "41", "or")
    self.transforms(src_in, src_out)

  def test_xor_binop(self):
    src_in, src_out = self.simple_binop("1", "^", "41", "xor")
    self.transforms(src_in, src_out)

  def simple_binop(self, left : str, op : str, right : str, instr : str):
    src_in = [
      f"a = {left} {op} {right}"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      f"\tli t0, {left}",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      f"\tli t0, {right}",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      f"\t{instr} t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    return src_in, src_out

  def test_simple_binop_with_load(self):
    src_in = [
      "b = 41",
      "a = 1 - b"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 41",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 1",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tsub t2, t2, t1",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_complex_binop(self):
    src_in = [
      "a = 1 - 41 + 3 * 5"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 1",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 41",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tsub t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 3",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 5",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tmul t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_complex_binop_with_load(self):
    src_in = [
      "b = 103",
      "a = 41 + 3 * 5 - b"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 103",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 41",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t1, 3",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t1, 5",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tmul t2, t2, t1",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t2, t2, t1",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tsub t2, t2, t1",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def simple_branch_cmp(self, left : str, op : str, right : str, instr : str):
    src_in = [
      f"{left} {op} {right}"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      f"\tli t0, {left}",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      f"\tli t0, {right}",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t2, 1",
      f"\t{instr} t1, t0, {instr.upper()}_global_sc_0_lab_0",
      "\tli t2, 0",
      f"{instr.upper()}_global_sc_0_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_lt(self):
    self.simple_branch_cmp("23", "<", "42", "blt")

  def test_gt(self):
    self.simple_branch_cmp("23", ">", "42", "bgt")

  def test_eq(self):
    self.simple_branch_cmp("23", "==", "42", "beq")

  def test_ne(self):
    self.simple_branch_cmp("23", "!=", "42", "bne")

  def test_le(self):
    self.simple_branch_cmp("23", "<=", "42", "ble")

  def test_ge(self):
    self.simple_branch_cmp("23", ">=", "42", "bge")

  def test_cmp_assign(self):
    src_in = [
      "a = 23 > 25"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 23",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 25",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t2, 1",
      "\tbgt t1, t0, BGT_global_sc_0_lab_0",
      "\tli t2, 0",
      "BGT_global_sc_0_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
    ]
    self.transforms(src_in, src_out)

  def test_if_elif_else(self):
    src_in = [
      "if 23 < 25:",
      "  a = 32",
      "elif 23 == 25:",
      "  a = 4",
      "else:",
      "  a = 23"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 23",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 25",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t2, 1",
      "\tblt t1, t0, BLT_global_sc_0_lab_0",
      "\tli t2, 0",
      "BLT_global_sc_0_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t0, else_global_sc_1_lab_0",
      "\taddi sp, sp, -8",
      "\tli t0, 32",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tj end_global_sc_2_lab_0",
      "else_global_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tli t0, 23",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 25",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t2, 1",
      "\tbeq t1, t0, BEQ_global_sc_2_lab_1",
      "\tli t2, 0",
      "BEQ_global_sc_2_lab_1:",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t0, else_global_sc_1_lab_0",
      "\taddi sp, sp, -8",
      "\tli t0, 4",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tj end_global_sc_2_lab_0",
      "else_global_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tli t0, 23",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "end_global_sc_2_lab_0:",
      "end_global_sc_2_lab_0:"
    ]
    self.transforms(src_in, src_out)

  def test_if_with_load(self):
    src_in = [
      "a = 50",
      "if 23 < 25:",
      "  a = 100",
      "b = a + 4"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 50",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 23",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t1, 25",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t3, 1",
      "\tblt t2, t1, BLT_global_sc_0_lab_0",
      "\tli t3, 0",
      "BLT_global_sc_0_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t3, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t1, else_global_sc_1_lab_0",
      "\taddi sp, sp, -8",
      "\tli t1, 100",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "else_global_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t1, 4",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t2, t2, t1",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_if_else(self):
    src_in = [
      "if 23 < 25:",
      "  a = 100",
      "else:",
      "  a = 200"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 23",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 25",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t2, 1",
      "\tblt t1, t0, BLT_global_sc_0_lab_0",
      "\tli t2, 0",
      "BLT_global_sc_0_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t0, else_global_sc_1_lab_0",
      "\taddi sp, sp, -8",
      "\tli t0, 100",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tj end_global_sc_2_lab_0",
      "else_global_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tli t0, 200",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "end_global_sc_2_lab_0:"
    ]
    self.transforms(src_in, src_out)

  def test_function(self):
    src_in = [
      "def function(a, b):",
      "  c = a + b",
      "  return c"
    ]
    src_out = [
      "function:",
      "\taddi sp, sp, -16",
      "\tsd ra, 8(sp)",
      "\tsd fp, 0(sp)",
      "\taddi fp, sp, 16",
      "\taddi sp, sp, -8",
      "\tsd a1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tsd a2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld ra, 8(sp)",
      "\tld fp, 0(sp)",
      "\taddi sp, sp, 16",
      "\tret"
    ]
    self.transforms(src_in, src_out)

  def test_function_call(self):
    src_in = [
      "def function(a, b):",
      "  c = a + b",
      "  return c",
      "function(1, function(2, 3))"
    ]
    src_out = [
      "function:",
      "\taddi sp, sp, -16",
      "\tsd ra, 8(sp)",
      "\tsd fp, 0(sp)",
      "\taddi fp, sp, 16",
      "\taddi sp, sp, -8",
      "\tsd a1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tsd a2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld ra, 8(sp)",
      "\tld fp, 0(sp)",
      "\taddi sp, sp, 16",
      "\tret",
      "\taddi sp, sp, -8",
      "\tli t0, 3",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 2",
      "\tsd t0, 0(sp)",
      "\tld a1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld a2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tcall function",
      "\taddi sp, sp, -8",
      "\tsd a0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 1",
      "\tsd t0, 0(sp)",
      "\tld a1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld a2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tcall function",
      "\taddi sp, sp, -8",
      "\tsd a0, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8"
    ]
    self.transforms(src_in, src_out)

  def test_recursive_function_call(self):
    src_in = [
      "def factorial(n):",
      "  if n == 0:",
      "    return 1",
      "  return n * factorial(n-1)",
      "",
      "def main():",
      "  a = factorial(3 + 4) * 123",
      "  return 0"
    ]
    src_out = [
      "factorial:",
      "\taddi sp, sp, -16",
      "\tsd ra, 8(sp)",
      "\tsd fp, 0(sp)",
      "\taddi fp, sp, 16",
      "\taddi sp, sp, -8",
      "\tsd a1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 0",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t2, 1",
      "\tbeq t1, t0, BEQ_factorial_sc_1_lab_0",
      "\tli t2, 0",
      "BEQ_factorial_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t0, else_factorial_sc_1_lab_0",
      "\taddi sp, sp, -8",
      "\tli t0, 1",
      "\tsd t0, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld ra, 8(sp)",
      "\tld fp, 0(sp)",
      "\taddi sp, sp, 16",
      "\tret",
      "else_factorial_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd a1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tsd a1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 1",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tsub t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld a1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tcall factorial",
      "\taddi sp, sp, -8",
      "\tsd a0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tmul t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld ra, 8(sp)",
      "\tld fp, 0(sp)",
      "\taddi sp, sp, 16",
      "\tret",
      "main:",
      "\taddi sp, sp, -16",
      "\tsd ra, 8(sp)",
      "\tsd fp, 0(sp)",
      "\taddi fp, sp, 16",
      "\taddi sp, sp, -8",
      "\tli t0, 3",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 4",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld a1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tcall factorial",
      "\taddi sp, sp, -8",
      "\tsd a0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t0, 123",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tmul t1, t1, t0",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 0",
      "\tsd t1, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld ra, 8(sp)",
      "\tld fp, 0(sp)",
      "\taddi sp, sp, 16",
      "\tret"
    ]
    self.transforms(src_in, src_out)

  def test_while(self):
    src_in = [
      "i = 0",
      "while i < 10:",
      "  i = i + 1"
    ]
    src_out = [
      "\taddi sp, sp, -8",
      "\tli t0, 0",
      "\tsd t0, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "while_global_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t1, 10",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t3, 1",
      "\tblt t2, t1, BLT_global_sc_1_lab_2",
      "\tli t3, 0",
      "BLT_global_sc_1_lab_2:",
      "\taddi sp, sp, -8",
      "\tsd t3, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t1, break_global_sc_1_lab_1",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t1, 1",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t2, t2, t1",
      "\taddi sp, sp, -8",
      "\tsd t2, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tj while_global_sc_1_lab_0",
      "break_global_sc_1_lab_1:"
    ]
    self.transforms(src_in, src_out)

  def test_while_in_fn(self):
    src_in = [
      "def sum(n):",
      "  sum = n",
      "  i = 0",
      "  while i < 10:",
      "    i = i + 1",
      "    sum = sum + 1",
      "  return sum"
    ]
    src_out = [
      "sum:",
      "\taddi sp, sp, -16",
      "\tsd ra, 8(sp)",
      "\tsd fp, 0(sp)",
      "\taddi fp, sp, 16",
      "\taddi sp, sp, -8",
      "\tsd a1, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tli t1, 0",
      "\tsd t1, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "while_sum_sc_1_lab_0:",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t2, 10",
      "\tsd t2, 0(sp)",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t3, 0(sp)",
      "\taddi sp, sp, 8",
      "\tli t4, 1",
      "\tblt t3, t2, BLT_sum_sc_1_lab_2",
      "\tli t4, 0",
      "BLT_sum_sc_1_lab_2:",
      "\taddi sp, sp, -8",
      "\tsd t4, 0(sp)",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tbeqz t2, break_sum_sc_1_lab_1",
      "\taddi sp, sp, -8",
      "\tsd t1, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t2, 1",
      "\tsd t2, 0(sp)",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t3, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t3, t3, t2",
      "\taddi sp, sp, -8",
      "\tsd t3, 0(sp)",
      "\tld t1, 0(sp)",
      "\taddi sp, sp, 8",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\taddi sp, sp, -8",
      "\tli t2, 1",
      "\tsd t2, 0(sp)",
      "\tld t2, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld t3, 0(sp)",
      "\taddi sp, sp, 8",
      "\tadd t3, t3, t2",
      "\taddi sp, sp, -8",
      "\tsd t3, 0(sp)",
      "\tld t0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tj while_sum_sc_1_lab_0",
      "break_sum_sc_1_lab_1:",
      "\taddi sp, sp, -8",
      "\tsd t0, 0(sp)",
      "\tld a0, 0(sp)",
      "\taddi sp, sp, 8",
      "\tld ra, 8(sp)",
      "\tld fp, 0(sp)",
      "\taddi sp, sp, 16",
      "\tret"
    ]
    self.transforms(src_in, src_out)