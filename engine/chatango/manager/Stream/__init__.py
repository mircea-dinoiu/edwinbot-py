# Project imports
from engine.chatango.common.User import User
from engine.chatango.manager.Stream.Utils import Utils


class StreamManager(Utils):
    """Class that manages multiple connections."""

    # User
    def get_user(self):
        return User(self._name)

    # Name
    def get_name(self):
        return self._name

    # Password
    def get_password(self):
        return self._password

    # Rooms
    def get_rooms(self):
        return set(self._rooms.values())

    # Rooms dict
    def get_rooms_dict(self):
        return self._rooms

    # Room names
    def get_room_names(self):
        return set(self._rooms.keys())

    # PM
    def get_pm(self):
        return self._pm

    # DB
    def get_db(self):
        return self._db

    # Logger
    def get_logger(self):
        return self._logger

    def set_logger(self, logger):
        self._logger = logger

    # Ping delay
    def get_ping_delay(self):
        return self._ping_delay

    user = property(get_user)
    name = property(get_name)
    password = property(get_password)
    rooms = property(get_rooms)
    rooms_dict = property(get_rooms_dict)
    room_names = property(get_room_names)
    pm = property(get_pm)
    db = property(get_db)
    logger = property(get_logger, set_logger)
    ping_delay = property(get_ping_delay)