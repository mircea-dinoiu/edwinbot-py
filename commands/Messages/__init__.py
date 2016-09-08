# Python imports
from time import strftime

# Project imports
from commands.Messages.Listening import *
from commands.Messages.Redirecting import *


class Messages(
    Listening,
    Redirecting
):
    # say
    def command_say(self):
        if not self.args:
            self._invalid_usage()
        else:
            self._message(self._htmlize(self.args_raw))

    # rsay
    def command_rsay(self):
        if not self.args:
            self._invalid_usage()
        else:
            args = self.args_raw.split(' ', 1)
            room_name = args[0].strip()
            try:
                message = args[1].strip()

                try:
                    room = self._get_room(room_name)
                    room.message(self._lang('USER_SAYS').format(
                        self._user_color(room=room, use_nick=False),
                        highlight(message, flags='i')
                    ))
                except:
                    self._message(self._lang('ERROR_NOT_CONNECTED').format(
                        room_name=self._room_link(room_name),
                        username=self._user_color()
                    ))
                    if self.log_level > 0:
                        raise
            except:
                self._invalid_usage()

    # announce
    def command_announce(self):
        if self.args:
            t = strftime('%I:%M %p, ')
            d = strftime('%d/%m/%Y')

            for room in self.bot.rooms:
                room.message(self._lang('ANNOUNCE').format(
                    self._user_color(use_nick=False),
                    t + d,
                    highlight(self.args_raw, flags='i')
                ))
        else:
            self._invalid_usage()