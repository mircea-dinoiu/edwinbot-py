# Third Party imports
import redis

# Project imports
from model.Db import Db
from db.RedisDbUtils import RedisDbUtils


class RedisDb(Db):
    def connect(self):
        self.connection = redis.Redis(
            decode_responses=self._params['decode_responses'],
            password=self._params['password'],
            db=self._params['database'],
            host=self._params['host']
        )
        self.utils = RedisDbUtils(self)