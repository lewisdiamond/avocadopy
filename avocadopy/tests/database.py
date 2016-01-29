import unittest
import six
from avocadopy import connection

class TestDatabase(unittest.TestCase):

    def setUp(self):
        c = connection.Connection()
        self.d = c.arango_client_test

    def test_get_collections(self):
        cols = self.d.collections()
        six.assertCountEqual(self, ['collection_one', 'collection_two', 'edge'], cols.keys())

    def test_get_collection(self):
        v = self.d.collection_one
        self.assertIsNotNone(v)


suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabase)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
