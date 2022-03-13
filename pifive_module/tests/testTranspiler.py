import unittest
from ..transpiler.transpiler import RISCV_Transpiler
from ast import parse

class TestTranspiler(unittest.TestCase):
  rv = RISCV_Transpiler()

  def test_pass(self):
    self.assertEqual(1, 1)

  def test_add(self):
    node = parse("x = 42")
    self.rv.transpile(node)
    self.rv.buffer.print_buffer()