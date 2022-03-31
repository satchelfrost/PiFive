import unittest
from ..transpiler.transpiler import RISCV_Transpiler
from ast import parse

class TestTranspiler(unittest.TestCase):
  rv = RISCV_Transpiler()

  def transforms(self, src_in, src_out):
    self.rv.reset()
    node = parse("\n".join(src_in))
    self.rv.transpile(node)
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