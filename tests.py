import unittest
import connection
import odm


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


class TestDatabase(unittest.TestCase):

    def setUp(self):
        c = connection.Connection()
        self.d = c.arango_client_test

    def test_get_collections(self):
        cols = self.d.collections()
        self.assertCountEqual(['collection_one', 'collection_two'], cols)

    def test_get_collection(self):
        v = self.d.collection_one
        self.assertIsNotNone(v)


class TestCollection(unittest.TestCase):

    def setUp(self):
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


class TestODM(unittest.TestCase):

    def setUp(self):
        c = connection.Connection()

        class Test(odm.Base):
            _collection = "collection_one"
            _db = c.arango_client_test
            name = odm.Field()
            surname = odm.Field()

        self.c = Test
        self.col = c.arango_client_test.collection_one
        doc = {'name': 'Bran', 'surname': 'Stark', '_key':'BranStark'}
        self.bran = self.col.save(doc)

    def test_field(self):
        i = self.c(name="Field1")
        self.assertEqual("Field1", i.name)
        i.surname = "Test"
        self.assertEqual("Test", i.surname)


    def test_get(self):
        o = self.c.get('BranStark')
        self.assertEqual(o.name, 'Bran')
        self.assertEqual(o.surname, 'Stark')

    def test_doc(self):
        o = self.c.get('BranStark')
        self.assertEqual(o._doc(), {'name':'Bran', 'surname':'Stark'})

    def test_put(self):
        o = self.c.get('BranStark')
        o.name = 'Brandon'
        o.sigil = 'Wolf'
        o.update()
        self.assertEqual(self.c.get('BranStark').name, 'Brandon')
        self.assertEqual(self.c.get('BranStark').sigil, 'Wolf')

    def test_delete(self):
        o = self.c.get('BranStark')
        o.delete()
        self.assertRaises(KeyError, self.c.get, 'BranStark')

    def tearDown(self):
        try:
            self.col.delete('BranStark')
        except:
            pass


if __name__ == '__main__':
        unittest.main()
