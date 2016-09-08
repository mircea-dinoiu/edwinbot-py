# Project imports
from manager.Command.Utils import *


class Miscellaneous(CommandUtils):
    # lottery
    def command_lottery(self):
        if not self.args:
            self._invalid_usage()
        else:
            lottery_type = self.args[0].lower()

            if lottery_type in ['level', 'lvl']:
                lottery_data = self.db.store['lotteries']['level']

                # Output error message if no session is running
                if lottery_data['running']:
                    duration = lottery_data['duration']
                    session_start = lottery_data['session_end'] - duration
                    time_passed = round(time.time() - session_start)

                    message = self._lang('LOTTERY_INFO').format(
                        head=highlight(self._lang('LOTTERY_INFO_HEAD_LEVEL'), flags='i'),
                        time_passed=self._format_seconds(time_passed),
                        duration=self._format_seconds(duration)
                    )

                    if time.time() > lottery_data['session_end']:
                        message = self.db.get_config('message.line_breaker').join([
                            message,
                            self._lang('LOTTERY_INFO_SESSION_END_NEEDED_USERS').format(
                                needed_users=lottery_data['needed_users']
                            )
                        ])
                    else:
                        message = self.db.get_config('message.line_breaker').join([
                            message,
                            self._lang('LOTTERY_INFO_SESSION_END_REMAINING').format(
                                remaining=self._format_seconds(round(lottery_data['session_end'] - time.time()))
                            )
                        ])

                    if lottery_data['users']:
                        message = self.db.get_config('message.line_breaker').join([
                            message,
                            self._lang('LOTTERY_INFO_REGISTERED_USERS').format(
                                users=', '.join([
                                    '{username} ({tickets})'.format(
                                        username=self._user_color(uid),
                                        tickets=lottery_data['users'][uid]
                                    )
                                    for uid in lottery_data['users']
                                ]),
                                count=len(lottery_data['users'])
                            )
                        ])
                    message += self.db.get_config('message.line_breaker')
                    self._message(message)
                else:
                    self._message(self._lang('ERROR_LOTTERY_SESSION_NOT_RUNNING').format(
                        me=self._user_color()
                    ))
            elif lottery_type in ['coin', 'coins', 'c']:
                lottery_data = self.db.store['lotteries']['coins']

                if lottery_data['running']:
                    duration = lottery_data['duration']
                    session_start = lottery_data['session_end'] - duration
                    time_passed = round(time.time() - session_start)

                    message = self._lang('LOTTERY_INFO').format(
                        head=highlight(self._lang('LOTTERY_INFO_HEAD_COINS'), flags='i'),
                        time_passed=self._format_seconds(time_passed),
                        duration=self._format_seconds(duration)
                    )

                    if time.time() > lottery_data['session_end']:
                        message = self.db.get_config('message.line_breaker').join([
                            message,
                            self._lang('LOTTERY_INFO_SESSION_END_NEEDED_USERS').format(
                                needed_users=lottery_data['needed_users']
                            )
                        ])
                    else:
                        message = self.db.get_config('message.line_breaker').join([
                            message,
                            self._lang('LOTTERY_INFO_SESSION_END_REMAINING').format(
                                remaining=self._format_seconds(round(lottery_data['session_end'] - time.time()))
                            )
                        ])

                    message = self.db.get_config('message.line_breaker').join([
                        message,
                        self._lang('LOTTERY_INFO_TICKET_PRICE').format(
                            ticket_price=self._format_coins(lottery_data['ticket_price'])
                        )
                    ])

                    if lottery_data['users']:
                        message = self.db.get_config('message.line_breaker').join([
                            message,
                            self._lang('LOTTERY_INFO_REGISTERED_USERS').format(
                                users=', '.join([
                                    '{username} ({tickets})'.format(
                                        username=self._user_color(uid),
                                        tickets=lottery_data['users'][uid]
                                    )
                                    for uid in lottery_data['users']
                                ]),
                                count=len(lottery_data['users'])
                            )
                        ])
                    message += self.db.get_config('message.line_breaker')
                    self._message(message)
                else:
                    self._message(self._lang('ERROR_LOTTERY_SESSION_NOT_RUNNING').format(
                        me=self._user_color()
                    ))
            else:
                self._invalid_usage()

    # top
    def command_top(self):
        if not self.args:
            self._invalid_usage()
            return

        top_type = self.args[0].lower()

        if top_type not in ['coins', 'coin', 'c', 'level', 'lvl']:
            self._invalid_usage()
            return

        if len(self.args) > 1:
            room_name = self.args[1]
            room = self._get_room(room_name)
        else:
            if self.pm:
                self._invalid_usage()
                return
            room = self.room
            room_name = room.name

        if not room:
            self._message(self._lang('ERROR_NOT_CONNECTED').format(
                room_name=self._room_link(room_name),
                username=self._user_color()
            ))
            return

        online_users = [user.uid for user in room.get_user_list()]
        top = list()

        if top_type in ['level', 'lvl']:
            for user in online_users:
                data = self.db.get_user_data(user)
                data['uid'] = user
                if 0 == data['ignored'] and 0 != data['level']:
                    top.append(data)

            users = sorted(top, key=lambda k: (k['level'], k['coins']), reverse=True)[:15]

            string = ''

            for index, user in enumerate(users):
                place = index + 1
                spacing = ' ' * (7 if len(str(place)) > 1 else 9)

                row = '{0}{1}. {2}: {3}<br>'.format(
                    spacing,
                    place,
                    self._user_color(user['uid']),
                    highlight(user['level'], 'Blue'),
                )

                string += row

            header = self._lang('ONLINE_ON_ROOM').format(
                room_name=self._room_link(room_name)
            )

            self._message(self._lang('TOP_LEVEL').format(
                header,
                string
            ))
        elif top_type in ['c', 'coins', 'coin']:
            for user in online_users:
                data = self.db.get_user_data(user)
                data['uid'] = user
                if 0 != data['coins'] and 0 == data['ignored']:
                    top.append(data)

            users = sorted(top, key=lambda k: k['coins'], reverse=True)[:15]

            string = ''

            for index, user in enumerate(users):
                place = index + 1
                spacing = ' ' * (7 if len(str(place)) > 1 else 9)

                row = '{spacing}{place}. {username}: {coins}<br>'.format(
                    spacing=spacing,
                    place=place,
                    username=self._user_color(user['uid']),
                    coins=self._format_coins(user['coins'])
                )

                string += row

            header = self._lang('ONLINE_ON_ROOM').format(
                room_name=self._room_link(room_name)
            )

            self._message(self._lang('TOP_COINS').format(
                header,
                string
            ))
