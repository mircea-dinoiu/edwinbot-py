# Python imports
import abc
import threading
import select
import socket
import time

# Project imports
from engine.chatango.stream.PM import PM


class Base:
    def __init__(self, name=None, password=None, pm=True, db=None):
        self._name = name
        self._password = password
        self._running = False
        self._tasks = set()
        self._rooms = dict()
        self._bgtime = 0
        self._db = db
        self._logger = None
        self._timer_resolution = 0.2
        self._ping_delay = 20
        self._delay = 0

        if pm:
            self._pm = PM(manager=self)
        else:
            self._pm = None

        self.start()

    def fire_event(self, name, stream=None, *args, **kwargs):
        if stream is None and name != 'event_called':
            getattr(self, 'on_' + name)(*args, **kwargs)
        else:
            getattr(self, 'on_' + name)(stream, *args, **kwargs)

        if name != 'event_called':
            self.fire_event('event_called', stream, name)

    def start(self):
        self.fire_event('init')
        self._running = True

        threading.Thread(
            target=self.cron_manager
        ).start()

        self.main()

    def get_connections(self):
        li = list(self._rooms.values())
        if self._pm:
            li.append(self._pm)
        return [c for c in li if c.sock is not None]

    def main(self):
        while self._running:
            try:
                conns = self.get_connections()
                socks = [x.sock for x in conns]
                w_socks = [x.sock for x in conns if x.write_buffer != b'']
                rd, wr, sp = select.select(socks, w_socks, [], self._timer_resolution)

                for sock in rd:
                    con = [c for c in conns if c.sock == sock][0]
                    try:
                        data = sock.recv(1024)
                        if len(data) > 0:
                            con.feed(data)
                        else:
                            con.disconnect()
                    except socket.error:
                        pass
                for sock in wr:
                    con = [c for c in conns if c.sock == sock][0]
                    try:
                        sent = b''
                        not_sent = b''
                        write_buffer = [each + b'\x00' for each in con.write_buffer.split(b'\x00')]

                        if len(write_buffer) > 1:
                            write_buffer.pop()

                        for each in write_buffer:
                            if str(each).startswith(("b'bmsg:tl2r:", "b'msg:")) and time.time() < con.wait_until:
                                not_sent += each
                            else:
                                sent += each
                                if str(each).startswith(("b'bmsg:tl2r:", "b'msg:")):
                                    con.wait_until = time.time()
                        size = sock.send(sent)
                        con.write_buffer = not_sent + sent[size:]
                    except socket.error:
                        pass
                self._tick()
            except KeyboardInterrupt:
                self.stop()
            except:
                pass

    def _tick(self):
        now = time.time()
        for task in set(self._tasks):
            if task.target <= now:
                task.function(*task.args, **task.kw)
                if task.is_interval:
                    task.target = now + task.timeout
                else:
                    self._tasks.remove(task)

    def stop(self):
        # Set the running flag to false
        self._running = False

        # Disconnect from chatrooms
        for conn in list(self._rooms.values()):
            conn.disconnect(reconnect=False)

    def restart(self):
        for conn in list(self._rooms.values()):
            conn.reconnect()
        self._running = True

    @abc.abstractmethod
    def cron_job(self, job):
        pass

    @abc.abstractmethod
    def cron_manager(self):
        pass