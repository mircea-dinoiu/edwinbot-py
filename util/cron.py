# Python imports
import time
from collections import OrderedDict

# Project imports
from util.time import format_seconds_to_short_string
from util.util import percentage
from util.render import highlight, currency
from engine.chatango.util.util import *


def level_lottery(bot):
    lottery_data = bot.db.store['lotteries']['level']

    # Lottery session has not begun
    if not lottery_data['running']:
        lottery_data['running'] = True
        lottery_data['session_end'] = time.time() + lottery_data['duration']
        lottery_data['last_message'] = time.time()
        lottery_data['message_count'] = 0
        lottery_data['last_ticket'] = 0
        lottery_data['users'] = OrderedDict()

        for room in bot.get_rooms():
            if not (
                room.sleep
                or room.login_fail
                or room.lock
            ):
                message = bot.lang('LEVEL_LOTTERY_START', room.lang).format(
                    command=highlight('{prefix}buy lottery level'.format(
                        prefix=bot.db.get_config('command.prefixes')[0]
                    ), 'Blue')
                )
                room.message(message)
    # Lottery session is going on
    else:
        if time.time() > lottery_data['session_end']:
            if len(lottery_data['users']) >= lottery_data['needed_users']:
                # Stop the lottery session
                lottery_data['running'] = False

                # Get the participants
                participants = []
                for participant in lottery_data['users']:
                    for i in range(0, lottery_data['users'][participant]):
                        participants.append(participant)
                        random.shuffle(participants)

                # Choose the winner :)
                winner = get_user(random.choice(participants))
                winner_data = bot.db.get_user_data(winner.uid)

                while winner_data['ignored']:
                    winner = get_user(random.choice(participants))
                    winner_data = bot.db.get_user_data(winner.uid)

                # Level up the winner :)
                bot.db.update_user(winner.uid, {
                    'level': winner_data['level'] + 1
                })

                # Output message to all rooms
                for room in bot.get_rooms():
                    if not (
                        room.sleep
                        or room.login_fail
                        or room.lock
                    ):
                        message = bot.lang('LEVEL_LOTTERY_WINNER', room.lang).format(
                            winner=highlight(
                                winner.name,
                                'Green' if (winner in room.get_user_list()) else 'Gray'
                            )
                        )
                        room.message(message)

                # PM the winner
                bot.pm.message(winner, bot.lang('PM_LEVEL_LOTTERY_WINNER', winner_data['lang']))
            else:
                # Print message that the session expired and bot is waiting for needed users
                if (
                    time.time() - lottery_data['last_message'] > lottery_data['message_interval']
                    and not (
                        lottery_data['message_count']
                        and time.time() - lottery_data['last_ticket'] > lottery_data['message_interval']
                    )
                ):
                    lottery_data['last_message'] = time.time()
                    lottery_data['message_count'] += 1

                    for room in bot.get_rooms():
                        if not (
                            room.sleep
                            or room.login_fail
                            or room.lock
                        ):
                            messages = list()
                            messages.append(
                                bot.lang('LEVEL_LOTTERY_NEEDED_USERS', room.lang).format(
                                    needed_users=lottery_data['needed_users'],
                                    command=highlight('{prefix}buy lottery level'.format(
                                        prefix=bot.db.get_config('command.prefixes')[0]
                                    ), 'Blue')
                                )
                            )
                            if lottery_data['users']:
                                messages.append(
                                    bot.lang('LOTTERY_REGISTERED_USERS', room.lang).format(
                                        users=', '.join([
                                            '{username} ({tickets})'.format(
                                                username=highlight(
                                                    user.name,
                                                    'Green' if (user in room.get_user_list()) else 'Gray'
                                                ),
                                                tickets=lottery_data['users'][user.uid]
                                            )
                                            for user in [
                                                get_user(uid)
                                                for uid in lottery_data['users']
                                            ]
                                        ]),
                                        count=len(lottery_data['users'])
                                    )
                                )

                            room.message(bot.indented_lines(messages))
        else:
            if (
                time.time() - lottery_data['last_message'] > lottery_data['message_interval']
                and not (
                    lottery_data['message_count']
                    and time.time() - lottery_data['last_ticket'] > lottery_data['message_interval']
                )
            ):
                lottery_data['last_message'] = time.time()
                lottery_data['message_count'] += 1

                for room in bot.get_rooms():
                    if not (
                        room.sleep
                        or room.login_fail
                        or room.lock
                    ):
                        messages = list()
                        messages.append(
                            bot.lang('LEVEL_LOTTERY_REMAINING', room.lang).format(
                                remaining=format_seconds_to_short_string(lottery_data['session_end'] - time.time()),
                                command=highlight('{prefix}buy lottery level'.format(
                                    prefix=bot.db.get_config('command.prefixes')[0]
                                ), 'Blue')
                            )
                        )
                        if lottery_data['users']:
                            messages.append(
                                bot.lang('LOTTERY_REGISTERED_USERS', room.lang).format(
                                    users=', '.join([
                                        '{username} ({tickets})'.format(
                                            username=highlight(
                                                user.name,
                                                'Green' if (user in room.get_user_list()) else 'Gray'
                                            ),
                                            tickets=lottery_data['users'][user.uid]
                                        )
                                        for user in [
                                            get_user(uid)
                                            for uid in lottery_data['users']
                                        ]
                                    ]),
                                    count=len(lottery_data['users'])
                                )
                            )
                        room.message(bot.indented_lines(messages))


