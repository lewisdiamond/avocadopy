import connection
import unittest

class TestEdge(unittest.TestCase):

    def setUp(self):
        c = connection.Connection()
        self.d = c.arango_client_test

        self.col1 = self.d.collection_one
        self.col2 = self.d.collection_two
        self.edge = self.d.edge

        self.jamie = self.col1.save({'name':'Jamie Lannister'})
        self.bran = self.col2.save({'name':'Bran Stark'})
        self.jamie_bran = self.edge.save(self.jamie, self.bran, {'pushed_out_the_window': True})

    def test_get_edges(self):
        pass

    def test_get_edges_none_exist(self):
        pass

    def test_get_edges_invalid_vertex(self):
        pass

    def test_add_edge(self):
        pass

    def test_add_edge_invalid_vertex(self):
        pass

    def tearDown(self):
        self.col1.delete(self.jamie)
        self.col2.delete(self.bran)
        self.edge.delete(self.jamie_bran)


suite = unittest.TestLoader().loadTestsFromTestCase(TestEdge)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
