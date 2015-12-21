import unittest
import connection


class TestConnection(unittest.TestCase):

    def setUp(self):
        self.c = connection.Connection()

    def test_get_dbs(self):
        dbs = self.c.databases()
        self.assertTrue('arango_client_test' in dbs and '_system' in dbs)

    def test_get_db(self):
        db = self.c.arango_client_test
        self.assertIsNotNone(db)

    def test_get_wrong_db(self):
        self.assertRaises(KeyError, self.c.__getattr__, 'potato')


suite = unittest.TestLoader().loadTestsFromTestCase(TestConnection)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