def coins_lottery(bot):
    lottery_data = bot.db.store['lotteries']['coins']

    # Lottery session has not begun
    if not lottery_data['running']:
        lottery_data['running'] = True
        lottery_data['session_end'] = time.time() + lottery_data['duration']
        lottery_data['last_message'] = time.time()
        if lottery_data['users']:
            number = len(lottery_data['users']) * 10
        else:
            number = lottery_data['needed_users'] * 10
        lottery_data['ticket_price'] = number
        lottery_data['message_count'] = 0
        lottery_data['last_ticket'] = 0
        lottery_data['users'] = OrderedDict()

        for room in bot.get_rooms():
            if not (
                room.sleep
                or room.login_fail
                or room.lock
            ):
                message = bot.lang('COINS_LOTTERY_START', room.lang).format(
                    command=highlight('{prefix}buy lottery coins'.format(
                        prefix=bot.db.get_config('command.prefixes')[0]
                    ), 'Blue'),
                    ticket_price=bot.format_coins(lottery_data['ticket_price'], room.lang)
                )
                room.message(message)
    # Lottery session is going on
    else:
        if time.time() > lottery_data['session_end']:
            if len(lottery_data['users']) >= lottery_data['needed_users']:
                # Stop the lottery session
                lottery_data['running'] = False

                # Get the participants
                participants = []
                for participant in lottery_data['users']:
                    for i in range(0, lottery_data['users'][participant]):
                        participants.append(participant)
                        random.shuffle(participants)

                # Choose the winner :)
                winner = get_user(random.choice(participants))
                winner_data = bot.db.get_user_data(winner.uid)

                while winner_data['ignored']:
                    winner = get_user(random.choice(participants))
                    winner_data = bot.db.get_user_data(winner.uid)

                # Set the reward
                reward = lottery_data['ticket_price'] * len(participants) * len(lottery_data['users'])

                # Give coins to the winner :)
                bot.db.update_user(winner.uid, {
                    'coins': winner_data['coins'] + reward
                })

                # Output message to all rooms
                for room in bot.get_rooms():
                    if not (
                        room.sleep
                        or room.login_fail
                        or room.lock
                    ):
                        message = bot.lang('COINS_LOTTERY_WINNER', room.lang).format(
                            winner=highlight(
                                winner.name,
                                'Green' if (winner in room.get_user_list()) else 'Gray'
                            ),
                            coins=bot.format_coins(reward, room.lang)
                        )
                        room.message(message)

                # PM the winner
                bot.pm.message(winner, bot.lang('PM_COINS_LOTTERY_WINNER', winner_data['lang']).format(
                    coins=bot.format_coins(reward, winner_data['lang'])
                ))
            else:
                # Print message that the session expired and bot is waiting for needed users
                if (
                    time.time() - lottery_data['last_message'] > lottery_data['message_interval']
                    and not (
                        lottery_data['message_count']
                        and time.time() - lottery_data['last_ticket'] > lottery_data['message_interval']
                    )
                ):
                    lottery_data['last_message'] = time.time()
                    lottery_data['message_count'] += 1

                    for room in bot.get_rooms():
                        if not (
                            room.sleep
                            or room.login_fail
                            or room.lock
                        ):
                            messages = list()
                            messages.append(
                                bot.lang('COINS_LOTTERY_NEEDED_USERS', room.lang).format(
                                    needed_users=lottery_data['needed_users'],
                                    command=highlight('{prefix}buy lottery coins'.format(
                                        prefix=bot.db.get_config('command.prefixes')[0]
                                    ), 'Blue'),
                                    ticket_price=bot.format_coins(lottery_data['ticket_price'], room.lang)
                                )
                            )
                            if lottery_data['users']:
                                messages.append(
                                    bot.lang('LOTTERY_REGISTERED_USERS', room.lang).format(
                                        users=', '.join([
                                            '{username} ({tickets})'.format(
                                                username=highlight(
                                                    user.name,
                                                    'Green' if (user in room.get_user_list()) else 'Gray'
                                                ),
                                                tickets=lottery_data['users'][user.uid]
                                            )
                                            for user in [
                                                get_user(uid)
                                                for uid in lottery_data['users']
                                            ]
                                        ]),
                                        count=len(lottery_data['users'])
                                    )
                                )
                            room.message(bot.indented_lines(messages))
        else:
            if (
                time.time() - lottery_data['last_message'] > lottery_data['message_interval']
                and not (
                    lottery_data['message_count']
                    and time.time() - lottery_data['last_ticket'] > lottery_data['message_interval']
                )
            ):
                lottery_data['last_message'] = time.time()
                lottery_data['message_count'] += 1

                for room in bot.get_rooms():
                    if not (
                        room.sleep
                        or room.login_fail
                        or room.lock
                    ):
                        messages = list()
                        messages.append(
                            bot.lang('COINS_LOTTERY_REMAINING', room.lang).format(
                                remaining=format_seconds_to_short_string(lottery_data['session_end'] - time.time()),
                                command=highlight('{prefix}buy lottery coins'.format(
                                    prefix=bot.db.get_config('command.prefixes')[0]
                                ), 'Blue'),
                                ticket_price=bot.format_coins(lottery_data['ticket_price'], room.lang)
                            )
                        )
                        if lottery_data['users']:
                            messages.append(
                                bot.lang('LOTTERY_REGISTERED_USERS', room.lang).format(
                                    users=', '.join([
                                        '{username} ({tickets})'.format(
                                            username=highlight(
                                                user.name,
                                                'Green' if (user in room.get_user_list()) else 'Gray'
                                            ),
                                            tickets=lottery_data['users'][user.uid]
                                        )
                                        for user in [
                                            get_user(uid)
                                            for uid in lottery_data['users']
                                        ]
                                    ]),
                                    count=len(lottery_data['users'])
                                )
                            )
                        room.message(bot.indented_lines(messages))


