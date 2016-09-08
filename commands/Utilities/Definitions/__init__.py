# Project imports
from manager.Command.Utils import *


class Definitions(CommandUtils):
    # definitions
    def command_definitions(self):
        pass

    # define
    def command_define(self):
        if not self.args:
            self._invalid_usage()
        else:
            array = self.args_raw.split(' as ', 1)
            keyword = array[0].strip()

            current_definition = self.db.get_definition_data(keyword)

            if len(array) == 1:
                if not current_definition['definition']:
                    for definition in sorted(self.db.get_definitions()):
                        if definition.startswith(keyword.lower()):
                            current_definition = self.db.get_definition_data(definition)
                            keyword = definition
                            break

                if current_definition['definition']:
                    self._message('{0}: {1}<br>-- {2}<br>'.format(
                        highlight(self._htmlize(keyword), flags='b'),
                        self._htmlize(close_html_tags(current_definition['definition'])),
                        self._user_color(current_definition['initiator'])
                    ))
                else:
                    self._message(self._lang('ERROR_NOT_DEFINED').format(
                        highlight(self._htmlize(keyword), flags='b')
                    ))
            elif len(array) == 2:
                if self._is_allowed(True):
                    definition = close_html_tags(array[1].strip())

                    if current_definition['definition']:
                        if current_definition['initiator'] != self.user.uid:
                            self._message(self._lang('ERROR_ALREADY_DEFINED').format(
                                highlight(self._htmlize(keyword), flags='b'),
                                self._user_color(current_definition['initiator'])
                            ))
                            return

                    self.db.update_definition(keyword, {
                        'initiator': self.user.uid,
                        'definition': definition
                    })

                    self._message('{0}: {1}<br>-- {2}<br>'.format(
                        highlight(self._htmlize(keyword), flags='b'),
                        self._htmlize(definition),
                        self._user_color(use_nick=False)
                    ))

    # undefine
    def command_undefine(self):
        if not self.args:
            self._invalid_usage()
        else:
            keyword = self.args_raw

            current_definition = self.db.get_definition_data(keyword)

            if not current_definition['definition']:
                self._message(self._lang('ERROR_NOT_DEFINED').format(
                    highlight(self._htmlize(keyword), flags='b')
                ))
            else:
                if current_definition['initiator'] == self.user.uid:
                    self._message(self._lang('SUCCESS_UNDEFINE').format(
                        keyword=highlight(keyword, flags='b'),
                        username=self._user_color()
                    ))

                    self.db.remove_definition(keyword)
                else:
                    self._message(self._lang('ERROR_UNDEFINE_NO_ACCESS').format(
                        highlight(self._htmlize(keyword), flags='b'),
                        self._user_color(current_definition['initiator'])
                    ))