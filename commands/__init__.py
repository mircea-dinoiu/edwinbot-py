# Project imports
from commands.Entertainment import *
from commands.Utilities import *
from commands.Messages import *
from commands.Games import *
from commands.Users import *
from commands.Streams import *
from commands.Rooms import *
from commands.PrivateMessaging import *
from commands.Miscellaneous import *
from commands.System import *


class CommandManager(
    Entertainment,
    Utilities,
    Messages,
    Games,
    Users,
    Streams,
    Rooms,
    PrivateMessaging,
    Miscellaneous,
    System
):
    # help
    def command_help(self):
        wl_message = ''

        if self.user_data['level'] == 0:
            wl_message = self._lang('SUCCESS_WHITE_LIST').format(
                username=self._user_color()
            )
            self.db.add_user(self.user.uid, {
                'level': 1,
                'registered_on': self.connection_name
            })

        if self.pm:
            link = self.db.get_info('website')
        else:
            link = '<a href="{0}" target="_blank">{1}</a>'.format(
                self.db.get_info('website'),
                highlight(self.db.get_info('website')[7:], 'Red', 'u')
            )

        self._message(wl_message + self._lang('BOT_HELP').format(
            link=link,
            cmd_prefixes=' '.join([
                highlight(delimiter, 'Orange', flags='b')
                for delimiter in self.db.get_config('command.prefixes')
            ]),
            cmds=highlight(self.prefix + 'cmds', 'Blue'),
            man='{cmd} {param}'.format(
                cmd=highlight(self.prefix + 'man', 'Blue'),
                param=highlight(self.db.store['help']['man']['params'][self.lang][0].strip('<>'), 'Yellow')
            )
        ))

    # cmds
    def command_cmds(self):
        def fn_join(array):
            return ', '.join([
                highlight(each, 'Red')
                for each in array
            ])

        def fn_get_message_params(**kwargs):
            return {
                'me': self._user_color(),
                'command_list': kwargs['joined_string'],
                'command_count': format_number(
                    number=kwargs['count'],
                    lang=self.lang,
                    many_text=self._lang('COMMANDS'),
                    one_text=self._lang('COMMAND')
                )
            }

        command_list = list()

        for command in list(self.db.store['help']):
            if self._is_allowed(command=command, silent=True):
                command_list.append(command)

        self._output_long_list(
            fn_join=fn_join,
            array=command_list,
            lang_key='COMMAND_LIST',
            fn_get_format_params=fn_get_message_params
        )

    # man
    def command_man(self):
        if not self.args:
            self._invalid_usage()
        else:
            command_name = self.args[0]
            command = self.bot.get_command(command_name)

            try:
                manual = self.db.store['help'][command]

                # Category
                category = None
                if 0 != len(manual['parents']):
                    category = ' » '.join([
                        highlight(parent[self.lang], 'Pink')
                        for parent in manual['parents']
                    ])

                # Aliases
                aliases = ' '.join(manual['aliases']) if manual['aliases'] else None

                # Command parameters
                if manual['params']:
                    params = list()
                    for param in manual['params'][self.lang]:
                        if '<' in param and '>' in param:
                            param = ' {0} '.format(param)

                            before = param.split('<')[0].strip()
                            after = param.split('>')[1].strip()
                            param = param.split('<')[1].split('>')[0].strip()

                            param_string = ''

                            if before:
                                param_string += highlight(before, 'Green') + (' ' if before[-1] != '[' else '')
                            param_string += highlight(param, 'Red')
                            if after:
                                param_string += (' ' if after[-1] != ']' else '') + highlight(after, 'Green')
                        else:
                            param_string = highlight(param, 'Green')

                        params.append(param_string)
                    params = ' ' + ' '.join(params)
                else:
                    params = ''

                # Requirements
                requirements = ', '.join([
                    (' ' + self._lang('OR') + ' ').join(requirement.split('|'))
                    for requirement in manual['requirements']
                ])
                requirements = requirements.replace(
                    '@UisM@',
                    self._lang('MAN_REQUIRES_USER_MODERATOR_ACCESS')
                ).replace(
                    '@BisM@',
                    self._lang('MAN_REQUIRES_BOT_MODERATOR_ACCESS').format(
                        bot_name=self._user_color(self.bot.user.uid)
                    )
                )

                # Description
                desc_array = manual['description'][self.lang].split(
                    self.db.get_config('message.line_breaker')
                )
                spacer = self.db.get_config('message.line_breaker') + ' ' * 10
                raw_desc = spacer + spacer.join(desc_array)
                description = raw_desc.replace(
                    '@BotName@',
                    self._user_color(self.bot.user.uid)
                )

                # Create the message
                parts = list()
                parts.append(self.db.get_config('message.line_breaker'))

                if category:
                    parts.append(self._lang('MAN_CATEGORY').format(
                        category=category
                    ))
                parts.append(self._lang('MAN_COMMAND').format(
                    command=highlight(command, 'Green') + params
                ))
                if aliases:
                    parts.append(self._lang('MAN_ALIASES').format(
                        aliases=highlight(aliases, 'Blue')
                    ))
                parts.append(self._lang('MAN_REQUIREMENTS').format(
                    requirements=requirements
                ))
                parts.append(self._lang('MAN_DESCRIPTION').format(
                    description=description
                ))

                message = self.db.get_config('message.line_breaker').join(parts)
                message += self.db.get_config('message.line_breaker')

                # Output the message
                self._message(message)
            except:
                self._message(self._lang('ERROR_COMMAND_NOT_EXISTING').format(
                    highlight(command_name, 'Orange'),
                    self._user_color()
                ))
                if self.log_level > 0:
                    raise

    # info
    def command_info(self):
        self._message(self._lang('BOT_INFO').format(
            highlight(len(self.db.store['help']), 'Red'),
            highlight(self.db.get_rooms_count(), 'Yellow'),
            highlight(self.db.get_users_count(), 'Yellow'),
            highlight(self.db.get_definitions_count(), 'Yellow'),
            highlight(self.db.get_info('version'), 'Pink')
        ))