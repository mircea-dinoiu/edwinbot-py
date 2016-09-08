# Python imports
import threading
import time

# Project imports
from util.util import *
from util.render import *
from engine.chatango.util.util import *
from util.exceptions import ValidationError


class CommandBase:
    def __init__(
        self,
        command,
        real_user, user,
        real_user_data, user_data,
        msg_time,
        room=None, pm=None, manager=None
    ):
        """
        CommandHelper class containing util methods for a command

        @type command: dict
        @param command: dict containing command data (prefix, name, arguments)

        @type real_user: User
        @param real_user: original, unshapeshifted user class

        @type user: User
        @param user: user class (maybe shapeshifted)

        @type user_data: dict
        @param user_data: dictionary containing data like level, coins, etc. related to the current user

        @type msg_time: int
        @param msg_time: value to check the execution time for a command (useful for development)

        @type room: Room
        @param room: room object where the message came from

        @type pm: bool
        @param pm: boolean which tells the bot if the user is using the PM System or room to interact

        @type manager: Bot/BotHelper/RoomManager
        @param manager: the bot
        """
        self.bot = manager or room.manager
        self.db = self.bot.db
        self.room = room
        self.real_user = real_user
        self.user = user
        self.user_data = user_data
        self.msg_time = msg_time
        self.aliases = self.db.store['aliases']
        self.log_level = self.db.get_config('log_level')
        self.pm = pm
        self.lang = real_user_data['lang'] if pm else room.lang
        self.connection_name = 'PM System' if pm else room.name

        # Command specific
        self.name = command['name']
        self.prefix = command['prefix']
        self.details = command['details']
        self.args = command['args']
        self.args_raw = command['args_raw']
        self.man = self.db.store['help'][self.name]

        if (
            self.name != 'unpark' and self.user_data['parked']
            and not (
                self.user != self.real_user
                and self.name == 'shapeshift'
            )
        ):
            self._message(self._lang('ERROR_ACCOUNT_PARKED').format(
                me=self._user_color(),
                command=highlight(self.prefix + 'unpark', 'Blue')
            ))
        elif self.pm and not self.man['pm']:
            self._message(self._lang('ERROR_COMMAND_NOT_AVAILABLE_IN_PM'))
        elif self.room and not self.man['room']:
            self._message(self._lang('ERROR_COMMAND_NOT_AVAILABLE_IN_CHATROOMS').format(
                me=self._user_color()
            ))
        else:
            threading.Thread(
                target=self._launch,
                args=(command['name'], False)
            ).start()

    def _launch(self, command_name, trespass=True):
        """
        Launch a function and output the execution time if the log level is at least 1

        This function is called in thread

        @type command_name: str
        @param command_name: name of the command which is going to be executed

        @type trespass: bool
        @param trespass: True if no requirements checking wanted, False otherwise
        """
        if trespass or self._is_allowed():
            if self.log_level > 0 and not trespass:
                print('Command execution allowed')

            try:
                getattr(self, 'command_{0}'.format(command_name))()
            except ValidationError:
                pass

            execution_time = round(time.time()-self.msg_time, 3)

            if not trespass:
                if execution_time > self.db.get_config('command.max_execution_time') and not self.man['slow']:
                    print('Warning: the execution of {0} command took {1}s. Optimization needed.'.format(
                        self.name, execution_time
                    ))
                elif self.log_level > 0:
                    print('Command execution time: {execution_time}s'.format(
                        execution_time=execution_time
                    ))
            log_command(self)
        else:
            if self.log_level > 0:
                print('Command execution denied')

    def _message(self, msg, html=True):
        """Send a message to the PM or to a room"""
        if self.pm:
            self.bot.pm.message(self.real_user, msg, html=html)
        else:
            self.room.message(msg, html=html)

    def _is_allowed(self, second_check=False, command=None, silent=False):
        """
        Check if user is allowed to execute a specific command

        This function is designed to execute a first check if the

        @type second_check: bool
        @param second_check: True if you want to check permissions for the second command functionality

        @type command: str
        @param command: specify a command to check if user has the permission to use it

        @rtype: bool
        @return: True if user is allowed to access the command, False otherwise
        """
        command = command or self.name

        if command in self.user_data['restricted_commands']:
            return False

        cmd_req = self.db.store['help'][command]['raw']

        # Don't check for commands that have custom permissions check
        if cmd_req.get('autoCheck') is False and second_check is False:
            return True

        user_moderator = True if self.pm else (self.room.get_level(self.user.uid) > 0)

        # Is this the second check?
        if not second_check:
            # Is this an admin command?
            if cmd_req.get('admin') is True and not self.user_data['admin']:
                if not silent:
                    self._message(self._lang('ERROR_ADMIN_ONLY').format(
                        self._user_color()
                    ))
                return False
            # Is the command available just from a certain level?
            elif (
                cmd_req.get('level')
                and not (self.user_data['admin'] and not cmd_req.get('adminTrespass') is False)
            ):
                if self.user_data['level'] < cmd_req['level']:
                    # Check if moderator access trespasses level requirements
                    if cmd_req.get('orModerator'):
                        if not user_moderator and self.user_data['level'] < cmd_req['level']:
                            if not silent:
                                self._message(self._lang('ERROR_LEVEL_AT_LEAST_OR_MODERATOR').format(
                                    cmd_req['level'],
                                    self._user_color()
                                ))
                            return False
                    else:
                        if not silent:
                            self._message(self._lang('ERROR_LEVEL_AT_LEAST').format(
                                cmd_req['level'],
                                self._user_color()
                            ))
                        return False
            else:
                u = cmd_req.get('requiresUserModerator')
                b = cmd_req.get('requiresBotModerator')

                if u and b:
                    bot_moderator = True if self.pm else (self.room.get_level(self.bot.user.uid) > 0)

                    if not bot_moderator or not user_moderator:
                        if not silent:
                            self._message(self._lang('ERROR_BOTH_MODDED').format(
                                self._user_color(self.bot.user.uid),
                                self._user_color()
                            ))
                        return False
        # It seems yes :)
        else:
            # Level check
            if (
                self.user_data['level'] < cmd_req['level2']
                and not (self.user_data['admin'] and not cmd_req.get('adminTrespass') is False)
            ):
                # Check if moderator access trespasses level requirements
                if cmd_req.get('orModerator') and cmd_req.get('autoCheck') is not False:
                    if not user_moderator and self.user_data['level'] < cmd_req['level2']:
                        self._message(self._lang('ERROR_LEVEL_AT_LEAST_OR_MODERATOR').format(
                            cmd_req['level2'],
                            self._user_color()
                        ))
                        return False
                else:
                    self._message(self._lang('ERROR_LEVEL_AT_LEAST').format(
                        cmd_req['level2'],
                        self._user_color()
                    ))
                    return False

        return True

    def _user_color(self, uid=None, room=None, use_nick=None, pm=None):
        """
        Get user colored name or nick name if is set

        @type uid: str
        @param uid: specify uid of an user or his username, if not specified it will consider current user's uid

        @type room: Room
        @param room: specify this to search a user in a certain room

        @type use_nick: bool
        @param use_nick: True if the function should use nick if set, False otherwise

        @type pm: bool
        @param pm: True if the user name should be colored for a PM message, False otherwise

        @rtype: str
        @return: colored user name
        """
        # Get user by uid
        if uid is None:
            user = self.user
        else:
            user = get_user(uid)

        if use_nick is None:
            if uid is None:
                use_nick = True
            else:
                use_nick = False

        if pm is None:
            pm = True if self.pm else False

        if room is None:
            room = self.room

        return self.bot.user_color(
            user=user,
            real_user=self.real_user,
            room=room,
            use_nick=use_nick,
            pm=pm
        )

    def _lang(self, key, lang=None):
        """
        Use self._lang to get the desired message for current room's language instead of specifying the hole expression

        @type key: str
        @param key: language text key

        @type lang: str
        @param key: language key

        @rtype: str
        @return: requested message
        """
        if lang is None:
            lang = self.lang

        return self.bot.lang(key, lang)