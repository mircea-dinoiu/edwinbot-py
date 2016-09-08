# Project imports
from manager.Command.Utils import *


class LevelRelated(CommandUtils):
    # level
    def command_level(self):
        if not self.args:
            user_data = self.user_data

            self._message(self._lang('YOUR_LEVEL').format(
                level=highlight(user_data['level'], 'Blue'),
                coins=self._format_coins(user_data['coins']),
                me=self._user_color()
            ))
        else:
            uid = self._get_user_uid(self.args[0])
            self._validate_username(uid)
                        
            if uid == self.bot.user.uid:
                self.args_raw = 'How much coins do you have?'
                self._launch('chat')
                return
                
            user_data = self.db.get_user_data(uid)
            
            # User doesn't exist
            if 0 == user_data['level']:
                self._message(self._lang('ERROR_USER_NOT_IN_DB').format(
                    self._user_color(uid),
                    self._user_color()
                ))
                return
            
            self._message(self._lang('USER_LEVEL').format(
                username=self._user_color(uid),
                level=highlight(user_data['level'], 'Blue'),
                coins=self._format_coins(user_data['coins'])
            ))

    # tradelevel
    def command_tradelevel(self):
        user_data = self.user_data

        paying = get_level_price(user_data['level'])
        
        self.db.update_user(self.user.uid, {
            'coins': user_data['coins'] + paying,
            'level': user_data['level'] - 1
        })
        
        self._message(self._lang('SUCCESS_TRADE_LEVEL').format(
            coins=self._format_coins(paying),
            me=self._user_color()
        ))