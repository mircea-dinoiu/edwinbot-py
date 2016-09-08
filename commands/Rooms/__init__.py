# Project imports
from commands.Rooms.Information import *
from commands.Rooms.Settings import *
from commands.Rooms.Moderation import *
from commands.Rooms.Blacklisting import *


class Rooms(
    Information,
    Settings,
    Moderation,
    Blacklisting
):
    # rooms
    def command_rooms(self):
        online_rooms = [
            '{room} ({count})'.format(
                room=self._room_link(room),
                count=self.bot.get_room(room).user_count
            )
            for room in sorted(self.bot.get_room_names())
        ]

        self._message(self._lang('CONNECTED_TO').format(
            len(self.bot.get_rooms()),
            ', '.join(online_rooms)
        ))

    # join
    def command_join(self):
        if not self.args:
            self._message(self._lang('ERROR_WHAT_ROOM_TO_JOIN').format(
                username=self._user_color()
            ))
        else:
            room = self.args[0].lower()
            self._validate_room_name(room)

            if room in self.bot.get_room_names():
                self._message(self._lang('ERROR_ALREADY_ONLINE').format(
                    room_name=self._room_link(room),
                    username=self._user_color()
                ))
            else:
                room_data = self.db.get_room_data(room)

                if room_data and 1 == room_data['blacklisted']:
                    self._message(self._lang('ERROR_ROOM_BLACKLISTED').format(
                        self._user_color()
                    ))
                else:
                    try:
                        if self.bot.join_room(room):
                            self._message(self._lang('SUCCESS_JOIN_ROOM').format(
                                room_name=self._room_link(room),
                                username=self._user_color()
                            ))

                            self.db.add_room(room, {
                                'initiator': self.user.uid,
                                'sleep': 1
                            })
                        else:
                            self._message(self._lang('ERROR_CONNECTING').format(
                                room_name=self._room_link(room),
                                username=self._user_color()
                            ))
                    except:
                        self._message(self._lang('ERROR_CONNECTING').format(
                            room_name=self._room_link(room),
                            username=self._user_color()
                        ))
                        if self.log_level > 0:
                            raise

    # leave
    def command_leave(self):
        if not self.args:
            if self.pm:
                self._invalid_usage()
                return
            room = self.room
            room_name = room.name
        else:
            room = self._get_room(self.args[0].lower())
            room_name = room.name if room else self.args[0].lower()
            if "*" != room_name:
                self._validate_room_name(room_name)

        if room_name == "*":
            if self._is_allowed(True):
                for each in self.bot.get_room_names():
                    if not each.default:
                        try:
                            room_data = self.db.get_room_data(each)
                            user_moderator = (self.bot.get_room(each).get_level(self.user.uid) > 0)

                            if (
                                room_data['initiator'] == self.user.uid
                                or self.user_data['level'] > self.db.get_user_data(room_data['initiator'], 'level')
                                or (user_moderator and room_name == self.room.name)
                                or self.user_data['admin']
                            ):
                                self.db.remove_room(each)
                                self.bot.leave_room(each)
                        except:
                            if self.log_level > 0:
                                raise
        else:
            cmd_req = self.man['raw']

            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            elif room.default:
                self._message(self._lang('ERROR_DEFAULT_ROOM').format(
                    self._user_color()
                ))
            elif (
                self.user_data['level'] >= cmd_req['level']
                or self.user_data['admin']
                or room.get_level(self.user.uid) > 0
            ):
                user_moderator = (room.get_level(self.user.uid) > 0)
                room_data = self.db.get_room_data(room_name)

                if (
                    room_data['initiator'] == self.user.uid
                    or self.user_data['level'] > self.db.get_user_data(room_data['initiator'], 'level')
                    or (user_moderator and room_name == self.room.name)
                    or self.user_data['admin']
                ):
                    self.db.remove_room(room_name)
                    self.bot.leave_room(room_name)
                else:
                    self._message(self._lang('ERROR_NOT_THE_ROOM_INITIATOR').format(
                        self._user_color()
                    ))
            else:
                self._message(self._lang('ERROR_LEVEL_AT_LEAST_OR_MODERATOR').format(
                    cmd_req['level'],
                    self._user_color()
                ))