class Base:
    def __init__(self):
        self._manager = None
        self._name = ''
        self._sock = None
        self._connected = False

        self._write_lock = False
        self._write_buffer = b""
        self._write_lock_buffer = b""
        self._read_buffer = b""

        self._first_command = True
        self._premium = False
        self._wait_until = 0
        self._ping_task = None
        self._delay = 0

    def connect(self):
        pass

    def disconnect(self, reconnect):
        pass

    def reconnect(self):
        pass

    def auth(self):
        pass

    def ping(self):
        pass

    def feed(self, data):
        """
        Feed data to the connection.

        @type data: bytes
        @param data: data to be fed
        """
        self._read_buffer += data
        while self._read_buffer.find(b"\x00") != -1:
            data = self._read_buffer.split(b"\x00")

            try:
                for food in data[:-1]:
                    self.process(food.decode('utf-8').rstrip("\r\n"))
            except:
                pass

            self._read_buffer = data[-1]

    def process(self, data):
        """
        Process a command string.

        @type data: str
        @param data: the command string
        """
        if data:
            self.fire_event("raw", data)
            data_array = data.split(":")
            cmd, args = data_array[0].lower(), data_array[1:]
            func = "on_receive_" + cmd
            if hasattr(self, func):
                try:
                    getattr(self, func)(args)
                except TypeError:
                    getattr(self, func)()
                except:
                    pass
            else:
                print('{stream_name}: it seems there is a command that is not handled: {data}'.format(
                    stream_name=self._name,
                    data=data
                ))

    def fire_event(self, name, *args, **kwargs):
        self._manager.fire_event(name, self, *args, **kwargs)

    def write(self, data):
        if self._write_lock:
            self._write_lock_buffer += data
        else:
            self._write_buffer += data

    def set_write_lock(self, lock):
        self._write_lock = lock
        if self._write_lock is False:
            self.write(self._write_lock_buffer)
            self._write_lock_buffer = b""

    def send_command(self, *args):
        """
        Send a command.

        @type args: [str, str, ...]
        @param args: command and list of arguments
        """
        if self._first_command:
            terminator = b"\x00"
            self._first_command = False
        else:
            terminator = b"\r\n\x00"
        self.write(":".join(args).encode() + terminator)