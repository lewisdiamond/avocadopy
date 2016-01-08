import requests
from avocadopy import database
from avocadopy import base
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


class Connection(base.List, base.Attr):

    """Base object used to connect to Arango"""

    _url_list_databases = "/_db/_system/_api/database"

    def __init__(self, url="http://localhost:8529/", auth=('root', 'admin')):
        """Initialize the connection

        :url: url to arango
        :auth: tuple of username and password

        """

        self.url = url
        self.auth = auth
        self.session = requests.Session()
        self.session.auth = auth

        self._list_databases = requests.Request('GET',
            urljoin(url,
                    self._url_list_databases
                    )
        ).prepare()

    def databases(self):
        """ Get a list of available databases names
        :returns: A list of database names
        """
        return self._list(self.session, self._list_databases, lambda x: x['result'])

    def __contains__(self, item):
        """ used for 'db' in connection

        :item: the name of the database
        :returns: True if the db exists, False otherwise
        :raises: IOError if unable to get an answer from the db

        """
        dbs = self.databases()
        return item in dbs


    def __getitem__(self, item):
        """Get a database object

        :item: the name of the database
        :returns: a database object
        :raises: KeyError

        """
        ret = None
        if item in self:
            ret = database.Database(self.url, self.session, item)
        else:
            raise KeyError('Database does not exist on server')

        return ret
