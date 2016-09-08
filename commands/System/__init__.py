# Python imports
import traceback

# Project imports
from manager.Command.Utils import *


class System(CommandUtils):
    # rst
    def command_rst(self):
        self.bot.stop()

    # ev
    def command_ev(self):
        success = False
        instruction_type = None
        statement_expression = self.args_raw.replace(self.db.get_config('message.line_breaker'), '\n')

        try:
            eval(statement_expression)
            success = True
            instruction_type = 'expression'
        except:
            try:
                exec(statement_expression)
                success = True
                instruction_type = 'statement'
            except:
                print(traceback.format_exc())

        if success:
            if 'expression' == instruction_type:
                self._message(self._lang('SUCCESS_EV_EXPRESSION').format(
                    username=self._user_color()
                ))
            elif 'statement' == instruction_type:
                self._message(self._lang('SUCCESS_EV_STATEMENT').format(
                    username=self._user_color()
                ))
        else:
            self._message(self._lang('ERROR_EV').format(
                username=self._user_color()
            ))

    # log
    def command_log(self):
        try:
            level = int(self.args[0])

            assert(level in range(0, 3))

            self.db.set_config('log_level', level, persistent=False)
        except:
            self._invalid_usage()