# Python imports
import time

# Project imports
from manager.Bot.Base import Base
from engine.chatango.util.util import *
from util.render import *
from util.util import explode, is_anon
from util.localization import format_number
from util.time import format_seconds_to_long_string
from lib.Youtube import Video
from model.Game import Game


class Utils(Base):
    def seen(self, message, user, room):
        """
        Set seen entry

        @type message: str
        @param message: message string

        @type user: User
        @param user: the sender user object

        @type room: Room
        @param room: room where the message came from
        """
        if not is_anon(user.uid):
            self.db.set_seen(user.uid, {
                'message': message,
                'time': int(time.time()),
                'room': room.name
            })

    def listen(self, message, user, room):
        """
        Listen for a word in a chatroom message

        @type message: str
        @param message: message string

        @type user: User
        @param user: the sender user object

        @type room: Room
        @param room: room where the message came from
        """
        if user.uid != self.user.uid:
            active_users = room.get_user_list('active')
            for each in self.db.store['listen']:
                message = strip_html(message)
                if each in message.lower():
                    def replacement(match):
                        return highlight(match.group(1), 'Pink')

                    message = re.sub(
                        '(?i)({0})'.format(each),
                        replacement,
                        message
                    )

                    for uid in self.db.store['listen'][each]:
                        target_user = get_user(uid)
                        if target_user not in active_users:
                            target_data = self.db.get_user_data(uid)

                            if not target_data['parked']:
                                to_send = self.lang('LISTEN_NOTIFY', target_data['lang']).format(
                                    username=self.user_color(
                                        user=user,
                                        real_user=None,
                                        pm=True,
                                        use_nick=False,
                                        room=room
                                    ),
                                    room_name=self.room_color(room.name),
                                    message=highlight(message, flags='i'),
                                    listened=highlight(each, 'Pink')
                                )

                                self.pm.message(target_user, to_send)

    def redirect(self, stream, real_user, real_user_data, user, message, command):
        """
        Redirect stream messages to a room

        @type stream: Room/PM
        @param stream: the stream where the messages should be taken from

        @type real_user: User
        @param real_user: the unshapeshifted user object

        @type real_user_data: dict
        @param real_user_data: dictionary containing user data

        @type user: User
        @param user: maybe the shapeshifted user object, most likely the same as the real_user

        @type message: str
        @param message: received message

        @type command: dict
        @param command: data about the called command

        @rtype: Room
        @return: the room to redirect to
        """
        room = None
        if (
            self.db.store['redirects'].get(real_user.uid)
            and command['name'] != 'unredirect'
        ):
            if 'redirect' in real_user_data['restricted_commands'] or real_user_data['parked']:
                self.db.store['redirects'].pop(real_user.uid)
            elif self.db.store['redirects'][real_user.uid].get(stream.name):
                room = self.get_room(self.db.store['redirects'][real_user.uid][stream.name])
                if room:
                    room.message('{0}: {1}'.format(
                        highlight(user.name, 'Green' if (user in room.get_user_list()) else 'Gray'),
                        message
                    ))

        return room or stream

    def collect_whois_data(self, message, user):
        """
        Collect whois data

        @type message: RoomMessage
        @param message: RoomMessage object

        @type user: User
        @param user: the user to collect data for
        """
        if message.uid:
            if message.uid not in self.db.store['whois']:
                self.db.store['whois'][message.uid] = dict()
                self.db.store['whois'][message.uid]['uids'] = list()
                self.db.store['whois'][message.uid]['uids'].append(user.uid)
                self.db.store['whois'][message.uid]['last_update'] = int(time.time())

                if not is_anon(user.uid):
                    self.db.set_whois(message.uid, self.db.store['whois'][message.uid])
            elif user.uid not in self.db.store['whois'][message.uid]['uids']:
                    self.db.store['whois'][message.uid]['uids'].append(user.uid)
                    self.db.store['whois'][message.uid]['last_update'] = int(time.time())

                    save = {
                        'uids': self.db.store['whois'][message.uid]['uids'],
                        'last_update': self.db.store['whois'][message.uid]['last_update']
                    }
                    for uid in save['uids']:
                        if is_anon(uid):
                            save['uids'].remove(uid)

                    if save['uids']:
                        self.db.set_whois(message.uid, save)

    def https_or_youtube(self, room, message):
        """
        HTTPS or Youtube feature
        Checks if the message is a https or youtube link

        @type room: Room
        @param room: the room where the message came from

        @type message: str
        @param message: message string

        @rtype: bool
        @return: True if the message is a https or youtube link, False otherwise
        """
        url_obj = re.match(r'^(https|http)://([^ ]+)$', message, re.IGNORECASE)
        if url_obj:
            url = 'http://{0}'.format(url_obj.group(2))
            failure = False
            https = ('https' == url_obj.group(1).lower())

            try:
                video_id = None

                if 'youtube.com' in url.lower():
                    regex = re.findall(r'(\?|&)v=([^&\?/ ]+)', url, re.IGNORECASE)
                    video_id = regex[-1][1]
                elif 'youtube.be' in url.lower():
                    regex = re.findall(r'youtu\.be/([^&?/ ]+)', url, re.IGNORECASE)
                    video_id = regex[-1][0]

                video = Video(video_id)
                room.message(self.lang('YOUTUBE', room.lang).format(
                    highlight(video.title, flags='b'),
                    highlight(video.author, flags='u'),
                    video.url if https else ''
                ))
            except:
                failure = True

            if failure and https:
                room.message(url)

            return True
        else:
            return False

    def set_style(self):
        """
        Set user style for the bot

        Activates:
        - name color
        - font color
        - font face
        - font size
        - background
        - recording
        """
        self.set_name_color(self.db.get_config('bot.name_color'))
        self.set_font_color(self.db.get_config('bot.font_color'))
        self.set_font_face(self.db.get_config('bot.font_face'))
        self.set_font_size(self.db.get_config('bot.font_size'))
        self.enable_bg()
        self.enable_recording()

    def room_color(self, room_name):
        """
        Get a room color

        The color is:
            <Blue> if the room is a default room
            <Green> if the bot is connected to that room
            <Yellow> if the bot cannot talk on that room
            <Red> if the connection to the room was unsuccessful
            <Gray> if the bot is not connected to that room

        @type room_name: str
        @param room_name: the room name

        @rtype: str
        @return: colored room name
        """
        room_name = room_name.lower()

        room_obj = self.get_room(room_name)

        if room_obj:
            if room_obj.login_fail:
                color = 'Red'
            elif (
                room_obj.sleep
                or room_obj.lock
            ):
                color = 'Yellow'
            elif room_obj.default:
                color = 'Blue'
            else:
                color = 'Green'
        else:
            color = 'Gray'

        return highlight(room_name, color, 'u')

    def user_color(self, user, real_user, room, use_nick, pm):
        """
        Get user colored name or nick name if is set

        @type user: User
        @param user: User instance

        @type room: Room/None
        @param room: specify this to search a user in a certain room

        @type use_nick: bool
        @param use_nick: True if the function should use nick if set, False otherwise

        @type pm: bool
        @param pm: True if the user name should be colored for a PM message, False otherwise

        @rtype: str
        @return: colored user name
        """
        if use_nick and user.nick is None:
            user.nick = self.db.get_user_data(user.uid, 'nick')

        if use_nick and user.nick:
            return highlight(user.nick, 'Skin')
        else:
            if user == self.user:
                return highlight(user.name, 'Green')
            elif pm:
                return highlight(user.name, 'Green' if user == real_user else 'Gray')
            else:
                # Select the room
                return highlight(
                    user.name,
                    'Green' if (user in room.get_user_list('all')) else 'Gray'
                )

    def lang(self, key, lang):
        """
        Get language string

        @type key: str
        @param key: key for language string

        @type lang: str
        @param lang: language short name

        @rtype: str
        @return: requested message
        """
        if isinstance(key, str):
            if isinstance(lang, str):
                try:
                    variants = self.db.store['lang'][key]
                    if len(variants) > 1:
                        return random.choice(variants)[lang]
                    else:
                        return variants[0][lang]
                except:
                    if self.db.store['lang'].get(key):
                        error_message = 'Language specified is not valid'
                    else:
                        error_message = 'Language key is not defined'
                    raise KeyError(error_message)
            else:
                raise TypeError('Language should be string')
        else:
            raise TypeError('Key should be string')

    def game_check_room_user_count(self, room):
        """
        Check room user count for a game
        The game will be stopped if the unique users count in the room got below 10

        @type room: Room
        @param room: room to check
        """
        if isinstance(room.game, Game):
            if len(room.get_user_list()) < 10:
                room.game.stop()

            if room.game.error:
                room.game = None
                self.db.update_room(room.name, {
                    'game': None
                })

    def get_command(self, query, get_details=False):
        """
        Get a command by its name, its alias or by a substring

        @type query: str
        @param query: the command name to search for

        @type get_details: bool
        @param get_details: True to return more info about the query,
                            False otherwise (if True, a tuple will be returned)

        @rtype: str/dict
        @return: the original command name if it's documented, None otherwise
        """
        command_name = query.strip().lower()
        command = self.db.store['aliases'].get(command_name) or command_name
        details = {
            'query_type': 'shortcut'
        }

        if not command:
            command = None
        elif not command in self.db.store['help']:
            command_list = sorted(list(self.db.store['aliases']) + list(self.db.store['help']))

            for each_command in command_list:
                if each_command.startswith(command):
                    details['match'] = each_command
                    command = self.db.store['aliases'].get(each_command) or each_command
                    break

            if not command in self.db.store['help']:
                command = None
        else:
            details['match'] = command_name

            if command == command_name:
                details['query_type'] = 'command'
            else:
                details['query_type'] = 'alias'

        if get_details:
            return {
                'name': command,
                'details': details
            }
        else:
            return command

    def extract_command(self, message, extra_prefixes=''):
        """
        Get a command by its name, its alias or by a substring

        @type message: str
        @param message: the message to extract the command

        @type extra_prefixes: str
        @param extra_prefixes: string of extra prefixes specific to some commands

        @rtype: dict
        @return: the command data
        """
        data = {
            'name': None
        }

        if isinstance(message, str) and len(message) > 1:
            prefix = message[0]
            if (
                prefix in extra_prefixes
                or prefix in self.db.get_config('command.prefixes')
            ):
                array = message.split(' ', 1)
                command = array[0].lower().strip()[1:]
                command_data = self.get_command(command, get_details=True)

                if command_data:
                    data['prefix'] = prefix
                    data['name'] = command_data['name']

                    if 2 == len(array):
                        args_raw = array[1].strip()
                        args = explode(args_raw)
                    else:
                        args_raw = ''
                        args = list()

                    data['args'] = args
                    data['args_raw'] = args_raw
                    data['details'] = command_data['details']

        return data

    def indented_line(self, to, line):
        """
        Add indented line to string block

        @type to: str
        @param to: the string to add a line in

        @type line: str
        @param line: the line to add in the string

        @rtype: str
        @return: the string with the indented line added
        """
        if to:
            return self.db.get_config('message.line_breaker').join([
                to,
                '{indentation}{line}'.format(
                    indentation=(
                        self.db.get_config('message.indentation')
                        if not self.db.get_config('message.line_breaker') in to
                        else self.db.get_config('message.big_indentation')
                    ),
                    line=line
                )
            ])
        else:
            return line

    def indented_lines(self, lines=list(), to=''):
        """
        Add multiple indented lines to string block

        @type lines: list
        @param lines: the lines to add in the string

        @type to: str
        @param to: the string to add the lines in

        @rtype: str
        @return: the string with the indented lines added
        """
        for line in lines:
            to = self.indented_line(to, line)

        return to

    def format_coins(self, coins, lang):
        """
        Format coins

        @type coins: int
        @param coins: coins

        @type lang: str
        @param lang: language to use

        @rtype: str
        @return: formatted coins
        """
        apply_functions = [
            currency,
            lambda number: highlight(number, 'WashedPrune')
        ]

        return format_number(
            number=coins,
            lang=lang,
            many_text=self.lang('COINS', lang),
            one_text=self.lang('COIN', lang),
            apply_functions=apply_functions
        )

    def format_seconds(self, seconds, lang):
        """
        Format seconds

        @type seconds: int
        @param seconds: seconds

        @type lang: str
        @param lang: language to use

        @rtype: str
        @return: formatted seconds
        """
        return format_seconds_to_long_string(seconds, lang, self.db.store['lang'])