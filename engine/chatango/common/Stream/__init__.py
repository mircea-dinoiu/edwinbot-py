# Project imports
from engine.chatango.common.Stream.Handlers import Handlers


class Stream(Handlers):
    # Name
    def get_name(self):
        return self._name

    # Manager
    def get_manager(self):
        return self._manager

    # Connected
    def get_connected(self):
        return self._connected

    # Write buffer
    def get_write_buffer(self):
        return self._write_buffer

    def set_write_buffer(self, write_buffer):
        self._write_buffer = write_buffer

    # Sock
    def get_sock(self):
        return self._sock

    # Wait until
    def get_wait_until(self):
        return self._wait_until

    def set_wait_until(self, wait_until):
        self._wait_until = wait_until + self._delay

    # Premium
    def get_premium(self):
        return self._premium

    name = property(get_name)
    manager = property(get_manager)
    connected = property(get_connected)
    write_buffer = property(get_write_buffer, set_write_buffer)
    sock = property(get_sock)
    wait_until = property(get_wait_until, set_wait_until)
    premium = property(get_premium)