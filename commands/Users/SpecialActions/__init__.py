# Project imports
from manager.Command.Utils import *


class SpecialActions(CommandUtils):
    # merge
    def command_merge(self):
        try:
            args_arr = [arg.lower() for arg in self.args]

            # merge uid1
            uid1 = self._get_user_uid(args_arr[0])
            self._validate_username(uid1)

            # merge uid1 and
            assert('and' == args_arr[1])

            # merge uid1 and uid2
            uid2 = self._get_user_uid(args_arr[2])
            self._validate_username(uid2)

            # merge uid1 and uid2 into
            assert('into' == args_arr[3])

            # merge uid1 and uid2 into uid
            uid = self._get_user_uid(args_arr[4])
            self._validate_username(uid)

            user1_data = self.db.get_user_data(uid1)
            user2_data = self.db.get_user_data(uid2)

            if uid in [uid1, uid2]:
                if not user1_data['level']:
                    unexisting_uid = uid1
                elif not user2_data['level']:
                    unexisting_uid = uid2
                else:
                    unexisting_uid = None

                if unexisting_uid:
                    self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                        self._user_color(unexisting_uid),
                        self._user_color()
                    ))
                else:
                    if uid1 != uid2:
                        self._message(self._lang('SUCCESS_USERS_MERGED').format(
                            self._user_color(uid1),
                            self._user_color(uid2),
                            self._user_color(uid),
                            self._user_color()
                        ))
                        self.db.merge_users(uid1, uid2, uid)
                    else:
                        self._message(self._lang('ERROR_CANNOT_MERGE_SAME_USERS').format(
                            username=self._user_color()
                        ))
            else:
                self._message(self._lang('ERROR_CANNOT_MERGE_INTO_UID').format(
                    self._user_color(),
                    self._user_color(uid1),
                    self._user_color(uid2)
                ))
        except ValidationError:
            pass
        except:
            self._invalid_usage()
            if self.log_level > 0:
                raise

    # shapeshift
    def command_shapeshift(self):
        user_data = self.db.get_user_data(self.real_user.uid)

        if not user_data['admin']:
            if user_data['level'] > 0:
                self._message(self._lang('ERROR_ADMIN_ONLY').format(
                    self._user_color()
                ))
            return

        target_uid = None

        if not self.args:
            shapeshifting_back = True
        else:
            target_uid = self._get_user_uid(self.args[0])
            self._validate_username(target_uid)
            shapeshifting_back = (target_uid == self.real_user.uid)

        if shapeshifting_back and self.real_user.uid == self.user.uid:
            return

        if shapeshifting_back:
            self._message(self._lang('SHAPESHIFT_LEAVING').format(
                self._user_color(self.real_user.uid),
                self._user_color(use_nick=False)
            ))

            self.db.store['shapeshiftings'].pop(self.real_user.uid)
        else:
            self._message(self._lang('SHAPESHIFTING_TO').format(
                self._user_color(self.real_user.uid),
                self._user_color(target_uid, use_nick=False)
            ))

            self.db.store['shapeshiftings'][self.real_user.uid] = target_uid

    # screw
    def command_screw(self):
        if not self.args:
            self._invalid_usage()
        else:
            target_uid = self._get_user_uid(self.args[0])
            self._validate_username(target_uid)
            target_data = self.db.get_user_data(target_uid)

            if target_data['admin']:
                self._message(self._lang('ERROR_NO_ACCESS').format(
                    self._user_color()
                ))
                return

            if 0 == target_data['level']:
                self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                    self._user_color(target_uid),
                    self._user_color()
                ))
            else:
                self._message(self._lang('SCREW_SUCCESS').format(
                    self._user_color(target_uid)
                ))
                self.db.update_user(target_uid, {
                    'coins': 0,
                    'coins_spent': 0,
                    'level': 1,
                    'bank': 0,
                    'ignored': 1,
                    'bank_earnings': 0
                })

                rooms = self.db.get_rooms()
                for room in rooms:
                    room_data = self.db.get_room_data(room)
                    if room_data['initiator'] == target_uid:
                        self.db.update_room(room, {
                            'initiator': self.user.uid
                        })
