import unittest
from avocadopy.tests import TestCase
from avocadopy import connection

class TestCollection(TestCase):

    def setUp(self):
        self._truncate_all()
        c = connection.Connection()
        self.col = c.arango_client_test.collection_one
        doc = {'name': 'Bran', 'surname': 'Stark'}
        self.bran = self.col.save(doc)

    def test_create_document(self):
        doc = {'name': 'Tyrion', 'surname': 'Lannister'}
        tyrion = self.col.save(doc)
        self.assertIsNotNone(tyrion)
        self.assertGreater(len(tyrion), 0)
        self.col.delete(tyrion)

    def test_get_documents(self):
        docs = self.col.documents()
        self.assertIn(self.bran, docs)
        self.assertEqual(docs[0]['name'], "Bran")
        for d in docs:
            self.assertIsNotNone(d['name'])

    def test_get_document(self):
        doc = self.col[self.bran]
        self.assertEqual(doc['name'], "Bran")

    def test_get_document_by_example(self):
        docs = self.col.example({'name': 'Bran'})
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['name'], 'Bran')

    def test_update_document(self):
        doc = self.col[self.bran]
        doc['name'] = 'Brandon'
        self.col.update(self.bran, doc)
        doc_u = self.col[self.bran]
        self.assertEqual(doc_u['name'], 'Brandon')

    def tearDown(self):
        self.col.delete(self.bran)

    def test_get_missing_doc(self):
        self.assertRaises(KeyError, self.col.__getitem__, 'collection_one/2555429912933')


suite = unittest.TestLoader().loadTestsFromTestCase(TestCollection)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
