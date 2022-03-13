import unittest
from ..transpiler.transpiler import RISCV_Transpiler
from ast import parse

class TestTranspiler(unittest.TestCase):
  rv = RISCV_Transpiler()

  def transform(self, src_in, src_out):
    self.rv.reset()
    node = parse("\n".join(src_in))
    self.rv.transpile(node)
    if self.rv.asm.instr_buffer:
      self.assertEqual(src_out, self.rv.asm.instr_buffer)
    else:
      self.fail("Instruction buffer was empty")

  def test_single_assign(self):
    src_in = ["x = 42"]
    src_out = ["\tli t0, 42"]
    self.transform(src_in, src_out)

  def test_successive_assign(self):
    src_in = [
      "a = 1",
      "b = 2"
    ]
    src_out = [
      "\tli t0, 1",
      "\tli t1, 2"
    ]
    self.transform(src_in, src_out)

  def test_reassign(self):
    src_in = [
      "a = 1",
      "b = 2",
      "a = b"
    ]
    src_out = [
      "\tli t0, 1",
      "\tli t1, 2",
      "\tmv t0, t1"
    ]
    self.transform(src_in, src_out)