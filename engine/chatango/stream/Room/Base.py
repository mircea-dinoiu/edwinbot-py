# Python imports
import socket

# Project imports
from engine.chatango.util.util import *
from engine.chatango.util.constants import *
from engine.chatango.common.Stream.Base import Base as StreamBase


class Base(StreamBase):
    def __init__(self, room, uid=None, server=None, port=None, manager=None):
        """
        Init function

        @type room: str
        @param room: name of room

        @type uid: str
        @param uid: user uid

        @type server: str
        @param server: server name

        @type port: int
        @param port: server port

        @type manager: StreamManager
        @param manager: stream manager
        """
        super().__init__()

        # Configurations
        self._max_history_length = 1000
        self._user_list_unique = True
        self._user_list_memory = 50
        self._user_list_event_unique = False
        self._too_big_message = BIG_MESSAGE_MULTIPLE
        self._max_length = 2600

        # Basic stuff
        self._name = room
        self._server = server or get_server(room)
        self._port = port or 443
        self._manager = manager

        # Under the hood
        self._reconnecting = False
        self._uid = uid or gen_uid()
        self._owner = None
        self._mods = set()
        self._message_queue = dict()
        self._history = list()
        self._user_list = list()
        self._connect_amount = 0
        self._user_count = 0
        self._users = dict()
        self._msgs = dict()
        self._aid = None
        self._i_log = None

        self._ban_list = list()
        self._unban_list = list()
        self._banned_words = list()
        self._recent_list = list()

        self._sleep = False
        self._flood = 0
        self._lang = None
        self._game = None
        self._games = dict()
        self._mode = None
        self._lock = True
        self._default = False
        self._login_fail = False
        self._rate_limit = 0
        self._rate_limit_first = True
        self._ban_count = 0
        self._ban_time = 0

        # Inited vars
        if self._manager:
            self.connect()

    def connect(self):
        """Connect to the server."""
        self._sock = socket.socket()
        self._sock.connect((self._server, self._port))
        self._sock.setblocking(False)
        self._first_command = True
        self._write_buffer = b""
        self.auth()
        self._ping_task = self._manager.set_interval(
            self._manager.ping_delay,
            self.ping
        )
        if not self._reconnecting:
            self._connected = True

    def reconnect(self):
        """Reconnect."""
        self._reconnecting = True
        if self._connected:
            self.disconnect(reconnect=False)
        self._uid = gen_uid()
        self.connect()
        self._reconnecting = False

    def disconnect(self, reconnect=True):
        """Disconnect from the server."""
        if reconnect and self._connect_amount:
            self.reconnect()
        else:
            self.fire_event("disconnect")
            if not self._reconnecting:
                self._connected = False
            for user in self._user_list:
                user.clear_session_ids(self)
            self._user_list = list()
            self._ping_task.cancel()
            self._sock.close()
            if not self._reconnecting:
                self._manager.rooms_dict.pop(self._name)

    def auth(self):
        """Authenticate."""
        self.send_command(
            "bauth",
            self._name,
            self._uid,
            self._manager.name,
            self._manager.password
        )

        self.set_write_lock(True)

    def ping(self):
        """Send a ping."""
        self.send_command("")
        self.fire_event("ping")