class RoomMessage:
    """Class that represents a room message."""

    def __init__(self, **kw):
        self._msgid = None
        self._time = None
        self._user = None
        self._body = None
        self._room = None
        self._raw = ""
        self._ip = None
        self._uid = ""
        self._unid = ""
        self._name_color = "000"
        self._font_size = 12
        self._font_face = "0"
        self._font_color = "000"
        for attr, val in kw.items():
            if val is None:
                continue
            setattr(self, "_" + attr, val)

    # ATTACH & DETACH

    def attach(self, room, msgid):
        """
        Attach the Message to a message id.
        
        @type msgid: str
        @param msgid: message id
        """
        if self._msgid is None:
            self._room = room
            self._msgid = msgid
            self._room.messages[msgid] = self
    
    def detach(self):
        """Detach the Message."""
        if self._msgid is not None and self._msgid in self._room.messages:
            del self._room.messages[self._msgid]
            self._msgid = None
    
    # SETTERS & GETTERS

    # Get id
    def get_id(self):
        return self._msgid

    # Get time
    def get_time(self):
        return self._time

    # Get user
    def get_user(self):
        return self._user

    # Get body
    def get_body(self):
        return self._body

    # Get IP
    def get_ip(self):
        return self._ip

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

    # Get uid
    def get_uid(self):
        return self._uid

    # Get room
    def get_room(self):
        return self._room

    # Get raw
    def get_raw(self):
        return self._raw

    # Get message unique ID
    def get_unid(self):
        return self._unid

    # PROPERTIES

    msgid = property(get_id)
    time = property(get_time)
    user = property(get_user)
    body = property(get_body)
    uid = property(get_uid)
    room = property(get_room)
    ip = property(get_ip)
    font_color = property(get_font_color)
    font_face = property(get_font_face)
    font_size = property(get_font_size)
    raw = property(get_raw)
    name_color = property(get_name_color)
    unid = property(get_unid)