def level_downgrade(bot):
    # Interval (approximately 1 day)
    now = int(time.time())
    interval = 3600 * 24 - 1

    # User list
    users = bot.db.get_users()

    for user in users:
        user_data = bot.db.get_user_data(user)

        if (
            user_data['level'] > 1
            and not user_data['parked']
        ):
            last_seen = bot.db.get_seen(user)

            if (
                last_seen
                and now - int(last_seen['time']) > interval
            ):
                bot.db.update_user(user, {
                    'level': user_data['level'] - 1
                })


def bank_interest(bot):
    users = bot.db.get_users()
    for user in users:
        user_data = bot.db.get_user_data(user)

        if (
            user_data['bank']
            and not user_data['ignored']
            and not user_data['parked']
        ):
            earnings = int(percentage(
                user_data['level'] / 10,
                user_data['bank']
            ))

            if earnings:
                bot.db.update_user(user, {
                    'bank': user_data['bank'] + earnings,
                    'bank_earnings': user_data['bank_earnings'] + earnings
                })


def bank_earnings(bot):
    users = bot.db.get_users()

    for user in users:
        user_data = bot.db.get_user_data(user)

        earnings = user_data['bank_earnings']

        if earnings:
            bot.db.update_user(user, {
                'bank_earnings': 0
            })

            if not user_data['ignored'] and not user_data['parked']:
                target_user = get_user(user)

                to_send = bot.lang('BANK_EARNINGS', user_data['lang']).format(
                    coins=highlight(currency(earnings), 'Yellow')
                )

                bot.pm.message(target_user, to_send)

                # Delay the messages sending manually
                time.sleep(3)


def delete_expired_whois_data(bot):
    # Interval (approximately one week)
    interval = 3600 * 24 * 7 - 1
    now = int(time.time())

    # Whois
    whois = dict(bot.db.store['whois'])

    for message_uid in whois:
        if (
            len(whois[message_uid]['uids']) == 1
            and now - whois[message_uid]['last_update'] > interval
        ):
            bot.db.remove_whois(message_uid)
            bot.db.store['whois'].pop(message_uid)


def unpark(bot):
    users = bot.db.get_users()

    for user in users:
        user_data = bot.db.get_user_data(user)

        if user_data['parked'] and time.time() > user_data['parked_until']:
            bot.db.update_user(user, {
                'parked': 0
            })