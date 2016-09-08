# Project imports
from manager.Command.Utils import *


class AccountParking(CommandUtils):
    # park
    def command_park(self):
        if not self.args:
            self._invalid_usage()
        else:
            mapping = {
                'h': 3600,  # 1 hour
                'd': 3600 * 24,  # 24 hours
                'm': 3600 * 24 * 30,  # 30 days
            }

            valid = True
            seconds = 0

            for arg in self.args:
                arg = arg.lower()

                number = arg[:-1]
                duration = arg[-1]

                if mapping.get(duration):
                    try:
                        seconds += mapping[duration] * int(number)
                    except:
                        valid = False
                        break
                else:
                    valid = False
                    break

            if not valid:
                self._invalid_usage()
            else:
                if seconds < mapping['h']:
                    self._message(self._lang('ERROR_PARKING_TIME_TOO_SHORT').format(
                        me=self._user_color()
                    ))
                elif seconds > mapping['m']:
                    self._message(self._lang('ERROR_PARKING_TIME_TOO_LONG').format(
                        me=self._user_color()
                    ))
                else:
                    price = int(round(seconds / 3600) * self.user_data['level'])

                    if price > self.user_data['coins']:
                        self._message(self._lang('ERROR_COINS_NOT_ENOUGH_TO_PARK').format(
                            me=self._user_color(),
                            coins=self._format_coins(price)
                        ))
                    else:
                        self._message(self._lang('SUCCESS_ACCOUNT_PARKED').format(
                            me=self._user_color(),
                            duration=self._format_seconds(seconds),
                            coins=self._format_coins(price)
                        ))

                        self.db.update_user(self.user.uid, {
                            'parked': 1,
                            'parked_until': round(time.time() + seconds),
                            'coins': self.user_data['coins'] - price,
                            'coins_spent': self.user_data['coins_spent'] + price
                        })

    # unpark
    def command_unpark(self):
        if not self.user_data['parked']:
            self._message(self._lang('ERROR_NOT_PARKED').format(
                me=self._user_color()
            ))
        else:
            self._message(self._lang('SUCCESS_UNPARK').format(
                me=self._user_color()
            ))

            self.db.update_user(self.user.uid, {
                'parked': 0,
            })