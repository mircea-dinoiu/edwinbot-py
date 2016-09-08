# Project imports
from manager.Command.Utils import *


class Contacts(CommandUtils):
    # contacts
    def command_contacts(self):
        contacts = self.bot.pm.contacts

        if not isinstance(contacts, set):
            self._message(self._lang('ERROR_CONTACT_LIST_CANNOT_BE_RETRIEVED').format(
                me=self._user_color()
            ))
        elif contacts:
            def fn_join(array):
                return ', '.join([
                    self._user_color(each)
                    for each in array
                ])

            def fn_get_message_params(**kwargs):
                return {
                    'contacts': kwargs['joined_string']
                }

            self._output_long_list(
                fn_join=fn_join,
                array=[user.uid for user in contacts],
                lang_key='PM_CONTACT_LIST',
                fn_get_format_params=fn_get_message_params
            )
        else:
            self._message(self._lang('PM_CONTACT_LIST_EMPTY').format(
                me=self._user_color()
            ))

    # addcontacts
    def command_addcontacts(self):
        if not self.args:
            self._invalid_usage()
        else:
            if not isinstance(self.bot.pm.contacts, set):
                self._message(self._lang('ERROR_PM_CANNOT_ADD_CONTACTS').format(
                    me=self._user_color()
                ))
            else:
                uids = self.args

                messages = list()

                invalid_usernames = list()
                people_added = list()
                people_not_added = list()

                for uid in uids:
                    contact = self._get_user_uid(uid)

                    if contact not in (invalid_usernames + people_added + people_not_added):
                        if self._validate_username(contact, exception=False) and not is_anon(contact):
                            user = get_user(contact)

                            if user in self.bot.pm.contacts:
                                people_not_added.append(contact)
                            else:
                                self.bot.pm.add_contact(user)
                                people_added.append(contact)
                        else:
                            invalid_usernames.append(contact)

                if people_added:
                    messages.append(
                        self._lang('SUCCESS_PM_CONTACTS_ADDED').format(
                            contacts=', '.join([
                                self._user_color(each_uid)
                                for each_uid in people_added
                            ]),
                            me=self._user_color()
                        )
                    )

                if people_not_added:
                    messages.append(
                        self._lang('ERROR_PM_CONTACTS_ALREADY_EXISTS').format(
                            contacts=', '.join([
                                self._user_color(each_uid)
                                for each_uid in people_not_added
                            ]),
                            me=self._user_color()
                        )
                    )

                if invalid_usernames:
                    messages.append(
                        self._lang('ERROR_INVALID_USERNAMES').format(
                            usernames=', '.join([
                                highlight(each_username, 'Gray')
                                for each_username in invalid_usernames
                            ]),
                            me=self._user_color()
                        )
                    )

                self._message(self.bot.indented_lines(messages))

    # removecontacts
    def command_removecontacts(self):
        if not self.args:
            self._invalid_usage()
        else:
            if not isinstance(self.bot.pm.contacts, set):
                self._message(self._lang('ERROR_PM_CANNOT_REMOVE_CONTACTS').format(
                    me=self._user_color()
                ))
            else:
                uids = self.args

                messages = list()

                invalid_usernames = list()
                people_removed = list()
                people_not_removed = list()

                for uid in uids:
                    contact = self._get_user_uid(uid)

                    if contact not in (invalid_usernames + people_removed + people_not_removed):
                        if self._validate_username(contact, exception=False) and not is_anon(contact):
                            user = get_user(contact)

                            if user not in self.bot.pm.contacts:
                                people_not_removed.append(contact)
                            else:
                                self.bot.pm.remove_contact(user)
                                people_removed.append(contact)
                        else:
                            invalid_usernames.append(contact)

                if people_removed:
                    messages.append(
                        self._lang('SUCCESS_PM_CONTACTS_REMOVED').format(
                            contacts=', '.join([
                                self._user_color(each_uid)
                                for each_uid in people_removed
                            ]),
                            me=self._user_color()
                        )
                    )

                if people_not_removed:
                    messages.append(
                        self._lang('ERROR_PM_CONTACTS_NOT_EXISTING').format(
                            contacts=', '.join([
                                self._user_color(each_uid)
                                for each_uid in people_not_removed
                            ]),
                            me=self._user_color()
                        )
                    )

                if invalid_usernames:
                    messages.append(
                        self._lang('ERROR_INVALID_USERNAMES').format(
                            usernames=', '.join([
                                highlight(each_username, 'Gray')
                                for each_username in invalid_usernames
                            ]),
                            me=self._user_color()
                        )
                    )

                self._message(self.bot.indented_lines(messages))