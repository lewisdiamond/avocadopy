import unittest
from .. import odm

class TestODM(unittest.TestCase):

    def setUp(self):
        self.connection = c = connection.Connection()
        self.db = c.arango_client_test

        class Test(odm.Base):
            _collection_name = "collection_one"
            _db = self.db
            name = odm.Field()
            surname = odm.Field()

        class Test2(odm.Base):
            _collection_name = "collection_two"
            _db = self.db

        self.test2 = Test2
        self.c = Test
        self.col = c.arango_client_test.collection_one
        self.col2 = c.arango_client_test.collection_two
        doc = {'name': 'Bran', 'surname': 'Stark', '_key':'BranStark'}
        self.bran = self.col.save(doc)

    def test_field(self):
        i = self.c(name="Field1")
        self.assertEqual("Field1", i.name)
        i.surname = "Test"
        self.assertEqual("Test", i.surname)

    def test_collection_descriptor(self):
        self.assertEqual(self.test2._collection_name, "collection_two")
        self.assertEqual(self.c._collection_name, "collection_one")

    def test_get(self):
        o = self.c.get('BranStark')
        self.assertEqual(o.name, 'Bran')
        self.assertEqual(o.surname, 'Stark')
        self.assertEqual(o._key, 'BranStark')
        self.assertEqual(o._id, 'collection_one/BranStark')


    def test_doc(self):
        o = self.c.get('BranStark')
        self.assertEqual(o._doc(), {'name': 'Bran', 'surname': 'Stark'})
        self.assertEqual(o._key, 'BranStark')

    def test_put(self):
        o = self.c.get('BranStark')
        o.name = 'Brandon'
        o.sigil = 'Wolf'
        o.update()
        bran = self.c.get('BranStark')
        self.assertEqual(bran.name, 'Brandon')
        self.assertEqual(bran.sigil, 'Wolf')

    def test_patch(self):
        o = self.c.get('BranStark')
        o2 = self.c(name='Brandon', sigil='Wolf')
        new = o.patch(o2)
        bran = self.c.get('BranStark')
        self.assertEqual(bran.name, 'Brandon')
        self.assertEqual(bran.sigil, 'Wolf')
        self.assertEqual(new.sigil, 'Wolf')
        self.assertEqual(new.name, 'Brandon')

    def test_delete(self):
        o = self.c.get('BranStark')
        o.delete()
        self.assertRaises(KeyError, self.c.get, 'BranStark')

    def tearDown(self):
        try:
            self.col.delete('BranStark')
        except:
            pass



suite = unittest.TestLoader().loadTestsFromTestCase(TestODM)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
