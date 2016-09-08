# Python imports
import time
import urllib.request

# Project imports
from util.util import html_entities
from engine.chatango.util.constants import *
from engine.chatango.util.util import *
from engine.chatango.common.RoomMessage import RoomMessage
from engine.chatango.common.Stream.Utils import Utils as StreamUtils
from engine.chatango.stream.Room.Base import Base


class Utils(StreamUtils, Base):
    def message(self, msg, styled=True, html=True, split=False):
        """
        Send a message.

        @type msg: str
        @param msg: message

        @type styled: bool
        @param styled: True to send the message with the f and n tags, False otherwise

        @type html: bool
        @param html: True if HTML tags should be converted to HTML entities, False otherwise

        @type split: bool
        @param split: True if message should be split in more messages, False otherwise
        """
        msg = str(msg)
        user = self._manager.user

        if self._banned_words:
            for banned_word in self._banned_words:
                msg.replace(banned_word, html_entities(banned_word))

        if not html:
            msg = msg.replace("<", "&lt;").replace(">", "&gt;")
        if styled:
            msg = "<n" + user.name_color + "/>" + msg
            msg = "<f x%0.2i%s=\"%s\">" % (user.font_size, user.font_color, user.font_face) + msg

        if self._sleep:
            msg = '{sleep} {message}'.format(
                sleep='zzzz',
                message=msg
            )
        if split and len(msg) > self._max_length:
            if self._too_big_message == BIG_MESSAGE_CUT:
                self.message(msg[:self._max_length], styled, html, split)
            elif self._too_big_message == BIG_MESSAGE_MULTIPLE:
                while len(msg) > 0:
                    sect = msg[:self._max_length]
                    msg = msg[self._max_length:]
                    self.message(sect, styled, html, split)
            return
        self.send_command(
            "bmsg:tl2r",
            (
                msg
                + (self._mode if self._mode else '')
                # little hack to have different messages
                #+ '<{0}'.format(random.randint(0, 9))
                + ' ' * random.randint(0, 9)
            )
        )

        if self._ban_count == 0:
            self._ban_time = time.time()
        self._ban_count += 1

    def set_bg(self, color3x):
        """
        Set your background. The color must be an html color code.
        The image parameter takes a boolean to turn the picture off or on.
        Transparency is a float less than one or an integer between 1-100.
        """
        if self._premium:
            # Get the original settings
            #letter1 = self.mgr.user.uid[0]
            #letter2 = self.mgr.user.uid[1] if len(self.mgr.user.uid) > 1 else self.mgr.user.uid[0]
            #data = urllib.request.urlopen(
            #    "http://fp.chatango.com/profileimg/%s/%s/%s/msgbg.xml" % (
            #        letter1,
            #        letter2,
            #        self.user.uid
            #    )
            #).read().decode()
            #data = dict([
            #    x.replace('"', '').split("=")
            #    for x in re.findall('(\w+=".*?")', data)[1:]
            #])
            # Add the necessary shiz
            #data["p"] = self.mgr.password
            #data["lo"] = self.mgr.user.uid
            #if color3x:
            #    data["bgc"] = color3x
            # Send the request
            #data = urllib.parse.urlencode(data)
            try:
                urllib.request.urlopen(
                    "http://chatango.com/updatemsgbg?bgc=%s&hasrec=0"
                    "&p=%s&isvid=0&lo=%s&align=br&bgalp=100&useimg=1"
                    "&ialp=50&tile=1" % (
                        color3x,
                        self._manager.password,
                        self._manager.user.uid
                    )
                ).read()
            except:
                return False
            else:
                return True

    def set_bg_mode(self, mode):
        self.send_command("msgbg", str(mode))

    def set_recording_mode(self, mode):
        self.send_command("msgmedia", str(mode))

    def add_bad_word(self, word):
        if self.get_level(self._manager.user.uid) == 2:
            self._banned_words.append(word)
            self.send_command("setbannedwords", "403", ", ".join(self._banned_words))

    def remove_bad_word(self, word):
        if self.get_level(self._manager.user.uid) == 2:
            self._banned_words.remove(word)
            self.send_command("setbannedwords", "403", ", ".join(self._banned_words))

    def add_mod(self, user):
        """
        Add a moderator.

        @type user: User
        @param user: User to mod.
        """
        if self.get_level(self._manager.user.uid) == 2:
            self.send_command("addmod", user.uid)

    def remove_mod(self, user):
        """
        Remove a moderator.

        @type user: User
        @param user: User to demod.
        """
        if self.get_level(self._manager.user.uid) == 2:
            self.send_command("removemod", user.uid)

    def flag(self, message):
        """
        Flag a message.

        @type message: RoomMessage
        @param message: message to flag
        """
        self.send_command("g_flag", message.msgid)

    def flag_user(self, user):
        """
        Flag a user.

        @type user: User
        @param user: user to flag

        @rtype: bool
        @return: whether a message to flag was found
        """
        msg = self.get_last_message(user)
        if msg:
            self.flag(msg)
            return True
        return False

    def delete(self, message):
        """
        Delete a message. (Moderator only)

        @type message: RoomMessage
        @param message: message to delete
        """
        if self.get_level(self._manager.user.uid) > 0:
            self.send_command("delmsg", message.msgid)

    def raw_clear_user(self, unid):
        self.send_command("delallmsg", unid)

    def clear_user(self, user):
        """
        Clear all of a user's messages. (Moderator only)

        @type user: User
        @param user: user to delete messages of

        @rtype: bool
        @return: whether a message to delete was found
        """
        if self.get_level(self._manager.user.uid) > 0:
            msg = self.get_last_message(user)
            if msg:
                self.raw_clear_user(msg.unid)
            return True
        return False

    def clearall(self):
        """Clear all messages. (Owner only)"""
        if self.get_level(self._manager.user.uid) == 2:
            self.send_command("clearall")

    def raw_ban(self, uid, ip, unid):
        """
        Execute the block command using specified arguments.
        (For advanced usage)

        @type uid: str
        @param uid: user id
        @type ip: str
        @param ip: ip address
        @type unid: str
        @param unid: unid
        """
        self.send_command("block", unid, ip, uid)

    def ban(self, msg):
        """
        Ban a message's sender. (Moderator only)

        @type msg: RoomMessage
        @param msg: message to ban sender of
        """
        if self.get_level(self._manager.user.uid) > 0:
            self.raw_ban(msg.user.uid, msg.ip, msg.unid)

    def ban_user(self, user):
        """
        Ban a user. (Moderator only)

        @type user: User
        @param user: user to ban

        @rtype: bool
        @return: whether a message to ban the user was found
        """
        msg = self.get_last_message(user)
        if msg:
            self.ban(msg)
            return True
        return False

    def request_ban_list(self):
        """Request an updated ban list."""
        self.send_command("blocklist", "block", "", "next", "500")

    def request_unban_list(self):
        """Request an updated unban list."""
        self.send_command("blocklist", "unblock", "", "next", "500")

    def raw_unban(self, uid, ip, unid):
        """
        Execute the unblock command using specified arguments.
        (For advanced usage)

        @type uid: str
        @param uid: user id
        @type ip: str
        @param ip: ip address
        @type unid: str
        @param unid: unid
        """
        self.send_command("removeblock", unid, ip, uid)

    def unban(self, user):
        """
        Unban a user. (Moderator only)

        @type user: User
        @param user: user to unban

        @rtype: bool
        @return: whether it succeeded
        """
        rec = self.get_ban_record(user)
        if rec:
            self.raw_unban(rec[2].uid, rec[1], rec[0])
            return True
        else:
            return False

    # UTIL METHODS

    def get_level(self, uid):
        if uid == self._owner.uid:
            return 2
        if uid in [user.uid for user in self._mods]:
            return 1
        return 0

    def get_last_message(self, user=None):
        if user:
            try:
                i = 1
                while True:
                    msg = self._history[-i]
                    if msg.user == user:
                        return msg
                    i += 1
            except IndexError:
                return None
        else:
            try:
                return self._history[-1]
            except IndexError:
                return None
        return None

    def add_history(self, msg):
        """
        Add a message to history.

        @type msg: RoomMessage
        @param msg: message
        """
        self._history.append(msg)
        if len(self._history) > self._max_history_length:
            rest, self._history = (
                self._history[:-self._max_history_length],
                self._history[-self._max_history_length:]
            )
            for msg in rest:
                msg.detach()

    def get_ban_record(self, user):
        for record in self._ban_list:
            if record[2] == user:
                return record
        return None

    def get_message(self, mid):
        return self._msgs.get(mid)

    def create_message(self, msgid, **kw):
        if msgid not in self._msgs:
            msg = RoomMessage(msgid=msgid, **kw)
            self._msgs[msgid] = msg
        else:
            msg = self._msgs[msgid]
        return msg