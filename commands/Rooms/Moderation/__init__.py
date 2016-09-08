# Project imports
from manager.Command.Utils import *


class Moderation(CommandUtils):
    # flag
    def command_flag(self):
        if not self.args:
            self._invalid_usage()
        else:
            if len(self.args) == 1:
                if self.pm:
                    self._invalid_usage()
                    return
                room = self.room
                room_name = room.name

                target_uid = self._get_user_uid(self.args[0], room)
                self._validate_username(target_uid)
            else:
                room_name = self.args[0]
                self._validate_room_name(room_name)
                room = self.bot.get_room(room_name)

                target_uid = self._get_user_uid(self.args[1], room)
                self._validate_username(target_uid)

            # Error if the bot is not connected on that room
            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            # Error if the target user is not connected on that room
            elif target_uid not in room.get_user_uids():
                self._message(self._lang('ERROR_USER_NOT_ONLINE').format(
                    username=self._user_color(target_uid),
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            # Everything seems to be ok until here
            else:
                target_data = self.db.get_user_data(target_uid)

                # Error if the target user has a higher level than you
                if (
                    (
                        target_data['level'] >= self.user_data['level']
                        or target_data['admin']
                    )
                    and not self.user_data['admin']
                ):
                    self._message(self._lang('ERROR_NO_ACCESS').format(
                        self._user_color()
                    ))
                # Finally flag the user
                else:
                    room.flag_user(get_user(target_uid))

                    if self.pm or (self.room and self.room != room):
                        self._message(self._lang('SUCCESS_FLAG_ROOM').format(
                            username=self._user_color(target_uid, room),
                            room_name=self._room_link(room.name)
                        ))
                    else:
                        self._message(self._lang('SUCCESS_FLAG').format(
                            username=self._user_color(target_uid, room)
                        ))

    # clearrecent
    def command_clearrecent(self):
        for each in self.room.get_user_names():
            self.room.clear_user(get_user(each.lower()))

    # delete
    def command_delete(self):
        if not self.args:
            self._invalid_usage()
        else:
            username = self._get_user_uid(self.args[0])
            self._validate_username(username)

            self.room.clear_user(get_user(username))

    # pdelete
    def command_pdelete(self):
        if not self.args:
            self._invalid_usage()
        else:
            p_username = self.args[0].lower()
            self._validate_username(p_username)

            for each in self.room.get_user_names():
                if p_username in each.lower():
                    self.room.clear_user(get_user(each.lower()))

    # autodelete
    def command_autodelete(self):
        if not self.args:
            if len(self.db.store['auto_delete']) > 0:
                def fn_join(array):
                    return ', '.join([
                        self._user_color(each)
                        for each in array
                    ])

                def fn_get_message_params(**kwargs):
                    return {
                        'auto_delete': kwargs['joined_string']
                    }

                self._output_long_list(
                    fn_join=fn_join,
                    array=self.db.store['auto_delete'],
                    lang_key='AUTO_DELETE_LIST',
                    fn_get_format_params=fn_get_message_params
                )
            else:
                self._message(self._lang('AUTO_DELETE_LIST_EMPTY').format(
                    me=self._user_color()
                ))
        else:
            if self._is_allowed(True):
                try:
                    uid = self._get_user_uid(self.args[0])
                    self._validate_username(uid)
                    user = get_user(uid)

                    if user.uid == self.bot.user.uid:
                        return

                    target_data = self.db.get_user_data(uid)

                    if (
                        (
                            target_data['level'] >= self.user_data['level']
                            or target_data['admin']
                        )
                        and not self.user_data['admin']
                    ):
                        self._message(self._lang('ERROR_NO_ACCESS').format(
                            self._user_color()
                        ))
                        return

                    mode = self.args[1]

                    if mode == 'on':
                        if user.uid in self.db.store['auto_delete']:
                            self._message(self._lang('ERROR_USER_ALREADY_EXISTS_IN_AUTO_DELETE_LIST').format(
                                user=self._user_color(user.uid),
                                me=self._user_color()
                            ))
                        else:
                            self._message(self._lang('SUCCESS_AUTODELETE_ADDED').format(
                                user=self._user_color(user.uid),
                                me=self._user_color()
                            ))

                            # Saving changes in the database
                            self.db.add_auto_delete(user.uid, {
                                'added_on': int(time.time()),
                                'added_by': self.user.uid
                            })
                    elif mode == 'off':
                        if user.uid not in self.db.store['auto_delete']:
                            self._message(self._lang('ERROR_USER_NOT_IN_AUTO_DELETE_LIST').format(
                                user=self._user_color(user.uid),
                                me=self._user_color()
                            ))
                        else:
                            self._message(self._lang('SUCCESS_AUTODELETE_REMOVED').format(
                                user=self._user_color(user.uid),
                                me=self._user_color()
                            ))

                            # Saving changes in the database
                            self.db.remove_auto_delete(user.uid)
                except:
                    self._invalid_usage()
                    if self.log_level > 0:
                        raise

    # ban
    def command_ban(self):
        if not self.args:
            self._invalid_usage()
        else:
            if len(self.args) == 1:
                if self.pm:
                    self._invalid_usage()
                    return
                room = self.room
                room_name = room.name

                target_uid = self._get_user_uid(self.args[0], room)
                self._validate_username(target_uid)
            else:
                room_name = self.args[0]
                self._validate_room_name(room_name)
                room = self.bot.get_room(room_name)

                target_uid = self._get_user_uid(self.args[1], room)
                self._validate_username(target_uid)

            # Error if the bot is not connected on that room
            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            # Error if user or bot doesn't have moderator access
            elif 0 == room.get_level(self.user.uid) or 0 == room.get_level(self.bot.user.uid):
                self._message(self._lang('ERROR_BOTH_MODDED').format(
                    self.bot.user.name,
                    self._user_color()
                ))
            # Error if the target user is moderator on the specified chatroom
            elif room.get_level(target_uid) > 0:
                if room != self.room:
                    self._message(self._lang('ERROR_USER_IS_MODERATOR_FULL').format(
                        username=self._user_color(target_uid),
                        room_name=self._room_color(room_name),
                        me=self._user_color()
                    ))
                else:
                    self._message(self._lang('ERROR_USER_IS_MODERATOR').format(
                        username=self._user_color(target_uid),
                        me=self._user_color()
                    ))
            else:
                target_user = get_user(target_uid)
                room.ban_user(target_user)

    # easyban
    def command_easyban(self):
        if not self.args:
            self._invalid_usage()
        else:
            if len(self.args) == 1:
                if self.pm:
                    self._invalid_usage()
                    return
                room = self.room
                room_name = room.name

                target_uid = self._get_user_uid(self.args[0], room)
                self._validate_username(target_uid)
            else:
                room_name = self.args[0]
                self._validate_room_name(room_name)
                room = self.bot.get_room(room_name)

                target_uid = self._get_user_uid(self.args[1], room)
                self._validate_username(target_uid)

            # Error if the bot is not connected on that room
            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            # Error if user or bot doesn't have moderator access
            elif 0 == room.get_level(self.user.uid) or 0 == room.get_level(self.bot.user.uid):
                self._message(self._lang('ERROR_BOTH_MODDED').format(
                    self.bot.user.name,
                    self._user_color()
                ))
            # Error if the target user is moderator on the specified chatroom
            elif room.get_level(target_uid) > 0:
                if room != self.room:
                    self._message(self._lang('ERROR_USER_IS_MODERATOR_FULL').format(
                        username=self._user_color(target_uid),
                        room_name=self._room_color(room_name),
                        me=self._user_color()
                    ))
                else:
                    self._message(self._lang('ERROR_USER_IS_MODERATOR').format(
                        username=self._user_color(target_uid),
                        me=self._user_color()
                    ))
            else:
                target_user = get_user(target_uid)
                room.ban_user(target_user)
                room.clear_user(target_user)

    # unban
    def command_unban(self):
        if not self.args:
            self._invalid_usage()
        else:
            if len(self.args) == 1:
                if self.pm:
                    self._invalid_usage()
                    return
                room = self.room
                room_name = room.name

                target_uid = self._get_user_uid(self.args[0], room)
                self._validate_username(target_uid)
            else:
                room_name = self.args[0]
                self._validate_room_name(room_name)
                room = self.bot.get_room(room_name)

                target_uid = self._get_user_uid(self.args[1], room)
                self._validate_username(target_uid)

            # Error if the bot is not connected on that room
            if not room:
                self._message(self._lang('ERROR_NOT_ONLINE').format(
                    room_name=self._room_color(room_name),
                    me=self._user_color()
                ))
            # Error if user or bot doesn't have moderator access
            elif 0 == room.get_level(self.user.uid) or 0 == room.get_level(self.bot.user.uid):
                self._message(self._lang('ERROR_BOTH_MODDED').format(
                    self._user_color(self.bot.user.uid),
                    self._user_color()
                ))
            # Error if the target user is moderator on the specified chatroom
            elif room.get_level(target_uid) > 0:
                if room != self.room:
                    self._message(self._lang('ERROR_USER_IS_MODERATOR_FULL').format(
                        username=self._user_color(target_uid),
                        room_name=self._room_color(room_name),
                        me=self._user_color()
                    ))
                else:
                    self._message(self._lang('ERROR_USER_IS_MODERATOR').format(
                        username=self._user_color(target_uid),
                        me=self._user_color()
                    ))
            else:
                target_user = get_user(target_uid)
                if room.unban(target_user):
                    if room == self.room:
                        self._message(self._lang('SUCCESS_USER_UNBANNED').format(
                            username=self._user_color(target_uid),
                            me=self._user_color()
                        ))
                    else:
                        self._message(self._lang('SUCCESS_USER_UNBANNED_FULL').format(
                            username=self._user_color(target_uid),
                            room_name=self._room_color(room_name),
                            me=self._user_color()
                        ))
                else:
                    if room == self.room:
                        self._message(self._lang('ERROR_USER_NOT_BANNED').format(
                            username=self._user_color(target_uid),
                            me=self._user_color()
                        ))
                    else:
                        self._message(self._lang('ERROR_USER_NOT_BANNED_FULL').format(
                            username=self._user_color(target_uid),
                            room_name=self._room_color(room_name),
                            me=self._user_color()
                        ))