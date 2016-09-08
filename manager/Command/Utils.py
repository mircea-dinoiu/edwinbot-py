# Python imports
import fnmatch

# Project imports
from manager.Command.Base import *


class CommandUtils(CommandBase):
    def _output_long_list(self, array, lang_key, fn_join, fn_get_format_params):
        """
        Create multiple messages from a list that exceeds the max chars per message when joined

        @type array: list
        @param array: array to join

        @type lang_key: str
        @param lang_key: language key to use for the message

        @type fn_join: function
        @param fn_join: function used to join the array

        @type fn_get_format_params: function
        @param fn_get_format_params: function that returns the params needed for format function
        """
        joined_string = fn_join(array)
        # If the encoded message is too long
        if len(joined_string) > 2900:
            first = True
            to_send = list()
            passed = 0
            # Get each element in order to print messages when
            # the element sub-lists have almost the maximum length that Chatango admits
            for each in array:
                passed += 1
                last = (passed == len(array))

                # Add element to the sub-list
                to_send.append(each)
                joined_string = fn_join(to_send)

                # If the message is too long, then pop the last element from the list, remake the message and print it
                if len(joined_string) > 2900:
                    to_send.pop()
                    joined_string = fn_join(to_send)
                    # If first, print information before
                    # else print the message as a simple list
                    if first:
                        format_params = fn_get_format_params(
                            count=len(array),
                            joined_string=joined_string + ('.' if last else ',')
                        )
                        self._message(self._lang(lang_key)[:-1].format(**format_params))
                        first = False
                    else:
                        self._message(joined_string + ('.' if last else ','))
                    # Prepare a new list for the next message
                    to_send = [each]
                # If this is the last array element, print the list and goodbye :D
                elif last:
                    joined_string = fn_join(to_send)
                    self._message(joined_string + '.')
        else:
            format_params = fn_get_format_params(
                count=len(array),
                joined_string=joined_string
            )
            self._message(self._lang(lang_key).format(**format_params))

    def _validate_username(self, username, exception=True):
        """
        Validate username by returning a valid flag or raising a ValidationError

        @type username: str
        @param username: username to validate

        @type exception: bool
        @param exception: flag to decide whether to throw exception or returning a boolean value

        @rtype: bool/None
        @return: bool if exception flag is True, otherwise raises ValidationError if username is invalid
        """
        if not username_is_valid(username):
            if exception:
                self._message(self._lang('ERROR_INVALID_USERNAME').format(
                    username=highlight(username, 'Gray'),
                    me=self._user_color()
                ))
                raise ValidationError
            else:
                return False

        if not exception:
            return True

    def _validate_room_name(self, room_name):
        """
        Validate room name by raising a ValidationError

        @type room_name: str
        @param room_name: room name to validate
        """
        if not room_name_is_valid(room_name):
            self._message(self._lang('ERROR_INVALID_ROOM_NAME').format(
                room_name=highlight(room_name, 'Gray'),
                me=self._user_color()
            ))
            raise ValidationError

    def _format_coins(self, coins, lang=None):
        """
        Format coins

        @type coins: int
        @param coins: coins

        @type lang: str
        @param lang: language to use

        @rtype: str
        @return: formatted coins
        """
        if lang is None:
            lang = self.lang

        return self.bot.format_coins(coins, lang)

    def _format_seconds(self, seconds, lang=None):
        """
        Format seconds

        @type seconds: float/int
        @param seconds: seconds

        @type lang: str
        @param lang: language to use

        @rtype: str
        @return: formatted seconds
        """
        if lang is None:
            lang = self.lang

        return self.bot.format_seconds(seconds, lang)

    def _game_name(self, string, is_class_name=False):
        """
        Get game name

        @type string: str
        @param string: string that can be used to find a game name

        @type is_class_name: bool
        @param is_class_name: True if you want to get the name according to the current room's language,
                              False if you want to get the class name

        @rtype: str
        @return: the game name
        """
        try:
            if is_class_name:
                return self._lang(string.upper() + '_GAME')
            else:
                return self.db.store['games'][string.lower()]
        except:
            if self.log_level > 0:
                raise
            return None

    def _room_color(self, room_name=None):
        """
        Get colored room name
        Uses the BotHelper method room_color

        @type room_name: str
        @param room_name: specified room name or nothing for the current room

        @rtype: str
        @return: colored room name
        """
        if not room_name:
            room_name = self.room.name

        return self.bot.room_color(room_name)

    def _room_link(self, name):
        """
        Get room link

        @type name: str
        @param name: room's name

        @rtype: str
        @return: a link to the room if the connection is a room connection, just the colored room otherwise
        """
        if self.pm:
            return self._room_color(name)
        else:
            return '<a target="_blank" href="http://{0}.chatango.com/group">{1}</a>'.format(
                name,
                self._room_color(name)
            )

    def _reset_vote_game_list(self):
        """Reset vote game list"""
        self.db.store['vote_game'][self.room.name] = dict()
        for game_key in self.db.store['games']:
            game_class_name = self.db.store['games'][game_key]
            self.db.store['vote_game'][self.room.name][game_class_name] = set()

    def _get_user_uid(self, username, room=None):
        """
        Get user id by username related to the current room

        @type username: str
        @param username: string that the username should start with or pattern for fnmatch or string with leading dot

        @type room: Room
        @param room: room object

        @rtype: str
        @return: user's uid
        """
        username = username.lower()

        if (
            '*' in username
            or '?' in username
            or '[' in username
            or ']' in username
        ):
            users = sorted(self.db.get_seen_entries())

            for user in users:
                if fnmatch.fnmatch(user, username):
                    return user

            return username
        else:
            if self.pm:
                return username
            else:
                if not room:
                    room = self.room

                if username.endswith('.'):
                    return username[:-1]

                user_ids = sorted([user.uid for user in room.get_user_list('all')])

                if username not in user_ids:
                    for name in user_ids:
                        if name.startswith(username):
                            return name

                return username

    def _invalid_usage(self):
        """
        Invalid command message
        """
        self._message(self._lang('ERROR_INVALID_COMMAND_USAGE').format(
            highlight(self.details['match'], 'Orange'),
            self._user_color(),
            highlight(self.prefix + 'man' + ' ' + self.details['match'], 'Blue')
        ))

    def _htmlize(self, string):
        """
        HTMLize string
        Removes the HTML tags from a string if the connection is PM's connection

        @type string: str
        @param string: the string to be filtered

        @rtype: str
        @return: HTML stripped string if the connection is PM's connection, the same string otherwise
        """
        if self.pm:
            return strip_html(string)
        else:
            return string

    def _get_room(self, substring):
        """
        Get room name using a substring as input

        @type substring: str
        @param substring: substring that has to be in the room name

        @rtype: Room
        @return: None if the bot is not connected to the room, else the room name
        """
        room = self.bot.get_room(substring)
        if not room:
            for each_room in self.bot.get_rooms():
                if substring.lower() in each_room.name:
                    return each_room

        return room