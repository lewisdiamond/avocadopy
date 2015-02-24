

class List(object):

    """ Provides basic capabilities to get a list of items. """

    @staticmethod
    def _list(session, req, extractor):
        resp = session.send(req)
        ret = []
        if resp.status_code is 200:
            ret = extractor(resp.json())
        else:
            raise IOError("Unable to fetch data from the server")
        return ret



class Attr(object):
    def __getattr__(self, attr):
        return self[attr]


