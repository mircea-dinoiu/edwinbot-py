# Python imports
import time
import urllib.parse

# Project imports
from engine.chatango.util.util import *

from engine.chatango.common.User import User
from engine.chatango.common.RoomMessage import RoomMessage
from engine.chatango.common.Structure import Structure

from engine.chatango.stream.Room.Utils import Utils
from engine.chatango.common.Stream.Handlers import Handlers as StreamHandlers


class Handlers(StreamHandlers, Utils):
    def on_receive_ok(self, args):
        if args[2] != "M":
            ##################################################################################
            # Happens often when the bot name contains a word banned on the chatroom
            #
            # We still want to read the banned words from that chatroom or the moderator list
            # but the bot won't be shown on the user list of the specific chatroom
            ##################################################################################
            self.fire_event("login_fail")
            #self.disconnect()
        self._owner = get_user(args[0])
        self._uid = args[1]
        self._aid = args[1][4:8]
        self._mods = set(map(lambda x: get_user(x), args[6].split(";")))
        self._i_log = list()

    def on_receive_denied(self, args):
        self.disconnect()
        self.fire_event("connect_fail")

    def on_receive_inited(self, args):
        self.send_command("g_participants", "start")
        self.send_command("getpremium", "1")
        self.send_command("getbannedwords")
        self.send_command("getratelimit")
        self.request_unban_list()

        self.request_ban_list()
        if self._connect_amount == 0:
            self.fire_event("connect")
            for msg in reversed(self._i_log):
                user = msg.user
                self.fire_event("history_message", user, msg)
                self.add_history(msg)
            del self._i_log
        else:
            self.fire_event("reconnect")
        self._connect_amount += 1
        self.set_write_lock(False)

    def on_receive_ratelimited(self, args):
        if self._rate_limit_first:
            self._rate_limit_first = False
        else:
            print('Warning: Check your settings, a message was not sent on {room_name}'.format(
                room_name=self._name,
            ))

    def on_receive_getratelimit(self, args):
        self._rate_limit = int(args[0])

    def on_receive_ratelimitset(self, args):
        self._rate_limit = int(args[0])

    def on_receive_bw(self, args):
        word = args[1] if args[1] != '' else args[2]
        words = urllib.parse.unquote(word).split(',')

        for each in words:
            if not each in self._banned_words:
                if len(each):
                    self._banned_words.append(each)

        for each in self._banned_words:
            if not each in words and words != ['']:
                self._banned_words.remove(each)

        self.fire_event("banned_words_updated", args)

    def on_receive_ubw(self, args):
        self.send_command("getbannedwords")

    def on_receive_premium(self, args):
        if float(args[1]) > time.time():
            self._premium = True
            if self._manager.user.mbg:
                self.set_bg_mode(1)
            if self._manager.user.mrec:
                self.set_recording_mode(1)
            self._manager.bgtime = args[1]
        else:
            self._premium = False

    def on_receive_mods(self, args):
        mod_names = args
        mods = set(map(lambda x: get_user(x), mod_names))
        pre_mods = self._mods
        for user in mods - pre_mods:
            #modded
            self._mods.add(user)
            self.fire_event("mod_add", user)
        for user in pre_mods - mods:
            #demodded
            self._mods.remove(user)
            self.fire_event("mod_remove", user)
        self.fire_event("mod_change")

    def on_receive_b(self, args):
        mtime = float(args[0])
        puid = args[3]
        ip = args[6]
        name = args[1]
        rawmsg = ":".join(args[9:])
        msg, n, f = clean_message(rawmsg)
        if name == "":
            name_color = None
            name = "#" + args[2]
            if name == "#":
                name = "!anon" + get_anon_id(n, puid)
        else:
            if n:
                name_color = parse_name_color(n)
            else:
                name_color = None
        i = args[5]
        unid = args[4]
        #Create an anonymous message and queue it because msgid is unknown.
        if f:
            font_color, font_face, font_size = parse_font(f)
        else:
            font_color, font_face, font_size = None, None, None
        msg = RoomMessage(
            time=mtime,
            user=User(name),
            body=msg,
            raw=rawmsg,
            uid=puid,
            ip=ip,
            name_color=name_color,
            font_color=font_color,
            font_face=font_face,
            font_size=font_size,
            unid=unid,
            room=self
        )
        self._message_queue[i] = msg

    def on_receive_u(self, args):
        temp = Structure(**self._message_queue)
        if hasattr(temp, args[0]):
            msg = getattr(temp, args[0])

            if msg.user != self._manager.user:
                msg.user._font_color = msg.font_color
                msg.user._font_face = msg.font_face
                msg.user._font_size = msg.font_size
                msg.user._name_color = msg.name_color

                if (
                    self._ban_count != 0
                    and time.time() - self._ban_time > 30
                ):
                    print('{room_name}: banned'.format(
                        room_name=self._name
                    ))
                    self._ban_count = 0
            else:
                if self._ban_count != 0:
                    self._ban_count -= 1
                    self._ban_time = time.time()

            del self._message_queue[args[0]]
            msg.attach(self, args[1])
            self.add_history(msg)
            self.fire_event("message", msg.user, msg)

    def on_receive_i(self, args):
        mtime = float(args[0])
        puid = args[3]
        ip = args[6]
        if ip == "":
            ip = None
        name = args[1]
        rawmsg = ":".join(args[9:])
        msg, n, f = clean_message(rawmsg)
        msgid = args[5]
        unid = args[4]
        if name == "":
            name_color = None
            name = "#" + args[2]
            if name == "#":
                name = "!anon" + get_anon_id(n, puid)
        else:
            if n:
                name_color = parse_name_color(n)
            else:
                name_color = None
        if f:
            font_color, font_face, font_size = parse_font(f)
        else:
            font_color, font_face, font_size = None, None, None
        msg = self.create_message(
            msgid=msgid,
            time=mtime,
            user=User(name),
            body=msg,
            raw=rawmsg,
            ip=ip,
            unid=unid,
            name_color=name_color,
            font_color=font_color,
            font_face=font_face,
            font_size=font_size,
            room=self
        )
        if msg.user != self._manager.user:
            msg.user._font_color = msg.font_color
            msg.user._font_face = msg.font_face
            msg.user._font_size = msg.font_size
            msg.user._name_color = msg.name_color
        self._i_log.append(msg)

    def on_receive_g_participants(self, args):
        args = ":".join(args)
        args = args.split(";")
        self._user_count = len(args)
        for data in args:
            data = data.split(":")
            name = data[3]
            uid = name.lower()
            if uid == "none":
                continue
            self._recent_list.append(uid)
            user = User(
                uid=name,
                room=self
            )
            user.add_session_id(self, data[0])
            self._user_list.append(user)

    def on_receive_participant(self, args):
        if args[0] == "0":
            #leave
            name = args[3]
            uid = name.lower()
            if uid == "none":
                return
            if uid in self._recent_list:
                self._recent_list.remove(uid)
            user = User(name)
            user.remove_session_id(self, args[1])
            self._user_list.remove(user)
            if (
                user not in self._user_list
                or not self._user_list_event_unique
            ):
                self.fire_event("leave", user)
        else:
            #join
            name = args[3]
            uid = name.lower()
            if uid == "none":
                return
            if not uid in self._recent_list:
                self._recent_list.append(uid)
            user = User(
                uid=name,
                room=self
            )
            user.add_session_id(self, args[1])
            if user not in self._user_list:
                do_event = True
            else:
                do_event = False
            self._user_list.append(user)
            if do_event or not self._user_list_event_unique:
                self.fire_event("join", user)

    def on_receive_show_fw(self, args):
        self._ban_count = 0
        self.fire_event("flood_warning")

    def on_receive_show_tb(self, args):
        self._ban_count = 0
        self.fire_event("flood_ban")

    def on_receive_tb(self, args):
        self._ban_count = 0
        self.fire_event("flood_ban_repeat")

    def on_receive_delete(self, args):
        msg = self.get_message(args[0])
        if msg:
            if msg in self._history:
                self._history.remove(msg)
                self.fire_event("message_delete", msg.user, msg)
                msg.detach()

    def on_receive_deleteall(self, args):
        for msgid in args:
            self.on_receive_delete([msgid])

    def on_receive_n(self, args):
        self._user_count = int(args[0], 16)
        self.fire_event("user_count_change")

    def on_receive_blocklist(self, args):
        self._ban_list = list()
        sections = ":".join(args).split(";")
        for section in sections:
            params = section.split(":")
            if len(params) != 5:
                continue
            if params[2] == "":
                continue
            self._ban_list.append((
                # unid
                params[0],
                # ip
                params[1],
                # target
                User(params[2]),
                # time
                float(params[3]),
                # src
                User(params[4])
            ))
        self.fire_event("ban_list_update")

    def on_receive_unblocklist(self, args):
        self._unban_list = list()
        sections = ":".join(args).split(";")
        for section in sections:
            params = section.split(":")
            if len(params) != 5:
                continue
            if params[2] == "":
                continue
            self._unban_list.append((
                # unid
                params[0],
                # ip
                params[1],
                # target
                User(params[2]),
                # time
                float(params[3]),
                # src
                User(params[4])
            ))
        self.fire_event("unban_list_update")

    def on_receive_blocked(self, args):
        if args[2] == "":
            return
        target = User(args[2])
        user = User(args[3])
        self._ban_list.append((args[0], args[1], target, float(args[4]), user))
        self.fire_event("ban", user, target)
        self.request_ban_list()

    def on_receive_unblocked(self, args):
        if args[2] == "":
            return
        target = User(args[2])
        user = User(args[3])
        self._unban_list.append((args[0], args[1], target, float(args[4]), user))
        self.fire_event("unban", user, target)
        self.request_unban_list()

    def on_receive_clearall(self, args):
        self.fire_event("clear_all")

    def on_receive_miu(self, args):
        pass

    def on_receive_updateprofile(self, args):
        pass

    def on_receive_annc(self, args):
        pass