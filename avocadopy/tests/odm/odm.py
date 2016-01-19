import unittest
import itertools
from avocadopy import odm
from avocadopy import connection
from avocadopy.tests import db, TestCase

class TestODM(TestCase):

    def setUp(self):
        self.connection = c = connection.Connection()
        self.db = c[db]

        class Test(odm.Base):
            _collection_name = "collection_one"
            _db = self.db
            name = odm.Field()
            sigil = odm.Field()
            surname = odm.Field()

        Test.related_to = odm.Edge('edge', Test)
        Test.killed_by = odm.Rel(Test)


        class Test2(odm.Base):
            _attrs = {'name':{}}
            _collection_name = "collection_two"
            _db = self.db
            _name = None

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, value):
                if value == "Tyrion Lannister":
                    value = "Tyrion Targaryen"
                self._name = value

        self.test2 = Test2
        self.c = Test
        self.col = c.arango_client_test.collection_one
        self.col2 = c.arango_client_test.collection_two
        doc = {'name': 'Bran', 'surname': 'Stark', 'friend': 'Jamie Lannister',  '_key':'BranStark'}
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
        self.assertRaises(AttributeError, lambda: o.friend)
        self.assertEqual(o.user_doc(), {'name': 'Bran', 'surname': 'Stark'})
        self.assertEqual(o._key, 'BranStark')

        import pdb; pdb.set_trace()
        rickon = self.c(name="Rickon", surname="Stark")
        o.related_to = [rickon]

        jamie = self.c(name="Jamie", surname="Lannister", sigil="Lion")
        o.killed_by = [jamie]

        o.save()


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

    def test_property(self):
        o = self.test2()
        o.name = "Tyrion Lannister"
        self.assertEqual(o.name, "Tyrion Targaryen")
        o.save()

        doc = self.test2._collection[o._id]
        self.assertEqual(doc['name'], "Tyrion Targaryen")

        _o = self.test2.get(o._id)
        self.assertEqual(_o.name, "Tyrion Targaryen")

        o.name = 'Tyrion'
        o.update()
        doc = self.test2._collection[o._id]
        self.assertEqual(doc['name'], "Tyrion")

    def tearDown(self):
        try:
            self.col.delete('BranStark')
        except:
            pass


class TestBatch(unittest.TestCase):

    def setUp(self):
        self.connection = connection.Connection()
        self.db = self.connection[db]
        self.col1 = self.db.collection_one
        self.arya = {'name': 'Arya'}
        self.davos = {'name': 'Davos'}

    def test_batch_request_getall(self):
        arya = self.col1.save(self.arya)
        davos = self.col1.save(self.davos)
        try:
            resp = self.col1.get_batched([arya, davos])
            for r in resp:
                self.assertTrue(r['name'] in ("Arya","Davos"))
            self.assertEqual(len(resp), 2)
        except:
            raise
        finally:
            self.col1.delete(arya)
            self.col1.delete(davos)

        resp = self.col1.get_batched([arya, davos])
        self.assertEquals(len(resp), 0)

suite = list(
    itertools.chain(
        unittest.TestLoader().loadTestsFromTestCase(TestODM),
        unittest.TestLoader().loadTestsFromTestCase(TestBatch)
    )
)


if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
