import itertools
import unittest
from avocadopy import connection as con

db = 'arango_client_test'

class TestCase(unittest.TestCase):

    @staticmethod
    def _truncate_all():
        c = con.Connection()
        c.arango_client_test.collection_one.truncate()
        c.arango_client_test.collection_two.truncate()
        c.arango_client_test.edge.truncate()




from avocadopy.tests import collection
from avocadopy.tests import database
from avocadopy.tests import connection
from avocadopy.tests import edge


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
