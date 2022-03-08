import unittest

class TestTranspiler(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(1, 1)
    def test_fail(self):
        self.assertEqual(1, 2)
        