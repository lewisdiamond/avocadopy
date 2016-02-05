import unittest
import six
from avocadopy import connection
from avocadopy.tests import db, TestCase
from avocadopy import odm
try:
    import unittest.mock as mock
except ImportError:
    import mock

class TestRel(TestCase):

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
            name = odm.Field()
            t = odm.Rel(T)

        class L(odm.Base):
            _collection_name = "collection_two"
            _db = self.db
            name = odm.Field()
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
        t.save = mock.MagicMock(return_value=t, side_effect=t.save)
        l1.save()
        self.assertEqual(t.save.call_count, 1)
        l1.save()
        self.assertEqual(t.save.call_count, 1)

        l1_ = self.L.get(l1._id)
        self.assertEqual(l1_.name, l1.name)
        self.assertEqual(l1.t[0]._id, l1_.t[0]._id)
        self.assertEqual(l1.t[1]._id, l1_.t[1]._id)

        l1.t.remove(t)
        l1.save()

        l1_ = self.L.get(l1._id)
        self.assertEqual(l1_.name, l1.name)
        self.assertEqual(len(l1.t), 1)
        six.assertCountEqual(self, l1.t[0]._id, l1_.t[0]._id)

        t.delete()
        t2.delete()
        l1.delete()


suite = unittest.TestLoader().loadTestsFromTestCase(TestRel)


if __name__ == '__main__':
    _suite = unittest.TestSuite(suite)
    runner = unittest.TextTestRunner()
    runner.run(_suite)
