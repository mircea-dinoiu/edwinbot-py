# Python imports
import time
import threading
import abc

# Project imports
from engine.chatango.common.Task import Task
from engine.chatango.common.User import User
from engine.chatango.stream.Room import Room
from engine.chatango.manager.Stream.Base import Base


class Utils(Base):
    def defer_to_thread(self, callback, func, *args, **kw):
        """
        Defer a function to a thread and callback the return value.

        @type callback: function
        @param callback: function to call on completion

        @type cbargs: tuple or list
        @param cbargs: arguments to get supplied to the callback

        @type func: function
        @param func: function to call
        """
        def f(f_func, f_callback, *f_args, **f_kwargs):
            ret = f_func(*f_args, **f_kwargs)
            self.set_timeout(0, f_callback, ret)

        threading.Thread(f, (func, callback) + args, kw).start()

    def set_timeout(self, timeout, function, *args, **kw):
        """
        Call a function after at least timeout seconds with specified arguments.

        @type timeout: int
        @param timeout: timeout
        @type func: function
        @param func: function to call

        @rtype: object
        @return: object representing the task
        """
        task = Task()
        task.manager = self
        task.target = time.time() + timeout
        task.timeout = timeout
        task.function = function
        task.is_interval = False
        task.args = args
        task.kw = kw
        self._tasks.add(task)
        return task

    def set_interval(self, timeout, function, *args, **kw):
        """
        Call a function at least every timeout seconds with specified arguments.

        @type timeout: int
        @param timeout: timeout
        @type func: function
        @param func: function to call

        @rtype: Task
        @return: the Task object
        """
        task = Task()
        task.manager = self
        task.target = time.time() + timeout
        task.timeout = timeout
        task.function = function
        task.is_interval = True
        task.args = args
        task.kw = kw
        self._tasks.add(task)
        return task

    def remove_task(self, task):
        """
        Cancel a task.

        @type task: object
        @param task: task to cancel
        """
        self._tasks.remove(task)

    def enable_bg(self):
        """Enable background if available."""
        user = User(self._name)
        user._mbg = True
        rooms = set(self._rooms.values())
        for room in rooms:
            room.set_bg_mode(1)

    def disable_bg(self):
        """Disable background."""
        user = User(self._name)
        user._mbg = False
        rooms = set(self._rooms.values())
        for room in rooms:
            room.set_bg_mode(0)

    def enable_recording(self):
        """Enable recording if available."""
        user = User(self._name)
        user._mrec = True
        rooms = set(self._rooms.values())
        for room in rooms:
            room.set_recording_mode(1)

    def disable_recording(self):
        """Disable recording."""
        user = User(self._name)
        user._mrec = False
        rooms = set(self._rooms.values())
        for room in rooms:
            room.set_recording_mode(0)

    def set_name_color(self, color3x):
        """
        Set name color.

        @type color3x: str
        @param color3x: a 3-char RGB hex code for the color
        """
        user = User(self._name)
        user._name_color = color3x

    def set_font_color(self, color3x):
        """
        Set font color.

        @type color3x: str
        @param color3x: a 3-char RGB hex code for the color
        """
        user = User(self._name)
        user._font_color = color3x

    def set_font_face(self, face):
        """
        Set font face/family.

        @type face: str
        @param face: the font face
        """
        user = User(self._name)
        user._font_face = face

    def set_font_size(self, size):
        """
        Set font size.

        @type size: int
        @param size: the font size (limited: 9 to 22)
        """
        if size < 9:
            size = 9
        if size > 22:
            size = 22
        user = User(self._name)
        user._font_size = size

    def join_room(self, room):
        """
        Join a room or return None if already joined.

        @type room: str
        @param room: room to join

        @rtype: Room or None
        @return: the room or nothing
        """
        room = room.lower()
        if room not in self._rooms:
            con = Room(room, manager=self)
            self._rooms[room] = con
            return con
        else:
            return None

    def leave_room(self, room):
        """
        Leave a room.

        @type room: str
        @param room: room to leave
        """
        room = room.lower()
        if room in self._rooms:
            print('{room_name}: leaving'.format(
                room_name=room
            ))
            con = self._rooms[room]
            con.disconnect(reconnect=False)

    def get_room(self, room):
        """
        Get room with a name, or None if not connected to this room.

        @type room: str
        @param room: room

        @rtype: Room
        @return: the room
        """
        room = room.lower()
        if room in self._rooms:
            return self._rooms[room]
        else:
            return None