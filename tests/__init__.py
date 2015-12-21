import collection
import database
import connection
import edge
import itertools

db = 'arango_client_test'

suite = list(
    itertools.chain(
        collection.suite
        ,database.suite
        ,connection.suite
        ,edge.suite
    )
)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
