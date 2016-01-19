import collections
import importlib
import six
from avocadopy.utils import is_id

_registry = {}

def class_for_name(name):
    parts = name.split(".")
    module_name = ".".join(parts[:-1])
    class_name = parts[-1]
    # load the module, will raise ImportError if module cannot be
    # loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot
    # be found
    c = getattr(m, class_name)
    return c

class CollectionName(object):

    value = None

    def __get__(self, obj, _type):
        return self.value if self.value is not None else _type.__name__.lower()

    def __set__(self, value):
        self.value = value


class DatabaseProvider(object):

    def __get__(self, obj, _type):
        ret = None
        try:
            if self._db is not None:
                ret = self._db
        except AttributeError:
            raise AttributeError("_db must be defined with the database object")

        return ret

    def __set__(self, value):
        self._db = value

class CollectionProvider(object):

    _collections = {}

    def __get__(self, obj, _type):
        if _type not in self._collections or self._collections[_type] is None:
            self._collections[_type] = _type._db[_type._collection_name]
        return self._collections[_type]

class OdmMeta(type):

    def __init__(cls, name, bases, dct):
        super(OdmMeta, cls).__init__(name, bases, dct)
        cls._attrs = getattr(cls, '_attrs', {}).copy()
        for k,v in cls.__dict__.items():
            is_attr = getattr(v.__class__, '_is_attr', False)
            name = None
            if is_attr is False:
                try:
                    is_attr = _registry[v]["_is_attr"]
                    name = _registry[v]["_name"]
                except:
                    pass
            else:
                name = getattr(v, '_name', None)

            if is_attr is True:
                cls._attrs[k] = {'name': name}

    def __setattr__(cls, name, value):
        is_attr = getattr(value.__class__, '_is_attr', False)
        if is_attr:
            _name = getattr(value, "_name", name)
            cls._attrs[name] = {'_is_attr': True, '_name': _name}
        type.__setattr__(cls, name, value)

def IsField(name=None, **kwargs):
    def wrapper(f):
        _registry[f] = {'_is_attr': True, '_name': name}
        return f
    return wrapper


class FieldMixin(object):
    _is_attr = True

    def __init__(self, name=None, readonly=False, **kwargs):
        self._name = name
        self._readonly = readonly

class SystemField(FieldMixin):

    def __get__(self, instance, _type):
        if instance is None:
            return self
        return instance._fields.get(self)

    def __set__(self, instance, value):
        instance._fields[self] = value

class Key(SystemField):
    pass

class Rev(SystemField):
    pass

class Id(SystemField):
    pass

class Base(six.with_metaclass(OdmMeta, object)):
    __metaclass__ = OdmMeta
    _collection_name = CollectionName()
    _db = DatabaseProvider()
    _collection = CollectionProvider()
    _fields = {}
    _key = Key()
    _rev = Rev()
    _id = Id()
    _fetch = True
    _eager = True
    _validate = True

    def __init__(self, _fetch=None, _eager=None, _validate=None, *args, **kwargs):
        self._collection = self._db[self._collection_name]
        self._edges = collections.defaultdict(dict)
        self._fields = {}
        self._rels = {}
        self._fetch = _fetch if _fetch is not None else self._fetch
        self._eager = _eager if _eager is not None else self._eager
        self._validate = _validate if _validate is not None else self._validate
        self._set_attributes(**kwargs)

    def _can_set(self, attr_name):
        attr = getattr(self.__class__, attr_name, None)
        ret = False
        if not isinstance(attr, collections.Callable):
            if not self._validate:
                ret = True
            elif isinstance(attr, FieldMixin) or attr_name in self._attrs:
                ret = True
        return ret

    def _set_attributes(self, **kwargs):
        for f in kwargs.keys():
            attr = getattr(self.__class__, f, None)
            if self._can_set(f):
                self.__setattr__(f, kwargs[f])

    def user_doc(self, include=[], include_edges=[], exclude=[]):
        exclude.extend(['_key', '_id', '_rev'])
        return self._doc(include, include_edges, exclude)

    def _doc(self, include=[], include_edges=[], exclude=[]):
        ignore = getattr(self, '__doc_ignore__', [])
        ignore.extend(exclude)
        ignore.append('_doc_ignore')
        ignore.append('_json_ignore')
        fields = [ k for k,v in self._attrs.items() if k not in ignore ]
        fields.extend(include_edges)
        fields.extend(include)
        fields = set(fields)
        ret = {}
        for field in fields:
            c_attr = getattr(self.__class__, field, None)
            attr = getattr(self, field)
            val = None
            try:
                val = c_attr._doc(self, full_object=(field in include_edges))
            except AttributeError:
                val = attr
            except:
                pass

            if val is not None:
                ret[field] = val

        return ret

    @classmethod
    def get(cls, id):
        ret = None
        if isinstance(id, (list, tuple)):
            objs = cls._collection.get_batched(id)
            ret = []
            for o in objs:
                ret.append(cls(**o))
        else:
            ret = cls(**cls._collection[str(id)])
        return ret

    def _update_keys(self, resp):
        keys = ['_id', '_key', '_rev']
        for k in keys:
            if k in resp:
                setattr(self, k, resp[k])

    def _save(self, update=False):
        ret = None
        self._save_rels()
        if self._id is not None or update:
            ret = self._collection.update(self._key, self._doc(), full_resp=True)
        else:
            ret = self._collection.save(self._doc(include=['_key']), full_resp=True)
        self._update_keys(ret)
        self._save_edges()
        return self

    def _save_edges(self):
        edges = self._list_attr(Edge)
        for e in edges:
            e.save(self)

    def _save_rels(self):
        for v in self._rels.values():
            for i in v:
                if i is not None:
                    i.save()

    def update(self):
        return self._save(True)

    def delete(self):
        self._collection.delete(self._id)
        self._delete_edges()

    def _delete_edges(self):
        edges = self._list_attr(Edge)
        for e in edges:
            e.delete(self)

    def save(self):
        return self._save()

    def patch(self, o):
        if self._id:
            self._collection.patch(o._doc(), self._id)
        return self.get(self._id)

    @classmethod
    def getall(cls):
        docs = cls._collection.documents()
        ret = []
        for d in docs:
            ret.append(cls(**d))
        return ret

    @classmethod
    def _list_attr(cls, _type):
        ret = []
        for f in [a for a in dir(cls) if not a.startswith("__")]:
            attr = getattr(cls, f)
            if isinstance(attr, _type):
                ret.append(attr)
        return ret

    @classmethod
    def example(cls, example):
        results = cls._collection.example(example)
        ret = []
        for r in results:
            ret.append(cls(**r))
        return ret


