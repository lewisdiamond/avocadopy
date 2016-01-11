import unittest
import connection
import odm

db = 'arango_client_test'


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
        self.assertItemsEqual(['collection_one', 'collection_two', 'edge'], cols.keys())

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
        print(self.edge[self.bran])

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

class TestEdge(unittest.TestCase):

    def setUp(self):
        self.connection = connection.Connection()
        self.db = self.connection[db]

        class Test(odm.Base):
            _collection_name = "collection_one"
            _db = self.db
            name = odm.Field()
            surname = odm.Field()

        Test.knows = odm.Edge("edge", Test, islist=False)

        self.Test = Test
        self.arya = Test(name="Arya", surname="Stark")
        self.sam = Test(name="Sam", surname="Tarly")
        self.jon = Test(name="Jon", surname="Snow")
        self.arya.save()
        self.sam.save()
        self.jon.save()

    def test_create_edge(self):
        self.arya.knows = self.sam
        self.jon.knows = self.sam

        self.arya.save()
        self.jon.save()
        arya = self.Test.get(self.arya._id)
        jon = self.Test.get(self.jon._id)

        self.assertEqual(arya.knows.name, 'Sam')
        self.assertEqual(jon.knows.name, 'Sam')


    def test_update_edge(self):
        self.assertEqual(self.arya.knows, None)
        self.arya.knows = self.sam
        self.arya.save()

        a_fetched = self.Test.get(self.arya._id)

        self.assertEqual(a_fetched.knows.name, 'Sam')
        a_fetched.knows = self.jon
        a_fetched.save()

        a_fetched = self.Test.get(self.arya._id)

        self.assertEqual(a_fetched.knows.name, 'Jon')


    def test_update_edge_list(self):
        self.assertEqual(self.arya.knows, None)

        class Person(odm.Base):
            _collection_name = "collection_one"
            _db = self.db
            knows = odm.Edge("edge", self.Test)

        arya = Person(name="Arya", surname="Stark")
        arya.knows = [self.jon]
        arya.save()

        arya_ = Person.get(arya._id)
        self.assertEqual(len(arya_.knows), 1)
        self.assertEqual(arya_.knows[0].name, 'Jon')
        arya_.knows.append(self.sam)
        arya_.save()

        arya_ = Person.get(arya._id)
        self.assertEqual(len(arya_.knows), 2)
        self.assertEqual(arya_.knows[0].name, 'Jon')
        self.assertEqual(arya_.knows[1].name, 'Sam')
        arya_.knows = [self.sam]
        arya_.save()

        arya_ = Person.get(arya._id)
        self.assertEqual(len(arya_.knows), 1)
        self.assertEqual(arya_.knows[0].name, 'Sam')
        arya_.delete()






    def tearDown(self):
        self.sam.delete()
        self.arya.delete()
        self.jon.delete()


class TestRel(unittest.TestCase):

    def setUp(self):
        self.connection = connection.Connection()
        self.db = self.connection[db]
        class T(odm.Base):
            _collection_name = "collection_one"
            _db = self.db
            name = odm.Field()

        class V(odm.Base):
            _collection_name = "collection_two"
            _db = self.db
            t = odm.Rel(T)

        class L(odm.Base):
            _collection_name = "collection_two"
            _db = self.db
            t = odm.Rel(T, islist=True)


        self.T = T
        self.V = V
        self.L = L


    def test_fetch_rel(self):
        t = self.T(name="test")
        v = self.V(name="test2")
        v.t = t
        v.save()
        _v = self.V.get(v._id)
        _t = _v.t
        self.assertEqual(_v.name, "test2")
        self.assertEqual(_v._id, v._id)
        self.assertNotEqual(_v, v)
        self.assertNotEqual(_t, t)
        self.assertEqual(_t.name, "test")

        _v.delete()
        _t.delete()

    def test_fetch_rel_list(self):
        t = self.T(name="content")
        t2 = self.T(name="content2")
        l1 = self.L(name="container")
        l2 = self.L(name="container2")

        l2.t.append(t2)
        self.assertEqual(len(l1.t), 0)
        l1.t = [t, t2]
        l1.save()

        l1_ = self.L.get(l1._id)
        self.assertEqual(l1_.name, l1.name)
        self.assertItemsEqual(l1.t[0]._id, l1_.t[0]._id)
        self.assertItemsEqual(l1.t[1]._id, l1_.t[1]._id)

        l1.t.remove(t)
        l1.save()

        l1_ = self.L.get(l1._id)
        self.assertEqual(l1_.name, l1.name)
        self.assertEqual(len(l1.t), 1)
        self.assertItemsEqual(l1.t[0]._id, l1_.t[0]._id)

        t.delete()
        t2.delete()
        l1.delete()


if __name__ == '__main__':
        unittest.main()
