import requests
import json
import base
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

class DocumentListIterator(object):
    def __init__(self, ids, collection):
        self.ids = ids
        self.iterator = self.ids.__iter__()
        self.collection = collection

    def __iter__(self):
        return self

    def __next__(self):
        item = next(self.iterator)
        return self.collection[item]

    next = __next__


class DocumentList(object):

    def __init__(self, ids, collection):
        self.ids = ids
        self.collection = collection

    def __getitem__(self, key):
        if type(key) is int:
            return self.collection[self.ids[key]]
        else:
            raise TypeError("List indices must be integers")

    def __len__(self):
        return len(self.ids)

    def __iter__(self):
        return DocumentListIterator(self.ids, self.collection)

    def __contains__(self, item_id):
        return item_id in self.ids

class Collection(base.List, base.Attr):

    """A collection"""
    _url_document = "_api/document"

    def __init__(self, url, session, name):
        """Initialize the connection

        :url: url to arango
        :session: the session to access the db
        :name: the name of the collection

        """

        self.url = url
        self.session = session
        self.name = name
        self._list_documents = requests.Request('GET',
            urljoin(url,
                    self._url_document
                    )
            , params={'type':'id', 'collection':name}
        ).prepare()

    def _make_id(self, id):
        if id and not id.startswith(self.name):
            id = self.name + '/' + id
        return id

    def createIndex(self, _type, fields, unique=False, sparse=False):
        resp = requests.post(urljoin(self.url,'_api/index'), params={
            'collection': self.name,
            },
            data=json.dumps({
                'type':_type,
                'fields': fields,
                'unique': unique,
                'sparse': sparse,
            })
        )

        if resp.status_code > 299:
            raise IOError("Failed to create index", resp.json())

    def save(self, doc, _key=None, full_resp=False):
        if _key is not None:
            doc['_key'] = _key
        req = requests.Request('POST',
            urljoin(self.url,
                    self._url_document
                    )
            , json=doc
            , params={'collection':self.name, 'createCollection': True}
        ).prepare()
        resp = self.session.send(req)
        if resp.status_code >= 200 and resp.status_code < 300:
            json_ = resp.json()
            del json_['error']
            return json_['_id'] if not full_resp else json_
        elif resp.status_code == 400:
            raise ValueError("Invalid document", doc)
        elif resp.status_code == 404:
            raise ValueError("Can't insert document in invalid collection")
        else:
            raise IOError(resp.json())

    def update(self, id, doc, full_resp=False):
        req = requests.Request('PUT',
                                urljoin(self.url,
                                        self._url_document) + '/' + self._make_id(id),
                                json=doc
                                ,params={'policy':'error'}
                                ).prepare()
        resp = self.session.send(req)
        if resp.status_code > 299:
            raise IOError(resp.status_code, resp.json()['errorMessage'])
        else:
            return resp.json() if full_resp else resp.json()['_id']


    def delete(self, id):
        req = requests.Request('DELETE',
                               urljoin(self.url,
                                       self._url_document) + '/' + self._make_id(id)
                               ).prepare()
        resp = self.session.send(req)
        if resp.status_code > 299:
            raise IOError(resp.status_code, resp.json()['errorMessage'])

    def patch(self, doc, id, keepNull=False, mergeObjects=False, full_resp=False):
        req = requests.Request('PATCH',
                               urljoin(self.url,
                                       self._url_document) + '/' + self._make_id(id),
                               json=doc,
                               params={'keepNull':keepNull, 'mergeObjects':mergeObjects}
                               ).prepare()
        resp = self.session.send(req)
        if resp.status_code > 299:
            raise IOError(resp.status_code, resp.json()['errorMessage'])
        else:
            return resp.json() if full_resp else resp.json()['_id']


    def documents(self):
        """ Get a list of all documents in the collection
        :returns: An iterable DocumentList object
        """
        items = self._list(self.session, self._list_documents, lambda x: x['documents'])
        return DocumentList(items, self)

    getall = documents

    def __contains__(self, item):
        """ used for 'doc' in collection
            Warning: Don't use this if you have a lot of documents
        :item: the id of the document
        :returns: True if the db exists, False otherwise
        :raises: IOError if unable to get an answer from the db

        """
        doc = self.documents()
        return item in dbs

    def __getitem__(self, item):
        """Get a database object

        :item: the document handle
        :returns: a document (dict)
        :raises: KeyError

        """
        item = item if item.startswith(self.name) else self.name + '/' + item
        req = requests.Request('GET', urljoin(self.url, self._url_document) + '/' + item).prepare()
        resp = self.session.send(req)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            raise KeyError('Document does not exist', item)
        else:
            raise IOError(resp.json())

        ## 304 and 412 not yet supported

    def example(self, example, skip=None, limit=None):
        body = {'collection': self.name,
                'example': example,
                'skip': skip,
                'limit': limit
                }
        req = requests.Request('PUT', urljoin(self.url, '_api/simple/by-example'), json=body).prepare()
        resp = self.session.send(req)
        if resp.status_code < 300 and resp.status_code > 199:
            return resp.json()['result']
        else:
            raise IOError("Failed to fetch documents by example: ", example, resp.json()['errorMessage'])

class Edge(base.List, base.Attr):

    """A collection"""
    _url_edges = "_api/edges/"
    _url_edge = "_api/edge/"

    def __init__(self, url, session, name):
        """Initialize the connection

        :url: url to arango
        :session: the session to access the db
        :name: the name of the collection

        """
        self.session = session
        self.url = url
        self._edges_url = urljoin(url, self._url_edges) + name
        self._edge_url = urljoin(url, self._url_edge)
        self.name = name


    def get(self, item, direction='any'):
        req = requests.Request('GET'
                               , self._edges_url
                               , params={'vertex':item,'direction':direction}
                               ).prepare()
        items = self._list(self.session, req, lambda x: x['edges'])
        return items


    def save(self, _from, to, doc=None, full_resp=False):
        req = requests.Request('POST'
                                , self._edge_url
                                , params={
                                    'collection': self.name,
                                    'createCollection': True,
                                    'from': _from,
                                    'to':to
                                }
                                ,json=doc).prepare()
        resp = self.session.send(req)

        if resp.status_code > 299:
            raise IOError("Failed to create edge", resp.json()["errorMessage"])
        else:
            ret = resp.json()
            del ret['error']
            return ret if full_resp else ret['_id']

    def delete(self, item):
        req = requests.Request('DELETE',
                                self._edge_url + item).prepare()
        resp = self.session.send(req)
        if resp.status_code > 299:
            raise IOError("Failed to delete edge", resp.json()["errorMessage"])
        else:
            return self


    def __getitem__(self, item):
        """Get a database object

        :item: the document handle
        :returns: a document (dict)
        :raises: KeyError

        """
        return self.get(item)
