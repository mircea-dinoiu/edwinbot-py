# Project imports
from manager.Command.Utils import *


class Streams(CommandUtils):
    # lang
    def command_lang(self):
        if self.args:
            lang = self.args[0].lower()
            if lang in self.db.store['languages']:
                if self.pm:
                    if self.user.lang != lang:
                        self._message(self._lang('SUCCESS_CHANGING_LANGUAGE').format(
                            highlight(self.db.store['languages'][lang], 'Yellow')
                        ))

                        self.user.lang = lang

                        self.db.update_user(self.real_user.uid, {
                            'lang': lang
                        })
                elif lang != self.room.lang:
                    if self._is_allowed(second_check=True):
                        self._message(self._lang('SUCCESS_CHANGING_LANGUAGE').format(
                            highlight(self.db.store['languages'][lang], 'Yellow')
                        ))

                        self.room.lang = lang

                        self.db.update_room(self.room.name, {'lang': lang})

                        if self.room.game:
                            self.room.game.reload(self.room)
        else:
            self._invalid_usage()

    # mode
    def command_mode(self):
        if not self.args:
            self._message(self._lang('ERROR_NO_MODE_SPECIFIED').format(
                self._user_color()
            ))
        else:
            mode = self.db.store['modes'].get(self.args[0].lower())

            if self.room.premium:
                self.room.mode = mode
            else:
                self._message(self._lang('ERROR_MODE_NEEDS_PREMIUM').format(
                    self._user_color(self.bot.user.uid),
                    self._user_color()
                ))

    # reconnect
    def command_reconnect(self):
        return
        if not self.args:
            if self.pm:
                if self._is_allowed(True):
                    self.bot.pm.reconnect()
                return
            room = self.room
            room_name = room.name
        else:
            room = self._get_room(self.args[0].lower())
            room_name = room.name if room else self.args[0].lower()
            if "*" != room_name:
                self._validate_room_name(room_name)

        if "*" == room_name:
            if self._is_allowed(True):
                for each_room in self.bot.rooms:
                    each_room.reconnect()
                if self.bot.pm:
                    self.bot.pm.reconnect()
        else:
            cmd_req = self.man['raw']

            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            elif (
                self.user_data['level'] >= cmd_req['level']
                or self.user_data['admin']
                or room.get_level(self.user.uid) > 0
            ):
                room.reconnect()
            else:
                self._message(self._lang('ERROR_LEVEL_AT_LEAST_OR_MODERATOR').format(
                    cmd_req['level'],
                    self._user_color()
                ))