class Field(FieldMixin):

    default = None

    def __init__(self, default=None, **kwargs):
        super(Field, self).__init__(**kwargs)
        self.default = default

    def __get__(self, instance, _type):
        if instance is None:
            return self
        return instance._fields[self] if self in instance._fields else self.default

    def __set__(self, instance, value):
        instance._fields[self] = value

class Rel(FieldMixin):
    _is_attr = True

    def __init__(self, _type, auto_fetch=True, islist=False):
        self._type = _type
        self.islist = islist
        self.default = lambda: []
        self.auto_fetch = auto_fetch


    def __get__(self, instance, _type=None):
        if instance is None:
            return self
        ret = None
        if self in instance._rels:
            ret = instance._rels[self]
            if len(ret) > 0 and isinstance(ret[0], six.string_types):
                self._fetch()
                ret = instance._rels[self]
        else:
            ret = self.default()
            instance._rels[self] = ret
        l = len(ret)
        if not self.islist:
            ret = ret[0] if l > 0 else None
        return ret

    def __set__(self, instance, value):
        v = None
        ok = self._check_value(value)
        if not ok:
            raise ValueError("The given 'relationship' type does not match the expected type:", value, self._type)
        if isinstance(value, list):
            instance._rels[self] = value
        else:
            instance._rels[self] = [value]
        if self.auto_fetch:
            self._fetch(instance)

    def _fetch(self, instance):
        val = instance._rels[self]
        if len(val) > 0:
            if isinstance(val[0], six.string_types):
                instance._rels[self] = self._type.get(val)

    def _check_value(self, value):
        def check(v):
            return isinstance(v, self._type) or (
                isinstance(v, six.string_types) and v.startswith(self._type._collection_name))

        ret = True
        if self.islist and not isinstance(value, list):
            ret = False
        elif self.islist:
            for x in value:
                ret = ret and check(x)
        return ret

    def _doc(self, instance, full_object=False, **kwargs):
        ret = None
        v = self.__get__(instance)
        if self.islist:
            ret = []
            for i in v:
                val = i._id if not full_object else i._doc(**kwargs)
                ret.append(val)
        else:
            ret = v._id
        return ret


class Edge(object):
    _collection = None

    def __init__(self, collection_name, _type, islist=True):
        self.collection_name = collection_name
        self.type = _type
        self.islist = islist

    def get_type(self):
        val = self.type
        if isinstance(val, six.string_types):
            val = class_for_name(val)
            self.type = val
        return val

    def collection(self, obj):
        if self._collection is None:
            self._collection = obj._db[self.collection_name]
        return self._collection

    def _fetch(self, instance):
        ret = []
        if instance._id is not None:
            ids = self.collection(instance)[instance._id]
            instance._edges[self]['db'] = ids
            for i in ids:
                if i["_to"] == instance._id:
                    ret.append(self.get_type().get(i["_from"]))
                elif i["_from"] == instance._id:
                    ret.append(self.get_type().get(i["_to"]))
            if not self.islist:
                if len(ret) > 1:
                    raise LookupError("Found multiple edges for", instance._id, "in", self.collection(instance).name)
        return ret

    def __get__(self, instance, _type=None):
        if instance is None:
            return self
        value = None
        if self in instance._edges and 'value' in instance._edges[self]:
            value = instance._edges[self]['value']
        elif hasattr(instance, "_id"):
            value = self._fetch(instance)
            instance._edges[self]['value'] = value
        if not self.islist:
            value = value[0] if len(value) is 1 else None
        return value

    def __set__(self, instance, value):
        o = []
        if isinstance(value, self.get_type()):
            o = [value]
        elif isinstance(value, dict):
            o = [self.get_type()(**value)]
        else:
            o = value
        instance._edges[self]['value'] = o

    def save(self, instance):
        objs = []
        db = []
        self._fetch(instance)
        try:
            objs = instance._edges[self]['value']
            db = instance._edges[self]['db']
        except KeyError:
            pass
        for i in db:
            self.collection(instance).delete(i['_id'])
        for o in objs:
            if instance._id is None:
                instance.save()
            if o._id is None:
                o.save()
            self.collection(instance).save(instance._id, o._id, {})

    def delete(self, instance):
        ids = self.collection(instance)[instance._id]
        for i in ids:
            self.collection(instance).delete(i['_id'])
        if self in instance._edges:
            del instance._edges[self]


    def _doc(self, instance, full_object, **kwargs):
        ret = None
        v = self.__get__(instance)
        if self.islist:
            ret = []
            for i in v:
                val = i._id if not full_object else i._doc(**kwargs)
                ret.append(val)
        else:
            ret = i._id
        return ret

