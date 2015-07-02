# avocadopy
A semi-functional piece of garbage Python client for ArangoDB


## How to use

1. Create a Base class
  ```
  from avocadopy import odm
  class ArangoBase(odm.Base):
    _db = None
     
    #Optionally, define what you want to be application IDs
    @property
    def id(self)
      return str(self._key) if self._key is not None else None
    
    @id.setter
      def id(self, value):
          self._key = str(value) if value is not None else None
  ```
1. Set the database this base class uses

  ```
  from avocadopy import Connection
  def init_arango(url, db):
      connection = Connection(url=url)
      db = connection[db]
      ArangoBase._db = db
  ```

## Contribute
Help me turn avocadopy from garbage to something functional.
- Add batching support (especially for edges)
- Add a pythonic AQL builder 
- Add configurable API endpoints (most useful for foxx endpoints)
- Correct any inconsistencies in the API
- Add type validation / support for custom validators
- Add transaction support
- Anything else you think would be useful
