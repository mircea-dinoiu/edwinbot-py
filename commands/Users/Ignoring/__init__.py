# Project imports
from manager.Command.Utils import *


class Ignoring(CommandUtils):
    # ignored
    def command_ignored(self):
        ignored_users = []

        users = self.db.get_users()

        for username in users:
            if self.db.get_user_data(username, 'ignored') == 1:
                ignored_users.append(username)

        if ignored_users:
            def fn_join(array):
                return ', '.join([
                    self._user_color(each)
                    for each in array
                ])

            def fn_get_message_params(**kwargs):
                return {
                    'ignored_users': kwargs['joined_string']
                }

            self._output_long_list(
                fn_join=fn_join,
                array=ignored_users,
                lang_key='IGNORED_USERS',
                fn_get_format_params=fn_get_message_params
            )
        else:
            self._message(self._lang('IGNORED_USERS_EMPTY').format(
                me=self._user_color()
            ))

    # ignore
    def command_ignore(self):
        if not self.args:
            self._message(self._lang('ERROR_WHAT_USER_TO_IGNORE').format(
                self._user_color()
            ))
            return

        target_uid = self._get_user_uid(self.args[0])
        self._validate_username(target_uid)
        target_data = self.db.get_user_data(target_uid)

        if (
            (
                target_data['level'] >= self.user_data['level']
                or target_data['admin']
            )
            and not self.user_data['admin']
        ):
            self._message(self._lang('ERROR_NO_ACCESS').format(
                self._user_color()
            ))
            return

        if target_data['level']:
            self._message(self._lang('SUCCESS_IGNORE').format(
                self._user_color(target_uid),
                self._user_color()
            ))

            self.db.update_user(target_uid, {
                'ignored': 1
            })
        else:
            self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                self._user_color(target_uid),
                self._user_color()
            ))

    # unignore
    def command_unignore(self):
        if not self.args:
            self._message(self._lang('ERROR_WHAT_USER_TO_UNIGNORE').format(
                self._user_color()
            ))
            return

        target_uid = self._get_user_uid(self.args[0])
        self._validate_username(target_uid)
        target_data = self.db.get_user_data(target_uid)

        if (
            (
                target_data['level'] >= self.user_data['level']
                or target_data['admin']
            )
            and not self.user_data['admin']
        ):
            self._message(self._lang('ERROR_NO_ACCESS').format(
                self._user_color()
            ))
            return

        if target_data['level']:
            self._message(self._lang('SUCCESS_UNIGNORE').format(
                self._user_color(target_uid),
                self._user_color()
            ))

            self.db.update_user(target_uid, {
                'ignored': 0
            })
        else:
            self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                self._user_color(target_uid),
                self._user_color()
            ))