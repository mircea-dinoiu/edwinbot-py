# Project imports
from manager.Command.Utils import *


class CoinsRelated(CommandUtils):
    # coins
    def command_coins(self):
        # Old style alias
        self._launch('level')

    # givec
    def command_givec(self):
        if len(self.args) < 2:
            self._invalid_usage()
        else:
            my_user_data = self.user_data

            target_name = self.args[0]
            target_uid = self._get_user_uid(target_name)
            self._validate_username(target_uid)
            target_user = get_user(target_uid)
            target_data = self.db.get_user_data(target_uid)

            coins = special_number(self.args[1], my_user_data['coins'])

            if coins is None:
                self._message(self._lang('ERROR_INVALID_NUMBER').format(
                    number=highlight(self.args[1], flags='b'),
                    me=self._user_color()
                ))
            else:
                if my_user_data['coins'] < coins:
                    self._message(self._lang('ERROR_COINS_NOT_ENOUGH_TO_GIVE').format(
                        coins=self._format_coins(coins),
                        me=self._user_color()
                    ))
                    return

                if (
                    is_anon(target_uid)
                    or target_data['level'] == 0
                    or target_data['ignored']
                    or target_data['parked']
                ):
                    self._message(self._lang('ERROR_CANNOT_RECEIVE_COINS').format(
                        me=self._user_color()
                    ))
                    return

                if coins < 0:
                    self._message(self._lang('ERROR_NEGATIVE_NUMBER').format(
                        me=self._user_color()
                    ))
                    return

                if self.user.uid != target_uid:
                    self.db.update_user(self.user.uid, {
                        'coins': my_user_data['coins'] - coins,
                        'coins_spent': my_user_data['coins_spent'] + coins
                    })
                    self.db.update_user(target_uid, {
                        'coins': target_data['coins'] + coins
                    })

                self._message(self._lang('SUCCESS_COINS_RECEIVED').format(
                    coins=self._format_coins(coins),
                    receiver=self._user_color(target_user.uid),
                    me=self._user_color()
                ))

                if not target_user.lang:
                    if target_data['lang']:
                        target_user.lang = target_data['lang']
                    else:
                        target_user.lang = self.db.get_config('default_language')

                if (
                    self.pm
                    or (
                        self.room
                        and target_user not in self.room.get_user_list('active')
                    )
                ):
                    if self.pm:
                        message = self._lang('COINS_RECEIVED_NOTIFY', target_user.lang).format(
                            coins=self._format_coins(coins, target_user.lang),
                            username=self._user_color(use_nick=False, pm=True)
                        )
                    else:
                        message = self._lang('COINS_RECEIVED_NOTIFY_ROOM', target_user.lang).format(
                            coins=self._format_coins(coins, target_user.lang),
                            room_name=self._room_color(),
                            username=self._user_color(use_nick=False, pm=True)
                        )

                    self.bot.pm.message(target_user, message)

    # bet
    def command_bet(self):
        # Initializations
        if self.db.store['bet_list'].get(self.user.uid) is None:
            self.db.store['bet_list'][self.user.uid] = dict()

        if not self.pm:
            #########################
            # Limit bet coins usage #
            #########################
            bet_limit = 0 if self.user_data['admin'] else (20 - self.user_data['level'])

            # Initializations
            if self.db.store['bet_list'][self.user.uid].get('bet_count') is None:
                self.db.store['bet_list'][self.user.uid]['bet_count'] = 0
            if self.db.store['bet_list'][self.user.uid].get('last_bet') is None:
                self.db.store['bet_list'][self.user.uid]['last_bet'] = 0

            if (
                time.time() - self.db.store['bet_list'][self.user.uid]['last_bet'] < bet_limit
                and not (
                    self.args
                    and self.args[0].lower() in ['red', 'black']
                    and self.db.store['bet_list'][self.user.uid].get('red_black')
                )
            ):
                if self.db.store['bet_list'][self.user.uid]['bet_count'] % 5 == 0:
                    self._message(self._lang('ERROR_COMMAND_TIME_LIMIT').format(
                        bet_limit,
                        self._user_color()
                    ))
                self.db.store['bet_list'][self.user.uid]['bet_count'] += 1
                return
            else:
                self.db.store['bet_list'][self.user.uid]['last_bet'] = time.time()

        #####################################################
        # Specific functionality of the command starts here #
        #####################################################
        if not self.args:
            self._invalid_usage()
            return

        # Constants
        value = special_number(self.args[0], self.user_data['coins']) or self.args[0].lower()
        red = highlight(self._lang('BET_COINS_RED'), 'Red')
        black = highlight(self._lang('BET_COINS_BLACK'), 'Gray')

        # RED | BLACK game
        if (
            self.db.store['bet_list'][self.user.uid].get('red_black')
            and value in ['red', 'black']
        ):
            check = self.db.store['bet_list'][self.user.uid]['red_black']['check']
            # If user's coins were changed, RED | BLACK cannot be done
            if self.user_data['coins'] == check:
                bot_choice = self.db.store['bet_list'][self.user.uid]['red_black']['choice']
                user_choice = value
                reward = self.db.store['bet_list'][self.user.uid]['red_black']['reward']

                # Message part that tells what the user has chosen
                msg_left = self._lang('BET_COINS_RED_BLACK_CHOSEN').format(
                    self._user_color(),
                    red if user_choice == 'red' else black
                )

                if user_choice == bot_choice:
                    # The message that tells whether user has won or lost
                    msg_center = self._lang('WON_COINS').format(
                        self._format_coins(reward)
                    )

                    # The new coins value
                    new_coins = self.user_data['coins'] + reward

                    # Make the changes in the database
                    self.db.update_user(self.user.uid, {
                        'coins': new_coins
                    })
                else:
                    # The message that tells whether user has won or lost
                    msg_center = self._lang('LOST_COINS').format(
                        self._format_coins(reward)
                    )

                    # The new coins value
                    new_coins = self.user_data['coins'] - reward
                    # The new coins spent value
                    new_coins_spent = self.user_data['coins_spent'] + reward

                    # Make the changes in the database
                    self.db.update_user(self.user.uid, {
                        'coins': new_coins,
                        'coins_spent': new_coins_spent
                    })

                # Strip the dot from the win or lost message
                msg_center = msg_center[:-1]

                # Shows the current coins to avoid getting spammed with the messages to check the current coins
                msg_right = self._lang('TOTAL_COINS').format(
                    self._format_coins(new_coins)
                )

                # Send the message
                self._message(msg_left + msg_center + msg_right)
            else:
                self._message(self._lang('BET_COINS_CHANGED').format(
                    red=red,
                    black=black,
                    username=self._user_color()
                ))
            self.db.store['bet_list'][self.user.uid].pop('red_black')
            return

        # Invalid coins
        if not isinstance(value, int):
            self._message(self._lang('ERROR_INVALID_COINS').format(
                self._user_color()
            ))
            return
        else:
            # Clean up the garbage from the RED | BLACK game
            try:
                self.db.store['bet_list'][self.user.uid].pop('red_black')
            except:
                # No need to debug this
                pass

        # 0 coins
        if not value:
            return
        # Bet coins is possible
        else:
            # If the user doesn't have enough coins, return an error message
            if self.user_data['coins'] < value:
                self._message(self._lang('ERROR_COINS_NOT_ENOUGH_TO_BET').format(
                    coins=self._format_coins(value),
                    me=self._user_color()
                ))
                return

            # If the coins user has bet if a negative number, return an error message
            if value < 0:
                self._message(self._lang('ERROR_NEGATIVE_NUMBER').format(
                    me=self._user_color()
                ))
                return

            # Set the reward related to the coins user has bet
            reward = value * int((1 + len(str(value))) / 2)

            # Set the chances to win related to the coins user has bet
            by = len(str(value))
            chance_number = int(by / 2)

            slots = slots_machine(self, chance_number)

            # Spun message
            msg_left = self._lang('SPUN').format(
                self._user_color(),
                highlight(slots['fruits'][0]['fruit'], slots['fruits'][0]['color']),
                highlight(slots['fruits'][1]['fruit'], slots['fruits'][1]['color']),
                highlight(slots['fruits'][2]['fruit'], slots['fruits'][2]['color'])
            )

            # Initialize RED | BLACK message
            msg_red_black = ''

            # If slots returned a full, user has won
            if 2 == slots['result']:
                # The message that tells whether user has won or lost
                msg_center = self._lang('WON_COINS').format(
                    self._format_coins(reward)
                )

                # The new coins value
                new_coins = self.user_data['coins'] + reward

                # Make the changes in the database
                self.db.update_user(self.user.uid, {
                    'coins': new_coins
                })

                # Prepare the RED | BLACK feature
                self.db.store['bet_list'][self.user.uid]['red_black'] = dict()
                self.db.store['bet_list'][self.user.uid]['red_black']['reward'] = reward
                self.db.store['bet_list'][self.user.uid]['red_black']['check'] = new_coins
                self.db.store['bet_list'][self.user.uid]['red_black']['choice'] = random.choice(['red', 'black'])

                # RED | BLACK message
                msg_red_black = self._lang('BET_COINS_RED_BLACK').format(
                    red=red,
                    black=black,
                    red_arg=highlight('red', 'Blue'),
                    black_arg=highlight('black', 'Blue'),
                    cmd=highlight(self.prefix + self.details['match'], 'Blue')
                )
            # User has lost otherwise
            else:
                # The message that tells whether user has won or lost
                msg_center = self._lang('LOST_COINS').format(
                    self._format_coins(value)
                )

                # The new coins value
                new_coins = self.user_data['coins'] - value
                # The new coins spent value
                new_coins_spent = self.user_data['coins_spent'] + value

                # Make the changes in the database
                self.db.update_user(self.user.uid, {
                    'coins': new_coins,
                    'coins_spent': new_coins_spent
                })

            # Strip the dot from the win or lost message
            msg_center = msg_center[:-1]

            # Shows the current coins to avoid getting spammed with the messages to check the current coins
            msg_right = self._lang('TOTAL_COINS').format(
                self._format_coins(new_coins)
            )

            msg_right = self.bot.indented_line(msg_right, msg_red_black)

            # Send the message
            self._message(msg_left + msg_center + msg_right)

    # bank
    def command_bank(self):
        deposited = self.user_data['bank']
        if self.args:
            try:
                action = self.args[0].lower()
                assert(action in ['deposit', 'withdraw', 'dep', 'wd'])

                if action in ['deposit', 'dep']:
                    value = special_number(self.args[1], self.user_data['coins'])
                else:
                    value = special_number(self.args[1], self.user_data['bank'])

                if value == 0:
                    return

                if value is None:
                    self._message(self._lang('ERROR_INVALID_NUMBER').format(
                        number=highlight(self.args[1].lower(), flags='b'),
                        me=self._user_color()
                    ))
                    return

                if action in ['deposit', 'dep']:
                    if value > self.user_data['coins']:
                        self._message(self._lang('ERROR_NOT_ENOUGH_COINS_TO_DEPOSIT').format(
                            coins=self._format_coins(value)
                        ))
                        return
                    else:
                        deposited += value

                        self._message(self._lang('SUCCESS_BANK_DEPOSIT').format(
                            coins=self._format_coins(value)
                        ))

                        self.db.update_user(self.user.uid, {
                            'bank': deposited,
                            'coins': self.user_data['coins'] - value
                        })
                else:
                    if value > deposited:
                        self._message(self._lang('ERROR_NOT_ENOUGH_DEPOSITED'))
                        return
                    else:
                        deposited -= value

                        self._message(self._lang('SUCCESS_BANK_WITHDRAW').format(
                            coins=self._format_coins(value)
                        ))

                        self.db.update_user(self.user.uid, {
                            'bank': deposited,
                            'coins': self.user_data['coins'] + value
                        })
            except:
                self._invalid_usage()
                return

        self._message(self._lang('BANK_DEPOSITED').format(
            coins=self._format_coins(deposited)
        ))