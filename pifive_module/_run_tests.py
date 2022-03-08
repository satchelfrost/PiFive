import unittest
from . import tests

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(tests)
    runner = unittest.TextTestRunner()
    res = runner.run(suite)