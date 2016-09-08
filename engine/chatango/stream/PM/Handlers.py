# Python imports
import time

# Project imports
from engine.chatango.util.util import *
from engine.chatango.common.User import User
from engine.chatango.common.Stream.Handlers import Handlers as StreamHandlers
from engine.chatango.stream.PM.Utils import Utils


class Handlers(StreamHandlers, Utils):
    def on_receive_idleupdate(self, args):
        pass

    def on_receive_time(self, args):
        pass

    def on_receive_status(self, args):
        pass

    def on_receive_seller_name(self, args):
        pass

    def on_receive_ok(self, args):
        self.set_write_lock(False)
        self.send_command("wl")
        self.send_command("getblock")
        self.send_command("getpremium", "1")
        self.set_idle()
        self.fire_event("pm_connect")

    def on_receive_wl(self, args):
        self._contacts = set()
        for i in range(len(args) // 4):
            name, last_on, is_on, idle = args[i * 4: i * 4 + 4]
            user = User(name)
            self._contacts.add(user)
        self.fire_event("pm_contact_list_receive")

    def on_receive_block_list(self, args):
        self._block_list = set()
        for name in args:
            if name == "":
                continue
            self._block_list.add(User(name))

    def on_receive_unblock_list(self, args):
        self._unblock_list = set()
        for name in args:
            if name == "":
                continue
            self._unblock_list.add(User(name))

    def on_receive_denied(self, args):
        self.disconnect()
        self.fire_event("login_fail")

    def on_receive_msg(self, args):
        user = User(args[0])

        # Clean message
        body = strip_html(":".join(args[5:]))\
            .replace("&lt;", "<")\
            .replace("&gt;", ">")\
            .replace("&quot;", "\"")\
            .replace("&apos;", "'")\
            .replace("&amp;", "&")

        self.fire_event("pm_message", user, body)

    def on_receive_msgoff(self, args):
        user = User(args[0])
        body = strip_html(":".join(args[5:]))
        self.fire_event("pm_offline_message", user, body)

    def on_receive_wlonline(self, args):
        self.fire_event("pm_contact_online", User(args[0]))

    def on_receive_wloffline(self, args):
        self.fire_event("pm_contact_offline", User(args[0]))

    def on_receive_connect(self, args):
            self.fire_event("pm_connect1", User(args[0]), args[1], args[2])

    def on_receive_premium(self, args):
        if float(args[1]) > time.time():
            self._premium = True
            if self._manager.user.mbg:
                self.set_bg_mode(1)
            if self._manager.user.mrec:
                self.set_recording_mode(1)
        else:
            self._premium = False

    def on_receive_kickingoff(self, args):
        self.disconnect()