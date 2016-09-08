# Python imports
import re
import os
from random import *

# Third Party imports
from unidecode import unidecode

# Project imports
from model.Game import Game
from util.render import *


class Trivia(Game):
    __reward_per_char = 10
    __hidden_char = '_'

    def __init__(self, room):
        super().__init__(room)

        self.__file_path = '{0}/data/games/trivia/quiz.{1}' . format(
            self.db.get_config('root_path'),
            self.room.lang
        )
        self.__current = None
        self.__quiz = list()
        self.__the_hint = None
        self.__msgs = None
        self.__reward = 0
        
        if self.room.user_count < 10:
            self._message(self._lang('ERROR_LOADING_GAME_USERS_NOT_ENOUGH'))
            self.stop()
        elif not os.path.isfile(self.__file_path):
            self._message(self._lang('ERROR_LOADING_GAME_LANG_NOT_MATCH'))
            self.stop()
        else:
            self.__load_quiz()
            self.__next()
            
    def action(self, user, user_data, message):
        self.skip = True
        
        msg = message.lower()
        
        if msg in self.__current['answers']:
            self._message(self._lang('TRIVIA_ANSWER_FOUND').format(
                username=self._user_color(user),
                answer=highlight(self.__current['answers'][0], 'Blue'),
                reward=self._format_coins(self.__reward)
            ))
            
            self.db.update_user(user.uid, {
                'coins': (user_data['coins'] + self.__reward)
            })
            self.__next()
        elif 'hint' == msg:
            self.__hint()
        elif 5 == self.__msgs:
            self.__hint()
        else:
            self.__msgs += 1
            
        self.skip = False
        
    def __next(self):
        if 0 == len(self.__quiz):
            self.__load_quiz()
        self.__current = choice(self.__quiz)
        self.__quiz.remove(self.__current)
        self.__the_hint = self.__hidden_char * len(self.__current['answers'][0])
        self.__msgs = 0
        self.__reward = self.__reward_per_char * len(self.__current['answers'][0])
        
        self._message(self._lang('TRIVIA_QUESTION').format(
            question=self.__current['question'],
            reward=self._format_coins(self.__reward)
        ), save=True)
        
    def __hint(self):
        # The reward is decreasing...
        self.__reward -= self.__reward_per_char
        
        # Nobody answered to the question, telling the answer
        if 0 == self.__reward:
            self._message(self._lang('TRIVIA_ANSWER_NOT_FOUND').format(
                answer=highlight(self.__current['answers'][0], 'Blue')
            ))
            self.__next()
        else:
            # Replace a random hidden character with a character from the answer
            while True:
                index = randint(0, len(self.__current['answers'][0]) - 1)
                if self.__hidden_char == self.__the_hint[index]:
                    hint_list = list(self.__the_hint)
                    hint_list[index] = self.__current['answers'][0][index]
                    self.__the_hint = ''.join(hint_list)
                    break

            self._message(
                self.bot.indented_line(
                    self._lang('TRIVIA_QUESTION').format(
                        question=self.__current['question'],
                        reward=self._format_coins(self.__reward)
                    ),
                    self._lang('TRIVIA_HINT').format(
                        hint=self.__the_hint
                    )
                ),
                save=True
            )

            self.__msgs = 0
        
    def __load_quiz(self):
        with open(self.__file_path, 'r+', encoding='utf-8') as file:
            for line in file:
                match_obj = re.match(r'^\[([^\[\]]+)\]\[([^\[\]]+)\]$', line, re.M | re.I)
            
                if match_obj:
                    self.__quiz.append({
                        'question': match_obj.group(1),
                        'answers': [
                            match_obj.group(2),
                            match_obj.group(2).lower(),
                            unidecode(match_obj.group(2)).lower()
                        ]
                    })