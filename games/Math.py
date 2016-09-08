# Python imports
import math
import time
from random import *

# Project imports
from model.Game import Game
from util.render import *


class Math(Game):
    __min_num = 0
    __max_num = 10
    __max_numbers = 2
    __operators = ['+', '-', '*', '/']

    def __init__(self, room):
        super().__init__(room)

        self.__result = None
        self.__expr = None
        self.__msgs = None
        self.__count = 0
        self.__reward = 0
        self.__number_count = None
        self.__average = None

        if self.room.user_count < 10:
            self._message(self._lang('ERROR_LOADING_GAME_USERS_NOT_ENOUGH'))
            self.stop()
        else:
            self.__next()

    def action(self, user, user_data, message):
        self.skip = True

        if message == str(self.__result):
            self._message(self._lang('MATH_USER_REWARDED').format(
                username=self._user_color(user),
                answer=highlight(self.__result, 'Blue'),
                reward=self._format_coins(self.__reward)
            ))

            self.db.update_user(user.uid, {
                'coins': (user_data['coins'] + self.__reward)
            })

            time.sleep(3)

            self.__next()
        else:
            self.__msgs += 1

            if 6 == self.__msgs:
                self.__msgs = 0
                self._message(self._lang('MATH_SOLVE_THE_EXPRESSION').format(
                    expression=highlight(self.__expr, 'Yellow'),
                    reward=self._format_coins(self.__reward)
                ), save=True)

        self.skip = False

    def __next(self):
        try:
            self.__number_count = 1
            self.__average = 0
            self.__expr = self.__expression(self.__max_numbers)
            self.__result = eval(self.__expr)

            assert(self.__result == int(self.__result))

            if 0 != self.__reward:
                self.__max_num += 1
                self.__count += 1

                if self.__count % 5 == 0:
                    self.__min_num += 1
                if self.__count % 10 == 0:
                    if self.__max_numbers < 2**3:
                        self.__max_numbers *= 2
                    else:
                        self.__max_numbers = 2
                if self.__count % 50 == 0:
                    self.__max_num = 10
                    self.__min_num = 0
            else:
                self.__count = 0

            self.__result = int(self.__result)
            self.__msgs = 0
            self.__reward = self.__number_count + int(self.__average / self.__number_count)

            self._message(self._lang('MATH_SOLVE_THE_EXPRESSION').format(
                expression=highlight(self.__expr, 'Yellow'),
                reward=self._format_coins(self.__reward)
            ), save=True)
        except ZeroDivisionError:
            self.__next()
        except AssertionError:
            self.__next()

    def __expression(self, max_numbers, max_depth=None, depth=0):
        # max_numbers has to be a power of 2
        if max_depth is None:
            max_depth = math.log(max_numbers, 2) - 1

        if depth < max_depth and randint(0, max_depth) > depth:
            left = self.__expression(max_numbers, max_depth, depth + 1)
        else:
            left = randint(self.__min_num, self.__max_num)
            self.__average += left

        if depth < max_depth and randint(0, max_depth) > depth:
            right = self.__expression(max_numbers, max_depth, depth + 1)
        else:
            right = randint(self.__min_num, self.__max_num)
            self.__average += right

        operator = choice(self.__operators)
        self.__number_count += 1

        return '{0!s} {1} {2!s}'.format(left, operator, right)