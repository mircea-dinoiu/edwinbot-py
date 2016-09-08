# Project imports
from engine.chatango.manager.Event.PMEvents import *
from engine.chatango.manager.Event.RoomEvents import *


class EventManager(RoomEvents, PMEvents):
    def on_raw(self, stream, raw):
        """
        Called before any command parsing occurs.

        @type stream: Stream
        @param stream: stream where the event occurred
        @type raw: str
        @param raw: raw command data
        """
        pass

    def on_event_called(self, stream, name, *args, **kw):
        """
        Called on every room-based event.

        @type stream: Stream
        @param stream: stream where the event occurred

        @type name: str
        @param name: the event
        """
        pass

    def on_premium_low(self, string):
        pass

    def on_init(self):
        """Called on init."""
        pass