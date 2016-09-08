# Python imports
import urllib.parse
import urllib.request

# Project imports
from commands.PrivateMessaging.Contacts import *


class PrivateMessaging(Contacts):
    # pm
    def command_pm(self):
        try:
            args = self.args_raw.split(' ', 1)

            uids = args[0].strip()
            uids = explode(uids, ',')
            message = args[1].strip()
            assert message

            messages = list()

            invalid_usernames = []
            people_received = []

            for uid in uids:
                target_uid = self._get_user_uid(uid)

                if target_uid not in (invalid_usernames + people_received):
                    if self._validate_username(target_uid, exception=False):
                        target_user = get_user(target_uid)

                        people_received.append(target_uid)

                        if not target_user.lang:
                            target_data = self.db.get_user_data(target_uid)
                            if target_data['lang']:
                                target_user.lang = target_data['lang']
                            else:
                                target_user.lang = self.db.get_config('default_language')

                        if self.pm:
                            personal_message = self._lang('PM_MESSAGE_FROM', target_user.lang).format(
                                username=self._user_color(use_nick=False, pm=True),
                                message=highlight(self._htmlize(message), flags='i')
                            )
                        else:
                            personal_message = self._lang('PM_MESSAGE_FROM_ROOM', target_user.lang).format(
                                username=self._user_color(use_nick=False, pm=True),
                                room_name=self._room_color(),
                                message=highlight(self._htmlize(message), flags='i')
                            )

                        self.bot.pm.message(target_user, personal_message)
                    else:
                        invalid_usernames.append(target_uid)

            if people_received:
                messages.append(
                    self._lang('SUCCESS_PM_MESSAGE_SENT').format(
                        destination=', '.join([self._user_color(each_uid) for each_uid in people_received]),
                        me=self._user_color()
                    )
                )

            if invalid_usernames:
                messages.append(
                    self._lang('ERROR_INVALID_USERNAMES').format(
                        usernames=', '.join([highlight(each_username, 'Gray') for each_username in invalid_usernames]),
                        me=self._user_color()
                    )
                )

            self._message(self.bot.indented_lines(messages))
        except:
            if self.log_level > 0:
                raise
            self._invalid_usage()

    # flagpic
    def command_flagpic(self):
        if not self.args:
            self._invalid_usage()
        else:
            if (
                self.bot.pm
                and self.bot.pm.connected
                and self.bot.pm.auth_id
            ):
                uids = self.args

                messages = list()

                invalid_usernames = list()
                people_flagged = list()
                people_not_flagged = list()

                for each_uid in uids:
                    uid = self._get_user_uid(each_uid)

                    if uid not in (invalid_usernames + people_flagged + people_not_flagged):
                        if self._validate_username(uid, exception=False) and not is_anon(uid):
                            data = urllib.parse.urlencode({
                                't': self.bot.pm.auth_id,
                                'sid': uid
                            }).encode()

                            try:
                                response = str(
                                    urllib.request.urlopen("http://chatango.com/iflag", data).read().decode()
                                )
                            except:
                                people_not_flagged.append(uid)
                            else:
                                if response == 'flagged':
                                    people_flagged.append(uid)
                                else:
                                    people_not_flagged.append(uid)
                        else:
                            invalid_usernames.append(uid)

                if people_flagged:
                    messages.append(
                        self._lang('SUCCESS_USERS_PICTURE_FLAGGED').format(
                            users=', '.join([
                                self._user_color(each_uid)
                                for each_uid in people_flagged
                            ]),
                            me=self._user_color()
                        )
                    )

                if people_not_flagged:
                    messages.append(
                        self._lang('ERROR_USERS_PICTURE_NOT_FLAGGED').format(
                            users=', '.join([
                                self._user_color(each_uid)
                                for each_uid in people_not_flagged
                            ]),
                            me=self._user_color()
                        )
                    )

                if invalid_usernames:
                    messages.append(
                        self._lang('ERROR_INVALID_USERNAMES').format(
                            usernames=', '.join([
                                highlight(each_username, 'Gray')
                                for each_username in invalid_usernames
                            ]),
                            me=self._user_color()
                        )
                    )

                self._message(self.bot.indented_lines(messages))
            else:
                self._message(self._lang('ERROR_PM_NOT_CONNECTED').format(
                    me=self._user_color()
                ))