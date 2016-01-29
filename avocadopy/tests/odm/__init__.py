from avocadopy.tests.odm import edge
from avocadopy.tests.odm import odm
from avocadopy.tests.odm import rel
from avocadopy.tests.odm import validation
from avocadopy.tests.odm import transformation
import itertools

db = 'arango_client_test'

suite = list(
    itertools.chain(
        edge.suite
        ,odm.suite
        ,rel.suite
    )
)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
