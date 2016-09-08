# Python imports
import socket

# Project imports
from engine.chatango.util.util import *
from engine.chatango.common.Stream.Base import Base as StreamBase


class Base(StreamBase):
    """Manages a connection with Chatango PM."""
    def __init__(self, manager):
        super().__init__()

        self._name = 'Private Messaging'
        self._manager = manager
        self._idle = 1
        self._auth_id = None
        self._block_list = set()
        self._unblock_list = set()
        self._contacts = None
        self._host = 'c1.chatango.com'
        self._port = 5222
        self._delay = 1.1

        self.connect()

    def connect(self):
        self._write_buffer = b""
        self._sock = socket.socket()
        self._sock.connect((self._host, self._port))
        self._sock.setblocking(False)
        self._first_command = True
        if self.auth():
            self._ping_task = self._manager.set_interval(
                self._manager.ping_delay,
                self.ping
            )
            self._connected = True

    def disconnect(self, reconnect=True):
        self.fire_event("pm_disconnect")
        self._connected = False
        self._sock.close()
        self._sock = None
        if reconnect:
            self.connect()

    def auth(self):
        self._auth_id = get_auth(self._manager.name, self._manager.password)
        if self._auth_id is None:
            self._sock.close()
            self.fire_event("login_fail")
            self._sock = None
            return False
        self.send_command("tlogin", self._auth_id, "2")
        self.set_write_lock(True)
        return True

    def ping(self):
        self.send_command("")
        self.fire_event("pm_ping")
        if self._idle != 0:
            self.set_idle()
            self._idle = 0

    def set_idle(self):
        self.send_command("idle:0")