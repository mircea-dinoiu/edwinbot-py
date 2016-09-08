class RoomEvents:
    def on_connect(self, room):
        """
        Called when connected to the room.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_reconnect(self, room):
        """
        Called when reconnected to the room.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_connect_fail(self, room):
        """
        Called when the connection failed.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_disconnect(self, room):
        """
        Called when the client gets disconnected.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_login_fail(self, room):
        """
        Called on login failure, disconnects after.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_flood_ban(self, room):
        """
        Called when either flood banned or flagged.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_flood_ban_repeat(self, room):
        """
        Called when trying to send something when flood banned.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_flood_warning(self, room):
        """
        Called when an overflow warning gets received.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_message_delete(self, room, user, message):
        """
        Called when a message gets deleted.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: owner of deleted message
        @type message: Message
        @param message: message that got deleted
        """
        pass

    def on_clear_all(self, room):
        """
        Called when chat owner clears all message

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_mod_change(self, room):
        """
        Called when the moderator list changes.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_mod_add(self, room, user):
        """
        Called when a moderator gets added.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_mod_remove(self, room, user):
        """
        Called when a moderator gets removed.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_message(self, room, user, message):
        """
        Called when a message gets received.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: owner of message
        @type message: Message
        @param message: received message
        """
        pass

    def on_banned_words_updated(self, room, words):
        """
        Called when a rooms banned words gets received.

        @type room: Room
        @param room: room where the event occurred

        @type words: List
        @param words: list of banned words
        """
        pass

    def on_history_message(self, room, user, message):
        """
        Called when a message gets received from history.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: owner of message
        @type message: Message
        @param message: the message that got added
        """
        pass

    def on_join(self, room, user):
        """
        Called when a user joins. Anonymous users get ignored here.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: the user that has joined
        """
        pass

    def on_leave(self, room, user):
        """
        Called when a user leaves. Anonymous users get ignored here.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: the user that has left
        """
        pass

    def on_ping(self, room):
        """
        Called when a ping gets sent.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_user_count_change(self, room):
        """
        Called when the user count changes.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_ban(self, room, user, target):
        """
        Called when a user gets banned.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: user that banned someone
        @type target: User
        @param target: user that got banned
        """
        pass

    def on_unban(self, room, user, target):
        """
        Called when a user gets unbanned.

        @type room: Room
        @param room: room where the event occurred
        @type user: User
        @param user: user that unbanned someone
        @type target: User
        @param target: user that got unbanned
        """
        pass

    def on_ban_list_update(self, room):
        """
        Called when a ban list gets updated.

        @type room: Room
        @param room: room where the event occurred
        """
        pass

    def on_unban_list_update(self, room):
        """
        Called when a unban list gets updated.

        @type room: Room
        @param room: room where the event occurred
        """
        pass