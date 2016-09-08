# Project imports
from commands.Rooms.Information.Chatango import *


class Information(Chatango):
    # room
    def command_room(self):
        if not self.args:
            if self.pm:
                self._invalid_usage()
                return
            room = self.room
            room_name = room.name
        else:
            room_name = self.args[0]
            self._validate_room_name(room_name)
            room = self._get_room(room_name)

            if room:
                room_name = room.name

        room_data = self.db.get_room_data(room_name)

        if not room_data:
            self._message(self._lang('ERROR_ROOM_NOT_IN_DB').format(
                self._room_color(room_name),
                self._user_color()
            ))
        else:
            message = self._lang('ROOM_INFO').format(
                room_name=self._room_link(room_name)
            )

            if room:
                message = self.db.get_config('message.line_breaker').join([
                    message,
                    self._lang('ROOM_INFO_DELAY').format(
                        delay=self._format_seconds(room.delay)
                    )
                ])

            message = self.db.get_config('message.line_breaker').join([
                message,
                self._lang('ROOM_INFO_FLAGS').format(
                    blacklisted=highlight(
                        self._lang('YES') if room_data['blacklisted'] == 1 else self._lang('NO'),
                        'Red' if room_data['blacklisted'] == 1 else 'Green'
                    ),
                    sleep=highlight(
                        self._lang('YES') if room_data['sleep'] == 1 else self._lang('NO'),
                        'Red' if room_data['sleep'] == 1 else 'Green'
                    )
                ),
                self._lang('ROOM_INFO_INITIATOR').format(
                    initiator=self._user_color(room_data['initiator'])
                ),
                self._lang('ROOM_INFO_LANGUAGE').format(
                    language=highlight(self.db.store['languages'][room_data['lang']], 'Yellow')
                )
            ])

            message += self.db.get_config('message.line_breaker')

            self._message(message)