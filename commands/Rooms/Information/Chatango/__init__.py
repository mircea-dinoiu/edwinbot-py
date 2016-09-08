# Project imports
from manager.Command.Utils import *


class Chatango(CommandUtils):
    # mods
    def command_mods(self):
        room_name = None

        if not self.args:
            if self.pm:
                self._invalid_usage()
                return
            room = self.room
        else:
            room_name = self.args[0]
            self._validate_room_name(room_name)
            room = self._get_room(room_name)

        if not room:
            self._message(self._lang('ERROR_NOT_CONNECTED').format(
                room_name=self._room_link(room_name),
                username=self._user_color()
            ))
            return

        mods = ', '.join([
            self._user_color(uid, room, pm=False)
            for uid in sorted(room.get_mod_uids())
        ])

        owner = self._user_color(
            room.get_owner_name(),
            room,
            pm=False
        )

        if mods:
            self._message(self._lang('OWNED_MODDED').format(
                room_name=self._room_link(room.name),
                owner=owner,
                mods=mods
            ))
        else:
            self._message(self._lang('OWNED_NOT_MODDED').format(
                room_name=self._room_link(room.name),
                owner=owner
            ))

    # bwords
    def command_bwords(self):
        if self.args:
            room_name = self.args[0]
            self._validate_room_name(room_name)
            room = self._get_room(room_name)

            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(self.args[0]),
                    me=self._user_color()
                ))
                return
        else:
            if self.pm:
                self._invalid_usage()
                return
            room = self.room

        words = room.banned_words

        if len(words):
            def fn_join(array):
                return ', '.join([
                    highlight(each, 'Yellow')
                    for each in array
                ])

            def fn_get_message_params(**kwargs):
                return {
                    'count': kwargs['count'],
                    'room_name': self._room_link(room.name),
                    'bwords_list': kwargs['joined_string']
                }

            self._output_long_list(
                fn_join=fn_join,
                array=words,
                lang_key='BANNED_WORDS',
                fn_get_format_params=fn_get_message_params
            )
        else:
            self._message(self._lang('NO_BANNED_WORDS').format(
                room_name=self._room_link(room.name),
                username=self._user_color()
            ))