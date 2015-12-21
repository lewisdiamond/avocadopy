import unittest
import tests
import itertools
from tests import odm

suite = list(
    itertools.chain(
    tests.suite,
    odm.suite
    )
)
if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
