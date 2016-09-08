# Project imports
from manager.Command.Utils import *


class Listening(CommandUtils):
    # listen
    def command_listen(self):
        if not self.args:
            entries = list()

            for listened, uids in self.db.store['listen'].items():
                if self.user.uid in uids:
                    entries.append(listened)

            if entries:
                self._message(self._lang('LISTENED_LIST').format(
                    username=self._user_color(),
                    listened_list=', '.join([
                        highlight(each, 'Pink')
                        for each in entries
                    ])
                ))
            else:
                self._message(self._lang('LISTENED_LIST_EMPTY').format(
                    username=self._user_color()
                ))
        else:
            listened = self.args_raw.lower()
            existing = False

            if listened in self.db.store['listen']:
                if self.user.uid in self.db.store['listen'][listened]:
                    self._message(self._lang('ERROR_LISTEN_ALREADY_LISTENING').format(
                        username=self._user_color(),
                        listened=highlight(listened, 'Pink')
                    ))
                    return
                else:
                    existing = True

            self._message(self._lang('SUCCESS_LISTEN').format(
                username=self._user_color(),
                listened=highlight(listened, 'Pink')
            ))

            if existing:
                self.db.store['listen'][listened].append(self.user.uid)
            else:
                self.db.store['listen'][listened] = [self.user.uid]

            self.db.set_listen(listened, self.db.store['listen'][listened])

    # unlisten
    def command_unlisten(self):
        if not self.args:
            self._invalid_usage()
        else:
            listened = self.args_raw.lower()

            if (
                listened in self.db.store['listen']
                and self.user.uid in self.db.store['listen'][listened]
            ):
                self._message(self._lang('SUCCESS_UNLISTEN_LISTEN_REMOVED').format(
                    username=self._user_color(),
                    listened=highlight(listened, 'Pink')
                ))

                self.db.store['listen'][listened].remove(self.user.uid)

                if self.db.store['listen'][listened]:
                    self.db.set_listen(listened, self.db.store['listen'])
                else:
                    self.db.remove_listen(listened)
                    self.db.store['listen'].pop(listened)
            else:
                self._message(self._lang('ERROR_UNLISTEN_NOT_LISTENING').format(
                    username=self._user_color(),
                    listened=highlight(listened, 'Pink')
                ))