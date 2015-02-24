import requests
import base
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


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
        self.session = requests.Session()
        self.name = name
        self._list_documents = requests.Request('GET',
            urljoin(url,
                    self._url_document
                    )
            , params={'type':'id', 'collection':name}
        ).prepare()

    def _make_id(self, id):
        if not id.startswith(self.name):
            id = self.name + '/' + id
        return id


    def save(self, doc):
        req = requests.Request('POST',
            urljoin(self.url,
                    self._url_document
                    )
            , json=doc
            , params={'collection':self.name}
        ).prepare()
        resp = self.session.send(req)
        if resp.status_code >= 200 and resp.status_code < 300:
            return resp.json()['_id']
        elif resp.status_code == 400:
            raise ValueError("Invalid document")
        elif resp.status_code == 404:
            raise ValueError("Can't insert document in invalid collection")

    def update(self, id, doc):
        resp = requests.request('PUT',
                                urljoin(self.url,
                                        self._url_document) + '/' + self._make_id(id),
                                json=doc
                                ,params={'policy':'error'}
                                )
        if resp.status_code > 299:
            raise IOError(resp.status_code, resp.json()['errorMessage'])


    def delete(self, id):
        resp = requests.request('DELETE',
                               urljoin(self.url,
                                       self._url_document) + '/' + self._make_id(id)
                               )
        if resp.status_code > 299:
            raise IOError(resp.status_code, resp.json()['errorMessage'])




    def documents(self):
        """ Get a list of available databases names
        :returns: A list of database names
        """
        return self._list(self.session, self._list_documents, lambda x: [ i for i in x['documents']])

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
        resp = requests.request('GET', urljoin(self.url, self._url_document) + '/' + item)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            raise KeyError('Document does not exist')
        else:
            raise IOError(resp.json())

        ## 304 and 412 not yet supported
