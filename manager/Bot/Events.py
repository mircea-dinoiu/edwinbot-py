# Python imports
import traceback
import random
import threading
import time

# Project imports
from manager.Log import Log
from manager.Bot.Utils import Utils
from util.games import *
from util.render import highlight
from util.util import is_anon
from engine.chatango.util.util import get_user
from engine.chatango.manager.Event import EventManager
from engine.chatango.common.RoomMessage import RoomMessage
from manager.Command import Command
from model.Game import Game


class Events(Utils, EventManager):
    def on_event_called(self, stream, name, *args, **kw):
        if (
            self.db.get_config('log_level') > 71
            and name not in ['raw', 'ping', 'pm_ping', 'user_count_change']
        ):
            print(name)

    def on_init(self):
        # Set up the logger
        self.logger = Log(self.db.get_config('log_directory'), 'commands', on_terminal=False)

        self.set_style()

        # Joining the rooms
        rooms = self.db.get_rooms(False)

        for room in rooms:
            try:
                self.join_room(room)
            except:
                print('{room_name}: connection failed'.format(
                    room_name=room.name
                ))

    def on_connect(self, room):
        room_data = self.db.get_room_data(room.name)

        # Getting sleep mode from database for each room
        room.game = room_data['game']
        room.sleep = bool(room_data['sleep'])
        room.lang = room_data['lang']
        room.default = bool(room_data['default'])
        room.delay = float(room_data['delay'])

        self.set_style()

        # Printing a success message
        print('{room_name}: successful connection (sleep: {sleep}, language: {lang}, default: {default})'.format(
            room_name=room.name,
            sleep=('On' if room.sleep else 'Off'),
            lang=self.db.store['languages'][room.lang],
            default=str(room.default),
        ))

    def on_user_count_change(self, room):
        if room.lock:
            if room.game and not room.sleep:
                game_class = globals()[room.game]
                room.game = game_class(room)
            room.lock = False
            if self.db.get_config('log_level') > 0:
                print('{room_name}: unlocked'.format(
                    room_name=room.name
                ))

    def on_reconnect(self, room):
        print('{room_name}: reconnected'.format(
            room_name=room.name
        ))

    def on_disconnect(self, room):
        print('{room_name}: disconnected'.format(
            room_name=room.name
        ))

    def on_message(self, room, user, message):
        # Debug part
        msg_time = time.time()

        # TODO DELETE THIS
        if user.uid == 'stranger111111':
            room.message(random.choice([
                'iesi acas',
                'tarfa',
                'i-ai facut show lui tobbi'
            ]))
        # if user.uid == 'pisi':
        #     room.message(random.choice([
        #         'iesi acas',
        #         'faggoato'
        #     ]))

        # Get message
        msg = message.body.strip()

        # Seen
        self.seen(msg, user, room)

        # Listen
        self.listen(msg, user, room)

        # Whois
        self.collect_whois_data(message, user)

        # Get real user
        real_user = user

        # Shapeshifting
        if self.db.store['shapeshiftings'].get(real_user.uid):
            user = get_user(self.db.store['shapeshiftings'][real_user.uid])

        # Bot is not ready on this room yet
        if room.lock:
            return

        #############################################
        # Ignoring bot's messages or empty messages #
        #############################################
        if (
            (
                user.uid == self.user.uid
                and user.uid == real_user.uid
            )
            or not msg
        ):
            return

        command = self.extract_command(msg)

        try:
            #################################
            # Deleting other users messages #
            #################################
            # Check if bot is moderator on current chatroom
            bot_moderator = (room.get_level(self.user.uid) > 0)

            # Auto-delete/auto-ban triggers
            if bot_moderator:
                if user.uid in self.db.store['auto_delete'] and user.uid == real_user.uid:
                    room.clear_user(user)
                    return

            #####################################
            # Ignore everything if flood warned #
            #####################################
            # If flood warned
            if room.flood and time.time() > room.flood:
                room_data = self.db.get_room_data(room.name)
                room.flood = 0
                room.delay = room_data['delay']

            # Get user data from the database
            user_data = self.db.get_user_data(user.uid)
            real_user_data = self.db.get_user_data(real_user.uid)

            # Room redirecting
            room = self.redirect(room, real_user, real_user_data, user, msg, command)

            ########################################
            # Ignore everything but wakeup command #
            ########################################
            if (
                room.sleep
                and command['name'] != 'wakeup'
                and not user_data['admin']
                and not real_user_data['admin']
            ):
                return

            ####################################
            # HTTPS links and Youtube Features #
            ####################################
            if self.https_or_youtube(room, msg):
                return

            #######################################################################
            # Allow moderators to execute some commands without being whitelisted #
            #######################################################################
            user_moderator = (room.get_level(user.uid) > 0)
            has_moderator_commands = user_moderator and command['name'] in [
                'startgame', 'pausegame', 'resumegame',
                'sleep', 'wakeup',
                'mode',
                'pdelete', 'delete', 'clearrecent'
            ]

            ###########################################
            # Ignore anons, ignored and unknown users #
            ###########################################
            anon_or_ignored = (is_anon(user.uid) or user_data['ignored'] == 1)
            unknown = (
                user_data['level'] == 0
                and command['name'] != 'help'
            )

            if (
                (unknown or anon_or_ignored)
                and not has_moderator_commands
                and command['name'] != 'shapeshift'
            ):
                if not anon_or_ignored and command['name']:
                    room.message(self.lang('ERROR_NOT_WHITELISTED', room.lang).format(
                        me=self.user_color(user=user, real_user=real_user, room=room, use_nick=False, pm=False),
                        command=highlight(command['prefix'] + 'help', 'Blue')
                    ))
                return

            ########################################################################
            # If we came across until here, we will want to understand the command #
            ########################################################################

            # Stop any game if an error occurred or there are too few users
            self.game_check_room_user_count(room)

            if command['name']:
                # If the message is a command
                pass
            elif self.user.uid in msg.lower():
                # If a user wants to speak with the bot
                msg = 'Nchat ' + msg
                command = self.extract_command(msg, extra_prefixes='N')
            elif room.name in self.db.store['speak']:
                # If speak mode is on
                msg = 'Schat ' + msg
                command = self.extract_command(msg, extra_prefixes='S')
            elif (
                isinstance(room.game, Game)
                and room.game.__class__.__name__ not in user_data['restricted_games']
                and not user_data['parked']
                and not room.game.skip
                and not room.sleep
            ):
                # Games time
                threading.Thread(
                    target=room.game.action,
                    args=(user, user_data, msg)
                ).start()

            if command['name'] and command['name'] not in user_data['restricted_commands']:
                Command(
                    command=command,
                    room=room,
                    real_user=real_user,
                    user=user,
                    real_user_data=real_user_data,
                    user_data=user_data,
                    msg_time=msg_time
                )
        except:
            # Usually triggers when a command didn't finished properly
            # Need to print some information about this error
            print('{room_name}: exception thrown while trying to understand {username}\'s message: {message}'.format(
                room_name=room.name,
                username=user.name,
                message=msg
            ))
            print(traceback.format_exc())

    def on_flood_warning(self, room):
        print('{room_name}: flood warned'.format(
            room_name=room.name
        ))

        room.flood = time.time() + self.db.get_config('room.flood_warned_grace_period')
        room.delay = self.db.get_config('room.delay_when_flood_warned')  # set a rougher delay
        room.wait_until = time.time()  # for buffered messages

    def on_flood_ban(self, room):
        if not room.flood:
            room.reconnect()

    def on_pm_message(self, pm, user, body):
        msg = body.strip()

        # Debug part
        msg_time = time.time()

        # Get real user
        real_user = user

        # Shapeshifting
        if self.db.store['shapeshiftings'].get(real_user.uid):
            user = get_user(self.db.store['shapeshiftings'][real_user.uid])

        # Get command data
        command = self.extract_command(msg)

        user_data = self.db.get_user_data(user.uid)
        real_user_data = self.db.get_user_data(real_user.uid)

        # Redirect messages to a room
        room = self.redirect(pm, real_user, real_user_data, user, msg, command)

        if room != pm:
            message = RoomMessage(
                room=room,
                time=msg_time,
                user=user,
                body=msg,
                raw=msg
            )
            self.on_message(room, real_user, message)
        else:
            # Set nick if exists
            if not user.nick and user_data['nick']:
                user.nick = user_data['nick']

            ###########################################
            # Ignore anons, ignored and unknown users #
            ###########################################
            anon_or_ignored = (is_anon(user.uid) or user_data['ignored'] == 1)
            unknown = (
                user_data['level'] == 0
                and command['name'] != 'help'
            )

            if (
                (unknown or anon_or_ignored)
                and command['name'] != 'shapeshift'
            ):
                if not anon_or_ignored:
                    pm.message(real_user, self.lang('ERROR_NOT_WHITELISTED', user_data['lang']).format(
                        me=self.user_color(user=user, real_user=real_user, room=None, use_nick=False, pm=True),
                        command=highlight(
                            (command.get('prefix') or self.db.get_config('command.prefixes')[0]) + 'help',
                            'Blue'
                        )
                    ))
                return

            if not user.lang:
                user.lang = user_data['lang']

            if not command['name']:
                msg = 'Pchat ' + msg
                command = self.extract_command(msg, extra_prefixes='P')

            try:
                if command['name'] not in user_data['restricted_commands']:
                    Command(
                        command=command,
                        pm=True,
                        manager=self,
                        real_user=real_user,
                        user=user,
                        real_user_data=real_user_data,
                        user_data=user_data,
                        msg_time=msg_time
                    )
            except:
                # Usually triggers when a command didn't finished properly
                # Need to print some information about this error
                print('PM System: error while trying to understand {username}\'s message: {message}'.format(
                    username=user.name,
                    message=msg
                ))
                print(traceback.format_exc())

    def on_login_fail(self, room):
        room.login_fail = True

    def on_raw(self, room, raw):
        if self.db.get_config('log_level') > 2:
            print(raw)

    def on_pm_disconnect(self, pm):
        print('{stream_name}: disconnected'.format(
            stream_name=pm.name
        ))

    def on_pm_connect(self, pm):
        print('{stream_name}: connected'.format(
            stream_name=pm.name
        ))