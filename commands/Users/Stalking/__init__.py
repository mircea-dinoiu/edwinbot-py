# Project imports
from manager.Command.Utils import *


class Stalking(CommandUtils):
    # whereis
    def command_whereis(self):
        if not self.args:
            self._invalid_usage()
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)

            rooms = []

            for room in self.bot.get_rooms():
                if uid in room.get_user_uids() or uid in room.get_recent_list():
                    rooms.append(self._room_link(room.name))

            if len(rooms):
                self._message(self._lang('USER_IS_CONNECTED_TO').format(
                    self._user_color(uid),
                    len(rooms),
                    ', '.join(sorted(rooms))
                ))
            else:
                self._message(self._lang('ERROR_USER_NOT_FOUND').format(
                    self._user_color(uid)
                ))

    # whois
    def command_whois(self):
        if not self.args:
            uid = self.user.uid
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)

        entries = set()

        for shared_uid, data in self.db.store['whois'].items():
            user_uids = data['uids']
            if uid in user_uids:
                entries |= set(user_uids)

        entries -= {uid}

        if entries:
            entries = sorted(list(entries))

            def fn_join(array):
                return ', '.join([
                    self._user_color(each)
                    for each in array
                ])

            def fn_get_message_params(**kwargs):
                return {
                    'whois_list': kwargs['joined_string'],
                    'username': self._user_color(uid)
                }

            self._output_long_list(
                fn_join=fn_join,
                array=entries,
                lang_key='WHOIS',
                fn_get_format_params=fn_get_message_params
            )
        else:
            self._message(self._lang('ERROR_NOT_FOUND').format(
                self._user_color(uid)
            ))

    # seen
    def command_seen(self):
        if not self.args:
            self._invalid_usage()
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)

            seen = self.db.get_seen(uid)

            if seen:
                self._message(self._lang('SEEN').format(
                    username=self._user_color(uid),
                    room_name=self._room_link(seen['room']),
                    message=highlight(self._htmlize(seen['message']), flags='i'),
                    time_passed=highlight(
                        self._format_seconds(round(time.time() - int(seen['time']))),
                        'Blue'
                    )
                ))
            else:
                self._message(self._lang('ERROR_NOT_FOUND').format(
                    self._user_color(uid)
                ))