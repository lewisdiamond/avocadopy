import requests
from avocadopy.collection import Collection, Edge
from avocadopy import base
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

class Database(base.List, base.Attr):

    """ArangoDB database"""

    _url_list_collections = "_api/collection"
    _url_graph = "_api/gharial"

    def __init__(self, url, session, name):
        """Initializes the db object

        :url: the base url for the db
        :session:the requests session object
        :name: the name of the db

        """

        self.url = urljoin(url, "/_db/" + name + "/")
        self._session = session
        self.name = name


        self._list_collections = requests.Request('GET',
            urljoin(self.url,
                    self._url_list_collections
                    )
            , params={'excludeSystem':'true'}
        ).prepare()


    def createCollection(self, name, options = {'type':2}):
        options['name'] = name
        resp = requests.post(urljoin(self.url, self._url_list_collections), json=options)

    def createGraph(self, definition):
        resp = requests.post(urljoin(self.url, self._url_graph), json=definition)
        return resp.status_code

    def collections(self):
        """ Gets a lists of available collections
        :returns: a list of available collection names

        """
        return self._list(self._session, self._list_collections, lambda x: {r['name']: r for r in x['result']})


    def __getitem__(self, item):
        """Get's a collection

        :item: collection name
        :returns: a collection

        """
        c = self.collections()
        if item in c:
            if c[item]["type"] is 2:
                return Collection(self.url, self._session, item)
            elif c[item]["type"] is 3:
                return Edge(self.url, self._session, item)
        else:
            raise KeyError("This collection does not exist", item)
