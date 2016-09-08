# Project imports
from manager.Command.Utils import *


class TheCannon(CommandUtils):
    def __format_ammunition(self):
        raw_ammunition = self.db.store['cannons'][self.user.uid]['ammunition']

        ammunition = highlight(raw_ammunition, 'Yellow')

        return ammunition

    def __format_target(self):
        raw_target = self.db.store['cannons'][self.user.uid]['target']

        if self._validate_username(raw_target, exception=False):
            target = self._user_color(raw_target)
        else:
            target = highlight(raw_target, 'Red')

        return target

    def __help_ammunition_command(self):
        return self._lang('CANNON_HELP_AMMUNITION').format(
            command='{prefix}{command} {arguments}'.format(
                prefix=highlight(self.prefix, 'Blue'),
                command=highlight('load', 'Blue'),
                arguments=highlight(
                    self.db.store['help']['load']['params'][self.lang][0].strip('<>'),
                    'Yellow'
                )
            )
        )

    def __help_target_command(self):
        return self._lang('CANNON_HELP_TARGET').format(
            command='{prefix}{command} {arguments}'.format(
                prefix=highlight(self.prefix, 'Blue'),
                command=highlight('target', 'Blue'),
                arguments=highlight(
                    self.db.store['help']['target']['params'][self.lang][0].strip('<>'),
                    'Yellow'
                )
            )
        )

    # cannon
    def command_cannon(self):
        store = self.db.store['cannons']

        ammunition = None
        target = None

        if store.get(self.user.uid):
            if store[self.user.uid].get('ammunition'):
                ammunition = self.__format_ammunition()
            if store[self.user.uid].get('target'):
                target = self.__format_target()

        if ammunition:
            ammunition_info = self._lang('CANNON_INFO_AMMUNITION').format(
                ammunition=ammunition
            )
        else:
            ammunition_info = '{0} {1}'.format(
                self._lang('ERROR_CANNON_NO_AMMUNITION').format(
                    me=self._user_color()
                ),
                self.__help_ammunition_command()
            )

        if target:
            target_info = self._lang('CANNON_INFO_TARGET').format(
                target=target
            )
        else:
            target_info = '{0} {1}'.format(
                self._lang('ERROR_CANNON_NO_TARGET').format(
                    me=self._user_color()
                ),
                self.__help_target_command()
            )

        self._message(self._lang('CANNON_INFO').format(
            ammunition_info=ammunition_info,
            target_info=target_info
        ))

    # load
    def command_load(self):
        if not self.args:
            self._invalid_usage()
        else:
            ammunition = self.args_raw

            store = self.db.store['cannons']
            if self.user.uid not in store:
                store[self.user.uid] = dict()

            store[self.user.uid]['ammunition'] = ammunition

    # target
    def command_target(self):
        if not self.args:
            self._invalid_usage()
        else:
            target = self._get_user_uid(self.args_raw)

            store = self.db.store['cannons']
            if self.user.uid not in store:
                store[self.user.uid] = dict()

            store[self.user.uid]['target'] = target

    # fire
    def command_fire(self):
        store = self.db.store['cannons']

        error_ammunition = False
        error_target = False

        if self.user.uid not in store:
            error_ammunition = True
            error_target = True
        else:
            if not store[self.user.uid].get('ammunition'):
                error_ammunition = True
            elif not store[self.user.uid].get('target'):
                error_target = True
            else:
                self._message(self._lang('CANNON_FIRE').format(
                    me=self._user_color(use_nick=False),
                    target=self.__format_target(),
                    ammunition=self.__format_ammunition()
                ))

        if error_ammunition:
            self._message('{0} {1}'.format(
                self._lang('ERROR_CANNON_NO_AMMUNITION').format(
                    me=self._user_color()
                ),
                self.__help_ammunition_command()
            ))
        elif error_target:
            self._message('{0} {1}'.format(
                self._lang('ERROR_CANNON_NO_TARGET').format(
                    me=self._user_color()
                ),
                self.__help_target_command()
            ))