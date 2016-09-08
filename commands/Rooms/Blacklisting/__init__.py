# Project imports
from manager.Command.Utils import *


class Blacklisting(CommandUtils):
    # blackrooms
    def command_blackrooms(self):
        array = [
            self._room_link(room)
            for room in self.db.get_rooms(True)
        ]
        if len(array) > 0:
            self._message(self._lang('BLACKROOMS').format(
                ', '.join(array)
            ))
        else:
            self._message(self._lang('BLACKROOMS_EMPTY').format(
                self._user_color()
            ))

    # blacklist
    def command_blacklist(self):
        if not self.args:
            self._launch('blackrooms')
        else:
            room_name = self.args[0].lower()
            self._validate_room_name(room_name)
            room = self._get_room(room_name)

            if room and room.default:
                self._message(self._lang('ERROR_DEFAULT_ROOM').format(
                    self._user_color()
                ))
            else:
                room_data = self.db.get_room_data(room_name)

                if room_data is None or not room_data['blacklisted']:
                    initiator_data = self.db.get_user_data(room_data['initiator'])
                    if room_data:
                        if (
                            room_data['initiator'] == self.user.uid
                            or (
                                self.user_data['level'] > initiator_data['level']
                                and not initiator_data['admin']
                            )
                        ):
                            self.db.update_room(room_name, {
                                'initiator': self.user.uid, 'blacklisted': 1
                            })
                        else:
                            self._message(self._lang('ERROR_NOT_THE_ROOM_INITIATOR').format(
                                self._user_color()
                            ))
                            return
                    else:
                        self.db.add_room(room_name, {
                            'initiator': self.user.uid,
                            'blacklisted': 1
                        })

                    self._message(self._lang('SUCCESS_BLACKLISTED').format(
                        self._room_color(room_name)
                    ))

                self.bot.leave_room(room_name)

    # unblacklist
    def command_unblacklist(self):
        if not self.args:
            self._message(self._lang('ERROR_WHAT_ROOM_TO_UNBLACKLIST').format(
                username=self._user_color()
            ))
        else:
            room = self.args[0].lower()
            self._validate_room_name(room)
            room_data = self.db.get_room_data(room)

            if room_data and room_data['blacklisted']:
                if (
                    room_data['initiator'] == self.user.uid
                    or self.user_data['level'] > self.db.get_user_data(room_data['initiator'], 'level')
                ):
                    self.db.remove_room(room)
                    self._message(self._lang('SUCCESS_REMOVED_FROM_BLACKLIST').format(
                        room_name=self._room_link(room),
                        username=self._user_color()
                    ))
                else:
                    self._message(self._lang('ERROR_NOT_THE_ROOM_INITIATOR').format(
                        self._user_color()
                    ))
            else:
                self._message(self._lang('ERROR_ROOM_NOT_BLACKLISTED').format(
                    room_name=self._room_link(room),
                    username=self._user_color()
                ))