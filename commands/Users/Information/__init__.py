# Project imports
from commands.Users.Information.Chatango import *


class Information(Chatango):
    # user
    def command_user(self):
        if not self.args:
            uid = self.user.uid
            user_data = self.user_data
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)
            user_data = self.db.get_user_data(uid)

        # User doesn't exist
        if 0 == user_data['level']:
            self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                self._user_color(uid),
                self._user_color()
            ))
            return

        parts = list()
        parts.append(self._lang('USER_INFO').format(
            username=self._user_color(uid)
        ))

        if user_data['nick']:
            parts.append(self._lang('USER_INFO_NICK').format(
                nick=self._user_color(uid, use_nick=True)
            ))

        parts.append(self._lang('USER_INFO_LEVEL_COINS').format(
            level=highlight(user_data['level'], 'Blue'),
            coins=highlight(currency(user_data['coins']), 'Yellow'),
            coins_spent=highlight(currency(user_data['coins_spent']), 'Yellow')
        ))

        parts.append(self._lang('USER_INFO_FLAGS').format(
            auto_delete=highlight(
                self._lang('YES' if uid in self.db.store['auto_delete'] else 'NO'),
                'Red' if uid in self.db.store['auto_delete'] else 'Green'
            ),
            ignored=highlight(
                self._lang('YES' if user_data['ignored'] else 'NO'),
                'Red' if user_data['ignored'] else 'Green'
            ),
            parked=highlight(
                self._lang('YES' if user_data['parked'] else 'NO'),
                'Blue' if user_data['parked'] else 'Gray'
            )
        ))

        if user_data['restricted_commands']:
            parts.append(self._lang('USER_INFO_RESTRICTED_COMMANDS').format(
                restricted_commands=', '.join([
                    highlight(command, 'Orange')
                    for command in user_data['restricted_commands']
                ])
            ))

        if user_data['restricted_games']:
            parts.append(self._lang('USER_INFO_RESTRICTED_GAMES').format(
                restricted_games=', '.join([
                    highlight(self._game_name(game, True), 'Orange')
                    for game in user_data['restricted_games']
                ])
            ))

        message = self.db.get_config('message.line_breaker').join(parts)
        message += self.db.get_config('message.line_breaker')

        self._message(message)