# Python imports
import re
import os

# Third Party imports
from unidecode import unidecode

# Project imports
from model.Game import Game
from util.render import *


class Pheasant(Game):
    __reward = 25
    __end_reward = 100

    def __init__(self, room):
        super().__init__(room)

        self.__file_path = '{0}/data/games/wordlists/lang.{1}'.format(
            self.db.get_config('root_path'),
            self.room.lang
        )
        self.__used_words = None
        self.__told = None
        self.__suffix = None
        self.__ignore = None
        self.__msgs = None
        self.__word_list = list()
                
        if self.room.user_count < 10:
            self._message(self._lang('ERROR_LOADING_GAME_USERS_NOT_ENOUGH'))
            self.stop()
        elif not os.path.isfile(self.__file_path):
            self._message(self._lang('ERROR_LOADING_GAME_LANG_NOT_MATCH'))
            self.stop()
        else:
            self.__create_word_list()
            self.__next()
    
    def action(self, user, user_data, message):
        self.skip = True

        msg = message.lower()
        
        # If no word is set yet, or the game has ended
        if not self.__suffix:
            check = self.__word_check(msg)
            error = None
            
            if check['word'] in self.__used_words:
                error = 'ERROR_PHEASANT_WORD_ALREADY_USED'
            elif len(msg) < 3:
                error = 'ERROR_PHEASANT_WORD_TOO_SHORT'
            elif not check['valid']:
                error = 'ERROR_PHEASANT_WORD_INCORRECT'
            elif self.__game_end(check['word'][-2:]):
                error = 'ERROR_PHEASANT_WORD_TYPE_END'
            
            if error:
                pass
                # if 'ERROR_PHEASANT_WORD_TYPE_END' == error:
                #     self.message(self._lang(error).format(
                #         me=self._user_color()
                #     ))
                # else:
                #     self.message(self._lang(error).format(
                #         word=highlight(msg, 'Blue'),
                #         me=self._user_color()
                #     ))
            else:
                # Someone has started the game with word bla bla...
                reward = self.__reward
                self._message(self._lang('PHEASANT_STARTED_THE_GAME').format(
                    username=self._user_color(user),
                    word=msg[:-2] + highlight(msg[-2:], flags='u'),
                    prefix=highlight(msg[-2:], 'Yellow'),
                    reward=self._format_coins(reward)
                ), save=True)

                self.__mark_as_used(check['word'])
                self.__next(check['word'][-2:], user)

                # Giving user the reward
                self.db.update_user(user.uid, {
                    'coins': (user_data['coins'] + reward)
                })
        # If game is running
        else:
            msg = unidecode(msg)
            if user.uid == self.__ignore.uid:
                if (
                    not self.__told
                    and msg in self.__word_list
                ):
                    self._message(self._lang('ERROR_PHEASANT_NOT_YOUR_TURN').format(
                        me=self._user_color(user)
                    ))
                    self.__told = True
            else:
                reward = None
                if msg[0:2] == self.__suffix:
                    if msg in self.__used_words:
                        if not self.__used_words[msg]:
                            self._message(self._lang('ERROR_PHEASANT_WORD_ALREADY_USED').format(
                                word=highlight(msg, 'Blue'),
                                me=self._user_color(user)
                            ))
                            self.__used_words[msg] = True
                    else:
                        # If messages seems to be fine
                        if len(msg) >= 3:
                            check = self.__word_check(msg, False)
                            msg = check['word']
                            # Check dictionary
                            if check['valid']:
                                # Game-closing word
                                if self.__game_end(msg[-2:]):
                                    reward = self.__end_reward
                                    self._message(self._lang('PHEASANT_USER_REWARDED_END').format(
                                        username=self._user_color(user),
                                        reward=self._format_coins(reward)
                                    ))
                                    self.__next()
                                # Good word
                                else:
                                    reward = self.__reward

                                    messages = [
                                        self._lang('PHEASANT_USER_REWARDED').format(
                                            username=self._user_color(user),
                                            reward=self._format_coins(reward)
                                        ),
                                        self._lang('PHEASANT_WAITING_FOR_A_SPECIFIC_WORD').format(
                                            prefix=highlight(msg[-2:], 'Yellow')
                                        )
                                    ]

                                    self._message(self.bot.indented_lines(messages), save=True)
                                    self.__next(msg[-2:], user)
                                
                                # Giving user the reward
                                self.db.update_user(user.uid, {
                                    'coins': (user_data['coins'] + reward)
                                })
                                
                                # Mark as used
                                self.__mark_as_used(msg)
                
                if reward is None:
                    if self.__msgs == 6:
                        self._message(self._lang('PHEASANT_NOBODY_ANSWERED').format(
                            prefix=highlight(self.__suffix, 'Yellow')
                        ), save=True)
                        self.__next()
                    self.__msgs += 1
                        
        self.skip = False
        
    def __mark_as_used(self, word):
        self.__used_words[word] = False
        self.__word_list.remove(word)
        
        if 0 == len(self.__word_list):
            self.__create_word_list()
        
    def __next(self, suffix=None, ignore=None):
        self.__suffix = suffix
        self.__ignore = ignore
        self.__told = False
        self.__msgs = 0
        
        if not suffix:
            self._message(self._lang('PHEASANT_WAITING_FOR_A_WORD'), save=True)
            
    def __word_check(self, word, parse_unidecode=True):
        if parse_unidecode:
            word = unidecode(word)
        
        r_word = re.sub(r'\W+', '', word)
                
        if len(r_word) >= 2 and word == r_word:
            valid = (r_word in self.__word_list)
        else:
            valid = False
                
        return {
            'valid': valid,
            'word': r_word
        }
        
    def __game_end(self, prefix):
        for word in self.__word_list:
            if word.startswith(prefix):
                return False
        
        return True
        
    def __create_word_list(self):
        self.__used_words = {}
        with open(self.__file_path, 'r+', encoding='utf-8') as file:
            for line in file:
                line = line.replace('\n', '')
                if len(line) >= 3:
                    self.__word_list.append(unidecode(line).lower())