import unittest
from ..transpiler.transpiler import RISCV_Transpiler
from ast import parse

class TestTranspiler(unittest.TestCase):
  rv = RISCV_Transpiler()

  def transform(self, src_in, src_out):
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
    self.transform(src_in, src_out)

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
    self.transform(src_in, src_out)

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
      "\tmv t0, t1"
    ]
    self.transform(src_in, src_out)

  # def test_reassign(self):
  #   src_in = [
  #     "a = 1 + 2 + 3",
  #   ]
  #   src_out = [
  #     "",
  #   ]
  #   self.transform(src_in, src_out)