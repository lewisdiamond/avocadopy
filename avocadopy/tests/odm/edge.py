import unittest
from avocadopy import connection
from avocadopy.tests import db, TestCase
from avocadopy import odm

class TestEdge(TestCase):

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



suite = unittest.TestLoader().loadTestsFromTestCase(TestEdge)

if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
