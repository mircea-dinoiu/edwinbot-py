# Python imports
import os
from random import *

# Third Party imports
from unidecode import unidecode

# Project imports
from model.Game import Game
from util.render import *


class Scramble(Game):
    __reward_per_char = 20
    
    def __init__(self, room):
        super().__init__(room)

        self.file_path = '{0}/data/games/wordlists/lang.{1}'.format(
            self.db.get_config('root_path'),
            self.room.lang
        )
        self.__msgs = None
        self.__answer = None
        self.__reward = 0
        self.__matrix = None
        self.__the_hint = None
        self.__used_words = None
        self.__word_list = None
                
        if self.room.user_count < 10:
            self._message(self._lang('ERROR_LOADING_GAME_USERS_NOT_ENOUGH'))
            self.stop()
        elif not os.path.isfile(self.file_path):
            self._message(self._lang('ERROR_LOADING_GAME_LANG_NOT_MATCH'))
            self.stop()
        else:
            self._create_word_list()
            self.__next()
            
    def action(self, user, user_data, message):
        self.skip = True
        
        msg = unidecode(message.lower())
    
        if msg == unidecode(self.__answer.lower()):
            self._message(self._lang('SCRAMBLE_USER_REWARDED').format(
                username=self._user_color(user),
                answer=highlight(self.__answer, 'Pink'),
                reward=self._format_coins(self.__reward)
            ))
            
            self.db.update_user(user.uid, {
                'coins': (user_data['coins'] + self.__reward)
            })
            self.__next()
        elif 'hint' == msg or 5 == self.__msgs:
            self.__hint()
        else:
            self.__msgs += 1
            
        self.skip = False
            
    def __next(self):
        self.__msgs = 0
    
        word = choice(self.__word_list)
        
        self.__word_list.remove(word)
        self.__used_words.append(word)
        
        word = word.upper()
        
        self.__answer = word
        self.__reward = self.__reward_per_char * (len(word) - 3)
        self.__matrix = [1] + [0] * (len(word) - 2) + [1]
                
        start = word[0]
        middle = word[1:-1]
        end = word[-1:]
        
        letters = list(middle)
        shuffled = list(middle)
        
        while shuffled == letters:
            shuffle(shuffled)
            
        self.__the_hint = start + ''.join(shuffled) + end
        
        self._message(self._lang('SCRAMBLE_REARRANGE_LETTERS').format(
            letters=' '.join([
                highlight(self.__the_hint[i], 'Pink')
                if self.__matrix[i] == 1
                else highlight(self.__the_hint[i], 'Gray')
                for i in range(0, len(self.__the_hint))
            ]),
            reward=self._format_coins(self.__reward)
        ), save=True)

    def __hint(self):
        # The reward is decreasing...
        self.__reward -= self.__reward_per_char
        
        # Nobody answered to the question, telling the answer
        if 0 == self.__reward:
            self.__next()
        else:
            pos = 0
            
            while 1 == self.__matrix[pos]:
                pos = randint(1, len(self.__the_hint)-2)

            if self.__answer[pos] == self.__the_hint[pos]:
                self.__matrix[pos] = 1
            else:
                hint = list(self.__the_hint)
                letter_a = self.__answer[pos]
                letter_b = hint[pos]

                next_pos = None

                middle = hint[1:-1]
                for i in range(0, len(middle)):
                    if letter_a == middle[i] and i + 1 != pos and self.__matrix[i + 1] == 0:
                        next_pos = i + 1

                hint[pos] = letter_a
                hint[next_pos] = letter_b
                self.__matrix[pos] = 1

                self.__the_hint = ''.join(hint)
                
            self._message(self._lang('SCRAMBLE_HINT').format(
                hint=' '.join([
                    highlight(self.__the_hint[i], 'Pink')
                    if self.__matrix[i] == 1
                    else highlight(self.__the_hint[i], 'Gray')
                    for i in range(0, len(self.__the_hint))
                ]),
                reward=self._format_coins(self.__reward)
            ), save=True)
            
            self.__msgs = 0

    def _create_word_list(self):
        self.__used_words = list()
        self.__word_list = list()
        
        with open(self.file_path, 'r+', encoding='utf-8') as file:
            for line in file:
                line = line.replace('\n', '')
                if len(line) in range(5, 9):
                    line = line.lower()
                    self.__word_list.append(line)