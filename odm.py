import collections

database = None


def setup_database(connection, name):
    global database
    database = connection[name]


class CollectionName(object):

    def __get__(self, obj, type):
        return self.value if self.value is not none else self.__class__.__name__

    def __set__(self, value):
        self.value = value


class DatabaseProvider(object):

    def __get__(self, obj, type):
        global database
        ret = None
        try:
            if self._db is not None:
                ret = self._db
            else:
                ret = database
        except AttributeError:
            ret = database

    def __set__(self, value):
        self._db = value


class Base(object):
    _collection = CollectionName()
    _db = DatabaseProvider()

    def __init__(self, *args, **kwargs):
        for f in kwargs.keys():
            self.__setattr__(f, kwargs[f])

    def _doc(self):
        ignore = getattr(self, '__json_ignore__', [])
        ignore.append('__json_ignore__')
        fields = [ n for n in dir(self) if not n.startswith('_') and not isinstance(getattr(self, n), collections.Callable) and n not in ignore ]
        ret = {}
        for field in fields:
            ret[field] = getattr(self, field)
        return ret


    @classmethod
    def _get_db(cls, db=None):
        return db if db is not None else cls._db

    @classmethod
    def get(cls, id, db=None):
        db = cls._get_db(db)
        o = db[cls._collection][id]
        return cls(**o)

    def update(self, db=None):
        db = self._get_db(db)
        db[self._collection].update(self._id, self._doc())

    def delete(self, db=None):
        db = self._get_db(db)
        db[self._collection].delete(self._id)


class Field(object):

    def __init__(self):
        self.value = None;

    def __get__(self, obj, type):
        return self.value

    def __set__(self, obj, value):
        self.value = value

