# Python imports
import abc


class Db:
    def __init__(self, db_params=None, store=None):
        self.utils = None
        self.store = None
        self.connection = None

        self._params = db_params
        self.store = store
        self.connect()

    @abc.abstractmethod
    def connect(self):
        pass
        
    def __getattr__(self, name):
        return getattr(self.utils, name)