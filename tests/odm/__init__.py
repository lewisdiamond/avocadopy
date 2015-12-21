import edge
import odm
import rel
import validation
import transformation
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
