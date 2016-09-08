# Project imports
from manager.Command.Utils import *


class Restrictions(CommandUtils):
    # restrictions
    def command_restrictions(self):
        if not self.args:
            target_uid = self.user.uid
        else:
            target_uid = self._get_user_uid(self.args[0])
            self._validate_username(target_uid)

        if target_uid == self.user.uid:
            user_data = self.user_data

            r_cmds = user_data['restricted_commands']
            r_games = user_data['restricted_games']

            # No restrictions for user
            if 0 == len(r_cmds) and 0 == len(r_games):
                self._message(self._lang('NO_RESTRICTIONS_FOR_YOU').format(
                    self._user_color(target_uid)
                ))
            # Just games restrictions
            elif 0 == len(r_cmds) and 0 != len(r_games):
                self._message(self._lang('RESTRICTED_GAMES_NO_COMMANDS_FOR_YOU').format(
                    self._user_color(target_uid),
                    ', '.join([
                        highlight(self._game_name(game, True), 'Orange')
                        for game in r_games
                    ])
                ))
            # Just command restrictions
            elif 0 != len(r_cmds) and 0 == len(r_games):
                self._message(self._lang('RESTRICTED_COMMANDS_NO_GAMES_FOR_YOU').format(
                    self._user_color(target_uid),
                    ', '.join([
                        highlight(command, 'Orange') for command in r_cmds
                    ])
                ))
            # Restrictions on both commands and games
            elif 0 != len(r_cmds) and 0 != len(r_games):
                self._message(self._lang('RESTRICTED_COMMANDS_AND_GAMES_FOR_YOU').format(
                    self._user_color(target_uid),
                    ', '.join([
                        highlight(command, 'Orange')
                        for command in r_cmds
                    ]),
                    ', '.join([
                        highlight(self._game_name(game, True), 'Orange')
                        for game in r_games
                    ])
                ))
        else:
            user_data = self.db.get_user_data(target_uid)

            # User doesn't exist
            if not user_data['level']:
                self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                    self._user_color(target_uid),
                    self._user_color()
                ))
                return

            r_cmds = user_data['restricted_commands']
            r_games = user_data['restricted_games']

            # No restrictions for user
            if 0 == len(r_cmds) and 0 == len(r_games):
                self._message(self._lang('NO_RESTRICTIONS').format(
                    self._user_color(target_uid)
                ))
            # Just games restrictions
            elif 0 == len(r_cmds) and 0 != len(r_games):
                self._message(self._lang('RESTRICTED_GAMES_NO_COMMANDS').format(
                    self._user_color(target_uid),
                    ', '.join([
                        highlight(self._game_name(game, True), 'Orange')
                        for game in r_games
                    ])
                ))
            # Just command restrictions
            elif 0 != len(r_cmds) and 0 == len(r_games):
                self._message(self._lang('RESTRICTED_COMMANDS_NO_GAMES').format(
                    self._user_color(target_uid),
                    ', '.join([
                        highlight(command, 'Orange')
                        for command in r_cmds
                    ])
                ))
            # Restrictions on both commands and games
            elif 0 != len(r_cmds) and 0 != len(r_games):
                self._message(self._lang('RESTRICTED_COMMANDS_AND_GAMES').format(
                    self._user_color(target_uid),
                    ', '.join([
                        highlight(command, 'Orange')
                        for command in r_cmds
                    ]),
                    ', '.join([
                        highlight(self._game_name(game, True), 'Orange')
                        for game in r_games
                    ])
                ))

    # restrict
    def command_restrict(self):
        try:
            args_arr = [arg.lower() for arg in self.args]

            # restrict command[s]|game[s]
            restrict_type = args_arr[0]
            assert(restrict_type in ['command', 'commands', 'game', 'games'])

            # restrict command[s]|game[s] key[s]
            keys = args_arr[1]

            # restrict command[s]|game[s] key[s] for
            assert('for' == args_arr[2])

            # restrict command[s]|game[s] key[s] for username
            uid = self._get_user_uid(args_arr[3])
            self._validate_username(uid)

            user_data = self.db.get_user_data(uid)

            # User doesn't exist
            if 0 == user_data['level']:
                self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                    self._user_color(uid),
                    self._user_color()
                ))
                return

            # User has a higher level than yours
            if (
                (
                    user_data['level'] >= self.user_data['level']
                    or user_data['admin']
                )
                and not self.user_data['admin']
            ):
                self._message(self._lang('ERROR_NO_ACCESS').format(
                    self._user_color()
                ))
                return

            if 'command' == restrict_type:
                command = explode(keys, ',')[0]

                real_command = self.bot.get_command(command)

                if real_command:
                    self._message(self._lang('SUCCESS_COMMAND_RESTRICTED').format(
                        highlight(real_command, 'Orange'),
                        self._user_color(uid),
                        self._user_color()
                    ))

                    self.db.update_user(uid, {
                        'restricted_commands': user_data['restricted_commands'] | {real_command}
                    })
                else:
                    self._message(self._lang('ERROR_COMMAND_NOT_EXISTING').format(
                        highlight(command, 'Orange'),
                        self._user_color()
                    ))
            elif 'commands' == restrict_type:
                good_list = set()
                bad_list = set()

                commands = set(explode(keys, ','))

                for command in commands:
                    real_command = self.bot.get_command(command)
                    if real_command:
                        good_list.add(real_command)
                    else:
                        bad_list.add(command)

                if bad_list:
                    if 1 == len(bad_list):
                        self._message(self._lang('ERROR_COMMAND_NOT_EXISTING').format(
                            highlight(bad_list.pop(), 'Orange'),
                            self._user_color()
                        ))
                    else:
                        self._message(self._lang('ERROR_COMMANDS_NOT_EXISTING').format(
                            ', '.join([
                                highlight(command, 'Orange')
                                for command in bad_list
                            ]),
                            self._user_color()
                        ))

                if good_list:
                    self.db.update_user(uid, {
                        'restricted_commands': user_data['restricted_commands'] | good_list
                    })
                    if len(good_list) == 1:
                        self._message(self._lang('SUCCESS_COMMAND_RESTRICTED').format(
                            highlight(good_list.pop(), 'Orange'),
                            self._user_color(uid),
                            self._user_color()
                        ))
                    else:
                        self._message(self._lang('SUCCESS_COMMANDS_RESTRICTED').format(
                            ', '.join([
                                highlight(command, 'Orange')
                                for command in good_list
                            ]),
                            self._user_color(uid),
                            self._user_color()
                        ))
            elif 'game' == restrict_type:
                game = explode(keys, ',')[0]

                game_name = self._game_name(game)

                if game_name:
                    self._message(self._lang('SUCCESS_GAME_RESTRICTED').format(
                        highlight(self._game_name(game_name, is_class_name=True) or game_name, 'Orange'),
                        self._user_color(uid),
                        self._user_color()
                    ))

                    self.db.update_user(uid, {
                        'restricted_games': user_data['restricted_games'] | {game_name}
                    })
                else:
                    self._message(self._lang('ERROR_GAME_INEXISTENT').format(
                        highlight(game, 'Orange'),
                        self._user_color()
                    ))
            elif 'games' == restrict_type:
                good_list = set()
                bad_list = set()

                games = set(explode(keys, ','))

                for game in games:
                    game_name = self._game_name(game)
                    if game_name:
                        good_list.add(game_name)
                    else:
                        bad_list.add(game)

                if bad_list:
                    if 1 == len(bad_list):
                        self._message(self._lang('ERROR_GAME_INEXISTENT').format(
                            highlight(bad_list.pop(), 'Orange'),
                            self._user_color()
                        ))
                    else:
                        self._message(self._lang('ERROR_GAMES_INEXISTENT').format(
                            ', '.join([
                                highlight(game, 'Orange')
                                for game in bad_list
                            ]),
                            self._user_color()
                        ))

                if good_list:
                    self.db.update_user(uid, {
                        'restricted_games': user_data['restricted_games'] | good_list
                    })

                    if 1 == len(good_list):
                        self._message(self._lang('SUCCESS_GAME_RESTRICTED').format(
                            highlight(self._game_name(good_list.pop(), is_class_name=True), 'Orange'),
                            self._user_color(uid),
                            self._user_color()
                        ))
                    else:
                        self._message(self._lang('SUCCESS_GAMES_RESTRICTED').format(
                            ', '.join([
                                highlight(self._game_name(game, is_class_name=True), 'Orange')
                                for game in good_list
                            ]),
                            self._user_color(uid),
                            self._user_color()
                        ))
        except ValidationError:
            pass
        except:
            self._invalid_usage()
            if self.log_level > 0:
                raise

    # unrestrict
    def command_unrestrict(self):
        try:
            args_arr = [arg.lower() for arg in self.args]

            # unrestrict * for username
            if (
                3 == len(args_arr)
                and '*' == args_arr[0]
                and 'for' == args_arr[1]
            ):
                uid = self._get_user_uid(args_arr[2])
                self._validate_username(uid)
                user_data = self.db.get_user_data(uid)

                # User doesn't exist
                if 0 == user_data['level']:
                    self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                        self._user_color(uid),
                        self._user_color()
                    ))
                # Remove all restrictions
                else:
                    self._message(self._lang('SUCCESS_ALL_RESTRICTIONS_REMOVED').format(
                        self._user_color(uid),
                        self._user_color()
                    ))

                    self.db.update_user(uid, {
                        'restricted_commands': set(),
                        'restricted_games': set()
                    })
            # unrestrict command[s]|game[s] key[s] for username
            else:
                # unrestrict command[s]|game[s]
                unrestrict_type = args_arr[0]
                assert(unrestrict_type in ['command', 'commands', 'game', 'games'])

                # unrestrict command[s]|game[s] key[s]
                keys = args_arr[1]

                # unrestrict command[s]|game[s] key[s] for
                assert('for' == args_arr[2])

                # unrestrict command[s]|game[s] key[s] for username
                uid = self._get_user_uid(args_arr[3])
                self._validate_username(uid)

                user_data = self.db.get_user_data(uid)

                # User doesn't exist
                if 0 == user_data['level']:
                    self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                        self._user_color(uid),
                        self._user_color()
                    ))
                    return

                # User has a higher level than yours
                if (
                    (
                        user_data['level'] >= self.user_data['level']
                        or user_data['admin']
                    )
                    and not self.user_data['admin']
                ):
                    self._message(self._lang('ERROR_NO_ACCESS').format(
                        self._user_color()
                    ))
                    return

                if 'command' == unrestrict_type:
                    command = keys.split(',')[0]

                    command_name = self.bot.get_command(command) or command

                    if command_name not in user_data['restricted_commands']:
                        # The command you have specified is not restricted
                        self._message(self._lang('ERROR_COMMAND_NOT_RESTRICTED').format(
                            highlight(command_name, 'Orange'),
                            self._user_color(uid),
                            self._user_color()
                        ))
                        return
                    else:
                        # The command was successfully unrestricted
                        self._message(self._lang('SUCCESS_COMMAND_UNRESTRICTED').format(
                            highlight(command_name, 'Orange'),
                            self._user_color(uid),
                            self._user_color()
                        ))

                        # Making the change in database
                        self.db.update_user(uid, {
                            'restricted_commands': user_data['restricted_commands'] - {command_name}
                        })
                elif 'commands' == unrestrict_type:
                    good_list = set()
                    bad_list = set()

                    commands = set(keys.split(','))

                    for command in commands:
                        command_name = self.bot.get_command(command) or command
                        if command_name in user_data['restricted_commands']:
                            good_list.add(command_name)
                        else:
                            bad_list.add(command_name)

                    if bad_list:
                        if 1 == len(bad_list):
                            self._message(self._lang('ERROR_COMMAND_NOT_RESTRICTED').format(
                                highlight(bad_list.pop(), 'Orange'),
                                self._user_color(uid),
                                self._user_color()
                            ))
                        else:
                            self._message(self._lang('ERROR_COMMANDS_NOT_RESTRICTED').format(
                                ', '.join([
                                    highlight(command, 'Orange')
                                    for command in bad_list
                                ]),
                                self._user_color(uid),
                                self._user_color()
                            ))

                    if good_list:
                        self.db.update_user(uid, {
                            'restricted_commands': user_data['restricted_commands'] - good_list
                        })
                        if 1 == len(good_list):
                            self._message(self._lang('SUCCESS_COMMAND_UNRESTRICTED').format(
                                highlight(good_list.pop(), 'Orange'),
                                self._user_color(uid),
                                self._user_color()
                            ))
                        else:
                            self._message(self._lang('SUCCESS_COMMANDS_UNRESTRICTED').format(
                                ', '.join([
                                    highlight(command, 'Orange')
                                    for command in good_list
                                ]),
                                self._user_color(uid),
                                self._user_color()
                            ))
                elif 'game' == unrestrict_type:
                    game = keys.split(',')[0]

                    game_name = self._game_name(game) or game

                    if game_name not in user_data['restricted_games']:
                        # The game you have specified is not restricted
                        self._message(self._lang('ERROR_GAME_NOT_RESTRICTED').format(
                            highlight(self._game_name(game_name, is_class_name=True) or game_name, 'Orange'),
                            self._user_color(uid),
                            self._user_color()
                        ))
                    else:
                        # Success unrestricting the game
                        self._message(self._lang('SUCCESS_GAME_UNRESTRICTED').format(
                            highlight(self._game_name(game_name, is_class_name=True) or game_name, 'Orange'),
                            self._user_color(uid),
                            self._user_color()
                        ))

                        # Making the change in database
                        self.db.update_user(uid, {
                            'restricted_games': user_data['restricted_games'] - {game_name}
                        })
                elif 'games' == unrestrict_type:
                    good_list = set()
                    bad_list = set()

                    games = set(keys.split(','))

                    for game in games:
                        game_name = self._game_name(game) or game
                        if game_name in user_data['restricted_games']:
                            good_list.add(game_name)
                        else:
                            bad_list.add(game_name)

                    if bad_list:
                        if 1 == len(bad_list):
                            game = bad_list.pop()
                            self._message(self._lang('ERROR_GAME_NOT_RESTRICTED').format(
                                highlight(self._game_name(game, is_class_name=True) or game, 'Orange'),
                                self._user_color(uid),
                                self._user_color()
                            ))
                        else:
                            self._message(self._lang('ERROR_GAMES_NOT_RESTRICTED').format(
                                ', '.join([
                                    highlight(self._game_name(game, is_class_name=True) or game, 'Orange')
                                    for game in bad_list
                                ]),
                                self._user_color(uid),
                                self._user_color()
                            ))

                    if good_list:
                        self.db.update_user(uid, {
                            'restricted_games': user_data['restricted_games'] - good_list
                        })
                        if 1 == len(good_list):
                            game = good_list.pop()
                            self._message(self._lang('SUCCESS_GAME_UNRESTRICTED').format(
                                highlight(self._game_name(game, is_class_name=True) or game, 'Orange'),
                                self._user_color(uid),
                                self._user_color()
                            ))
                        else:
                            self._message(self._lang('SUCCESS_GAMES_UNRESTRICTED').format(
                                ', '.join([
                                    highlight(self._game_name(game, is_class_name=True) or game, 'Orange')
                                    for game in good_list
                                ]),
                                self._user_color(uid),
                                self._user_color()
                            ))
        except ValidationError:
            pass
        except:
            self._invalid_usage()
            if self.log_level > 0:
                raise