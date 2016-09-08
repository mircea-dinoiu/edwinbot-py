# Project imports
from util.time import *
from commands.Users.Information import *
from commands.Users.LevelRelated import *
from commands.Users.CoinsRelated import *
from commands.Users.Stalking import *
from commands.Users.Ignoring import *
from commands.Users.Restrictions import *
from commands.Users.AccountParking import *
from commands.Users.SpecialActions import *


class Users(
    Information,
    LevelRelated,
    CoinsRelated,
    Stalking,
    Ignoring,
    Restrictions,
    AccountParking,
    SpecialActions
):
    # nick
    def command_nick(self):
        if not self.args:
            if self.user.nick:
                self._message(self._lang('YOUR_NICK').format(
                    nick=self._user_color(),
                    username=self._user_color(use_nick=False)
                ))
            else:
                self._message(self._lang('NICK_NOT_SET').format(
                    username=self._user_color(),
                    command=highlight(self.prefix + 'nick', 'Blue'),
                    param=highlight(
                        self.man['raw']['params'][0]['name'][self.lang],
                        'Blue'
                    )
                ))
        else:
            # Remove html
            nick = strip_html(self.args_raw)

            if self.user.nick and nick.lower() == self.user.uid:
                # Set the User's nick attribute to empty string to prevent querying again the database for the nick
                self.user.nick = ''

                self._message(self._lang('SUCCESS_NICK_REMOVED').format(
                    username=self._user_color()
                ))

                # Make the chances in the database
                self.db.update_user(self.user.uid, {'nick': None})
            else:
                if self.user.uid == nick.lower():
                    self._message(self._lang('ERROR_NICK_SAME_AS_USERNAME').format(
                        username=self._user_color()
                    ))
                else:
                    if len(nick) > 255:
                        self._message(self._lang('ERROR_NICK_TOO_LONG').format(
                            username=self._user_color()
                        ))
                    else:
                        # Set the User's nick attribute
                        self.user.nick = nick

                        self._message(self._lang('SUCCESS_NICK_CHANGED').format(
                            nick=self._user_color(),
                            username=self._user_color(use_nick=False)
                        ))

                        # Make the changes in the database
                        self.db.update_user(self.user.uid, {'nick': nick})

    # buy
    def command_buy(self):
        if not self.args:
            self._invalid_usage()
        else:
            user_data = self.user_data
            item = self.args[0].lower()

            if item in ['level', 'lvl']:
                try:
                    if len(self.args) > 1:
                        wanted_level = int(self.args[1])
                    else:
                        wanted_level = user_data['level'] + 1
                except:
                    self._message(self._lang('ERROR_INVALID_LEVEL').format(
                        me=self._user_color(),
                        level=highlight(self.args[1], 'Blue')
                    ))
                else:
                    if wanted_level > user_data['level']:
                        price = 0

                        for i in range(user_data['level'] + 1, wanted_level + 1):
                            price += get_level_price(i)

                        if user_data['coins'] < price:
                            self._message(self._lang('ERROR_COINS_NOT_ENOUGH_TO_BUY_LEVEL').format(
                                level=wanted_level,
                                me=self._user_color(),
                                coins=self._format_coins(price - user_data['coins'])
                            ))
                        else:
                            user_data['coins'] -= price
                            user_data['coins_spent'] += price
                            user_data['level'] = wanted_level

                            self.db.update_user(self.user.uid, {
                                'coins': user_data['coins'],
                                'coins_spent': user_data['coins_spent'],
                                'level': user_data['level']
                            })

                            self._message(self._lang('SUCCESS_LEVEL_UPGRADED').format(
                                level=wanted_level,
                                me=self._user_color()
                            ))
                    else:
                        self._message(self._lang('ERROR_HIGHER_LEVEL_NEEDED').format(
                            me=self._user_color()
                        ))
            elif item in ['lottery', 'lot']:
                if len(self.args) > 1:
                    args = self.args[1:]
                else:
                    args = ['level', 'coins']

                args_used = {
                    'level': False,
                    'coins': False
                }

                messages = list()

                for arg in args:
                    if arg in ['level', 'lvl'] and not args_used['level']:
                        args_used['level'] = True

                        # Use a shorted name for lottery data
                        lottery_data = self.db.store['lotteries']['level']

                        # Check if session is running
                        if not lottery_data['running']:
                            message = self._lang('ERROR_LOTTERY_SESSION_NOT_RUNNING').format(
                                me=self._user_color()
                            )
                        elif (
                            self.user.uid in lottery_data['users']
                            and lottery_data['users'][self.user.uid] == lottery_data['max_tickets_per_user']
                        ):
                            message = self._lang('ERROR_TOO_MANY_TICKETS').format(
                                me=self._user_color(),
                                max=lottery_data['max_tickets_per_user']
                            )
                        else:
                            # Set the price that will be the ticket price * user's level
                            price = lottery_data['ticket_price'] * user_data['level']
                            if self.user.uid in lottery_data['users']:
                                price *= lottery_data['users'][self.user.uid] + 1

                            # Return an error if user has no money to pay for this lottery ticket
                            if user_data['coins'] < price:
                                message = self._lang('ERROR_COINS_NOT_ENOUGH_TO_BUY_LOTTERY_TICKET').format(
                                    me=self._user_color(),
                                    coins=self._format_coins(price)
                                )
                            else:
                                # Take user's money
                                user_data['coins'] -= price
                                user_data['coins_spent'] += price

                                self.db.update_user(self.user.uid, {
                                    'coins': user_data['coins'],
                                    'coins_spent': user_data['coins_spent']
                                })

                                # Register user to lottery
                                lottery_data['last_ticket'] = time.time()
                                if self.user.uid in lottery_data['users']:
                                    lottery_data['users'][self.user.uid] += 1
                                else:
                                    lottery_data['users'][self.user.uid] = 1

                                # Session is expired and continues until the users number reach the needed
                                session_expired = (time.time() > lottery_data['session_end'])

                                if session_expired:
                                    # Check if this registration triggered the session end
                                    number_of_registered_users = len(lottery_data['users'])
                                    triggered_end = (number_of_registered_users >= lottery_data['needed_users'])

                                    if triggered_end:
                                        message = self._lang(
                                            'SUCCESS_BOUGHT_LEVEL_LOTTERY_SESSION_ENDS'
                                        ).format(
                                            me=self._user_color()
                                        )
                                    else:
                                        if lottery_data['users'][self.user.uid] > 1:
                                            message = self._lang(
                                                'SUCCESS_BOUGHT_LEVEL_LOTTERY_TICKET_NEEDED_USERS_TICKETS'
                                            ).format(
                                                me=self._user_color(),
                                                needed_users=lottery_data['needed_users'],
                                                tickets=lottery_data['users'][self.user.uid]
                                            )
                                        else:
                                            message = self._lang(
                                                'SUCCESS_BOUGHT_LEVEL_LOTTERY_TICKET_NEEDED_USERS'
                                            ).format(
                                                me=self._user_color(),
                                                needed_users=lottery_data['needed_users']
                                            )
                                else:
                                    if lottery_data['users'][self.user.uid] > 1:
                                        message = self._lang(
                                            'SUCCESS_BOUGHT_LEVEL_LOTTERY_TICKET_REMAINING_TICKETS'
                                        ).format(
                                            me=self._user_color(),
                                            remaining=format_seconds_to_short_string(
                                                lottery_data['session_end'] - time.time()
                                            ),
                                            tickets=lottery_data['users'][self.user.uid]
                                        )
                                    else:
                                        message = self._lang(
                                            'SUCCESS_BOUGHT_LEVEL_LOTTERY_TICKET_REMAINING'
                                        ).format(
                                            me=self._user_color(),
                                            remaining=format_seconds_to_short_string(
                                                lottery_data['session_end'] - time.time()
                                            )
                                        )

                        messages.append(message)
                    elif arg in ['coins', 'coin', 'c'] and not args_used['coins']:
                        args_used['coins'] = True

                        # Use a shorted name for lottery data
                        lottery_data = self.db.store['lotteries']['coins']

                        # Check if session is running
                        if not lottery_data['running']:
                            message = self._lang('ERROR_LOTTERY_SESSION_NOT_RUNNING').format(
                                me=self._user_color()
                            )
                        else:
                            # Get the price from db store
                            price = lottery_data['ticket_price']

                            # Return an error if user has no money to pay for this lottery ticket
                            if user_data['coins'] < price:
                                message = self._lang('ERROR_COINS_NOT_ENOUGH_TO_BUY_LOTTERY_TICKET').format(
                                    me=self._user_color(),
                                    coins=self._format_coins(price)
                                )
                            elif (
                                self.user.uid in lottery_data['users']
                                and lottery_data['users'][self.user.uid] == lottery_data['max_tickets_per_user']
                            ):
                                message = self._lang('ERROR_TOO_MANY_TICKETS').format(
                                    me=self._user_color(),
                                    max=lottery_data['max_tickets_per_user']
                                )
                            else:
                                # Take user's money
                                user_data['coins'] -= price
                                user_data['coins_spent'] += price

                                self.db.update_user(self.user.uid, {
                                    'coins': user_data['coins'],
                                    'coins_spent': user_data['coins_spent']
                                })

                                # Register user to lottery
                                lottery_data['last_ticket'] = time.time()
                                if self.user.uid in lottery_data['users']:
                                    lottery_data['users'][self.user.uid] += 1
                                else:
                                    lottery_data['users'][self.user.uid] = 1

                                # Session is expired and continues until the users number reach the needed
                                session_expired = (time.time() > lottery_data['session_end'])

                                if session_expired:
                                    # Check if this registration triggered the session end
                                    number_of_registered_users = len(lottery_data['users'])
                                    triggered_end = (number_of_registered_users >= lottery_data['needed_users'])

                                    if triggered_end:
                                        message = self._lang('SUCCESS_BOUGHT_COINS_LOTTERY_SESSION_ENDS').format(
                                            me=self._user_color()
                                        )
                                    else:
                                        if lottery_data['users'][self.user.uid] > 1:
                                            message = self._lang(
                                                'SUCCESS_BOUGHT_COINS_LOTTERY_TICKET_NEEDED_USERS_TICKETS'
                                            ).format(
                                                me=self._user_color(),
                                                needed_users=lottery_data['needed_users'],
                                                tickets=lottery_data['users'][self.user.uid]
                                            )
                                        else:
                                            message = self._lang(
                                                'SUCCESS_BOUGHT_COINS_LOTTERY_TICKET_NEEDED_USERS'
                                            ).format(
                                                me=self._user_color(),
                                                needed_users=lottery_data['needed_users']
                                            )
                                else:
                                    if lottery_data['users'][self.user.uid] > 1:
                                        message = self._lang(
                                            'SUCCESS_BOUGHT_COINS_LOTTERY_TICKET_REMAINING_TICKETS'
                                        ).format(
                                            me=self._user_color(),
                                            remaining=format_seconds_to_short_string(
                                                lottery_data['session_end'] - time.time()
                                            ),
                                            tickets=lottery_data['users'][self.user.uid]
                                        )
                                    else:
                                        message = self._lang('SUCCESS_BOUGHT_COINS_LOTTERY_TICKET_REMAINING').format(
                                            me=self._user_color(),
                                            remaining=format_seconds_to_short_string(
                                                lottery_data['session_end'] - time.time()
                                            )
                                        )

                        messages.append(message)

                if not messages:
                    self._invalid_usage()
                else:
                    self._message(self.bot.indented_lines(messages))
            else:
                self._invalid_usage()