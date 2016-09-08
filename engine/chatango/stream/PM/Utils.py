# Python imports
import re

# Project imports
from engine.chatango.common.Stream.Utils import Utils as StreamUtils
from engine.chatango.stream.PM.Base import Base


class Utils(StreamUtils, Base):
    def message(self, user, msg, html=True):
        self.set_active()
        self._idle = 0

        if not html:
            msg = msg.replace("<", "&lt;").replace(">", "&gt;").strip()

            message = "<n{name_color}/><m v=\"1\">"\
                      "<g xs0=\"0\">" \
                      "<g x{font_size}s{font_color}=\"{font_face}\">{message}</g>" \
                      "</g>"\
                      "</m>".format(
                          name_color=self._manager.user.name_color,
                          font_size=self._manager.user.font_size,
                          font_color=str(self._manager.user.font_color).lower(),
                          font_face=self._manager.user.font_face,
                          message=msg
                      )
        else:
            # Replace tags
            msg = msg.replace("<b>", "<B>")\
                .replace("<u>", "<U>")\
                .replace("<i>", "<I>")\
                .replace("</b>", "</B>")\
                .replace("</u>", "</U>")\
                .replace("</i>", "</I>")

            def replacement(match):
                return '<g x{font_size}s{font_color}="{font_face}">{message}</g>'.format(
                    font_size=self._manager.user.font_size,
                    font_face=self._manager.user.font_face,
                    font_color=match.group(1).lower(),
                    message=match.group(2)
                )

            msg = re.sub(
                r'<font color=\"#([0-9A-F]+)\">(.*?)</font>',
                replacement,
                msg
            )

            lines = msg.split(self._manager.db.get_config('message.line_breaker'))

            message = "<n{name_color}/><m v=\"1\">".format(name_color=self._manager.user.name_color)

            if len(lines) == 1:
                message += "<g xs0=\"0\">" \
                           "<g x{font_size}s{font_color}=\"{font_face}\">{message}</g>" \
                           "</g>".format(
                               font_size=self._manager.user.font_size,
                               font_color=str(self._manager.user.font_color).lower(),
                               font_face=self._manager.user.font_face,
                               message=lines[0].strip()
                           )
            else:
                for line in lines:
                    message += "<P><g xs0=\"0\">" \
                               "<g x{font_size}s{font_color}=\"{font_face}\">{message}</g>" \
                               "</g></P>".format(
                                   font_size=self._manager.user.font_size,
                                   font_color=str(self._manager.user.font_color).lower(),
                                   font_face=self._manager.user.font_face,
                                   message=line.strip()
                               )

            message += '</m>'

        self.send_command(
            "msg",
            user.uid,
            message
        )

    def test(self, user):
        self.send_command("connect", user.uid)

    def add_contact(self, user):
        if isinstance(self._contacts, set) and user not in self._contacts:
            self.send_command("wladd", user.uid)
            self._contacts.add(user)
            self.fire_event("pm_contact_add", user)

    def go_idle(self, args):
            self.send_command("idle", str(args))

    def remove_contact(self, user):
        if isinstance(self._contacts, set) and user in self._contacts:
            self.send_command("wldelete", user.uid)
            self._contacts.remove(user)
            self.fire_event("pm_contact_remove", user)

    def block(self, user):
        if user not in self._block_list:
            self.send_command("block", user.uid, user.uid, "S")
            self._block_list.add(user)
            self.fire_event("pm_block", user)

    def unblock(self, user):
        if user in self._block_list:
            self.send_command("unblock", user.uid)
            self._block_list.remove(user)
            self.fire_event("pm_unblock", user)

    def set_bg_mode(self, mode):
        self.send_command("msgbg", str(mode))

    def set_recording_mode(self, mode):
        self.send_command("msgmedia", str(mode))

    def set_active(self):
        self.send_command("idle:1")