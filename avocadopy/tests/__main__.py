import unittest
import itertools
from avocadopy.tests import suite
from avocadopy.tests import odm

suite = list(
    itertools.chain(
    suite,
    odm.suite
    )
)
if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(_suite)
