# Project imports
from manager.Command.Utils import *


class Redirecting(CommandUtils):
    # redirect
    def command_redirect(self):
        if not self.args:
            self._invalid_usage()
        else:
            room_name = self.args[0]
            self._validate_room_name(room_name)
            room = self._get_room(room_name)

            if room:
                if not self.pm and room.name == self.room.name:
                    self._message(self._lang('ERROR_REDIRECT_SAME_ROOM').format(
                        username=self._user_color()
                    ))
                else:
                    self.db.store['redirects'][self.real_user.uid] = dict()
                    self.db.store['redirects'][self.real_user.uid][
                        self.bot.pm.name if self.pm else self.room.name
                    ] = room.name

                    self._message(self._lang('SUCCESS_REDIRECT').format(
                        room_name=self._room_link(room.name),
                        username=self._user_color()
                    ))
            else:
                self._message(self._lang('ERROR_NOT_CONNECTED').format(
                    room_name=self._room_link(room_name),
                    username=self._user_color()
                ))

    # unredirect
    def command_unredirect(self):
        if self.db.store['redirects'].get(self.real_user.uid):
            name = self.bot.pm.name if self.pm else self.room.name

            try:
                self.db.store['redirects'][self.real_user.uid].pop(name)

                # Delete user's redirect store
                if not self.db.store['redirects'][self.real_user.uid]:
                    self.db.store['redirects'].pop(self.real_user.uid)
            except:
                pass