

class List(object):

    """ Provides basic capabilities to get a list of items. """

    @staticmethod
    def _list(session, req, extractor):
        resp = session.send(req)
        ret = []
        if resp.status_code > 199 and resp.status_code < 300:
            ret = extractor(resp.json())
        else:
            raise IOError("Unable to fetch data from the server", resp.json())
        return ret



class Attr(object):
    def __getattr__(self, attr):
        return self[attr]


