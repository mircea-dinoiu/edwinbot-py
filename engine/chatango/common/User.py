# Project imports
from engine.chatango.util.constants import *
from lib.Cleverbot import Cleverbot


class NewUser:
    """Class that represents a user."""

    def __init__(self, uid, **kwargs):
        if uid == uid.lower():
            uid = uid.capitalize()
    
        self._uid = uid.lower()
        self._name = uid[0].upper() + uid[1:]
        self._sids = dict()
        self._msgs = list()
        self._name_color = "000"
        self._font_size = 12
        self._font_face = "0"
        self._font_color = "000"
        self._mbg = False
        self._mrec = False
        self._nick = None
        self._cb = Cleverbot()
        self._lang = None
        for attr, val in kwargs.items():
            if not val:
                continue
            setattr(self, "_" + attr, val)

    # Get uid
    def get_uid(self):
        return self._uid

    # Get name
    def get_name(self):
        return self._name

    # Get session ids
    def get_session_ids(self, room=None):
        if room:
            return self._sids.get(room, set())
        else:
            return set.union(*self._sids.values())

    # Get rooms
    def get_rooms(self):
        return self._sids.keys()

    # Get room names
    def get_room_names(self):
        return [room.name for room in self.get_rooms()]

    # Get font color
    def get_font_color(self):
        return self._font_color

    # Get font face
    def get_font_face(self):
        return self._font_face

    # Get font size
    def get_font_size(self):
        return self._font_size

    # Get name color
    def get_name_color(self):
        return self._name_color

    # Get mbg
    def get_mbg(self):
        return self._mbg

    # Get mrec
    def get_mrec(self):
        return self._mrec

    # Get, set nick
    def get_nick(self):
        return self._nick

    def set_nick(self, nick):
        self._nick = nick

    # Get Cleverbot
    def get_cleverbot(self):
        return self._cb

    # Get, set lang
    def get_lang(self):
        return self._lang

    def set_lang(self, lang):
        self._lang = lang

    # PROPERTIES

    uid = property(get_uid)
    name = property(get_name)
    session_ids = property(get_session_ids)
    rooms = property(get_rooms)
    room_names = property(get_room_names)
    font_color = property(get_font_color)
    font_face = property(get_font_face)
    font_size = property(get_font_size)
    name_color = property(get_name_color)
    mbg = property(get_mbg)
    mrec = property(get_mrec)
    nick = property(get_nick, set_nick)
    cb = property(get_cleverbot)
    lang = property(get_lang, set_lang)

    # UTIL METHODS

    def add_session_id(self, room, sid):
        if room not in self._sids:
            self._sids[room] = set()
        self._sids[room].add(sid)

    def remove_session_id(self, room, sid):
        try:
            self._sids[room].remove(sid)
            if len(self._sids[room]) == 0:
                del self._sids[room]
        except KeyError:
            pass

    def clear_session_ids(self, room):
        try:
            del self._sids[room]
        except KeyError:
            pass

    def has_session_id(self, room, sid):
        try:
            if sid in self._sids[room]:
                return True
            else:
                return False
        except KeyError:
            return False


class User(NewUser):
    def __new__(cls, uid, **kwargs):
        user = USERS.get(uid.lower())
        if not user:
            user = NewUser(uid, **kwargs)
            USERS[uid.lower()] = user
        return user