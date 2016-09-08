# Project imports
from manager.Command.Utils import *


class Settings(CommandUtils):
    # speak
    def command_speak(self):
        self.db.store['speak'] |= {self.room.name}

    # shutup
    def command_shutup(self):
        self.db.store['speak'] -= {self.room.name}
        self._message(self._lang('SHUTUP_SUCCESS'))

    # sleep
    def command_sleep(self):
        if not self.args:
            if self.pm:
                self._invalid_usage()
                return
            room_obj = self.room
            room = room_obj.name
        else:
            room = self.args[0]
            if "*" != room:
                self._validate_room_name(room)
            room_obj = self._get_room(room)

        if room == "*":
            if self._is_allowed(True):
                for each in self.bot.rooms:
                    each.message(self._lang('GOING_TO_SLEEP'))
                    each.sleep = True

                    self.db.update_room(each.name, {
                        'sleep': 1
                    })
        elif room_obj is None:
            self._message(self._lang('ERROR_NOT_ONLINE').format(
                room_name=self._room_color(room),
                me=self._user_color()
            ))
        else:
            self._message(self._lang('GOING_TO_SLEEP'))
            room_obj.sleep = True

            self.db.update_room(room_obj.name, {
                'sleep': 1
            })

    # wakeup
    def command_wakeup(self):
        if not self.args:
            if self.pm:
                self._invalid_usage()
                return
            room_obj = self.room
            room = room_obj.name
        else:
            room = self.args[0]
            if "*" != room:
                self._validate_room_name(room)
            room_obj = self._get_room(room)

        if room == "*":
            if self._is_allowed(True):
                for each in self.bot.rooms:
                    each.sleep = False
                    if isinstance(each.game, str):
                        game_class = globals()[each.game]
                        each.game = game_class(each)
                    each.message(self._lang('WAKING_UP'))

                    self.db.update_room(each.name, {
                        'sleep': 0
                    })
        elif not room_obj:
            self._message(self._lang('ERROR_NOT_ONLINE').format(
                room_name=self._room_color(room),
                me=self._user_color()
            ))
        else:
            room_obj.sleep = False
            if isinstance(room_obj.game, str):
                game_class = globals()[room_obj.game]
                room_obj.game = game_class(room_obj)
            room_obj.message(self._lang('WAKING_UP'))

            self.db.update_room(room_obj.name, {
                'sleep': 0
            })

    # delay
    def command_delay(self):
        if not self.args:
            self._invalid_usage()
        else:
            if len(self.args) == 1:
                delay = self.args[0]
                if self.pm:
                    self._invalid_usage()
                    return
                room = self.room
                room_name = room.name
            else:
                delay = self.args[1]
                room_name = self.args[0]
                if "*" != room_name:
                    self._validate_room_name(room_name)
                room = self._get_room(room_name)

            try:
                delay = round(float(delay), 2)
            except:
                self._message(self._lang('ERROR_INVALID_NUMBER').format(
                    number=highlight(delay, flags='b'),
                    me=self._user_color()
                ))
            else:
                if delay < 0:
                    self._message(self._lang('ERROR_NEGATIVE_NUMBER').format(
                        me=self._user_color()
                    ))
                elif room_name == "*":
                    for each in self.bot.rooms:
                        if not each.flood:
                            each.delay = delay
                            each.message(self._lang('GLOBAL_DELAY_SET').format(
                                delay=self._format_seconds(delay)
                            ))
                if not room:
                    self._message(self._lang('ERROR_NOT_ONLINE').format(
                        room_name=self._room_color(room_name),
                        me=self._user_color()
                    ))
                else:
                    if room.flood:
                        self._message(self._lang('ERROR_DELAY_CANNOT_BE_SET').format(
                            me=self._user_color()
                        ))
                    else:
                        room.delay = delay
                        self._message(self._lang('SUCCESS_DELAY_SET').format(
                            delay=self._format_seconds(delay),
                            me=self._user_color()
                        ))