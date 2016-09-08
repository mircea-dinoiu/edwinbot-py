from xml.dom import minidom

from commands.Entertainment.TheCannon import *


class Entertainment(TheCannon):
    # google
    def command_google(self):
        if not self.args:
            self._invalid_usage()
        else:
            if self.pm:
                message = 'http://lmgtfy.com/?q={0}'.format(self.args_raw)
            else:
                message = '<a href="http://lmgtfy.com/?q={0}" target="_blank"><u>{0}</u></a>'.format(
                    self.args_raw
                )

            self._message(message)

    # gag
    def command_9gag(self):
        raw = str(
            request.urlopen(
                'http://9gagrss.com/feed/'
            ).read().decode('utf-8')
        )
        xmldoc = minidom.parseString(raw)
        itemlist = xmldoc.getElementsByTagName('item')

        while True:
            gag = random.choice(itemlist)

            title = gag.getElementsByTagName('title')[0].firstChild.data
            url = gag.getElementsByTagName('link')[0].firstChild.data

            description = gag.getElementsByTagName('description')[0].firstChild.data
            description_obj = re.match(r'.+<img src="([^"]+\.jpg)" />.+', description, re.IGNORECASE)

            if description_obj:
                if self.pm:
                    message = '{title} ( {url} ) <i s="{image}" w="125" h="93.75"/>'.format(
                        title=title,
                        url=url,
                        image=description_obj.group(1)
                    )
                else:
                    message = '{title} ( {url} ) {image}'.format(
                        title=title,
                        url=highlight(url, flags='u'),
                        image=description_obj.group(1)
                    )

                self._message(message)
                return

    # chat
    def command_chat(self):
        if not self.args:
            self._invalid_usage()
        else:
            bot_name = self.db.get_config('bot.name')

            message = re.sub("(?i)" + bot_name, "Cleverbot", self.args_raw)

            verify = set(''.join(re.findall("[a-zA-Z]+", message)).lower())

            if len(verify) < 3:
                return

            try:
                cb = self.user.cb
                response = cb.chat(message)
                if '&' in response['ttsText']:
                    self._launch('chat')
                else:
                    answer = re.sub('(?i)cleverbot', bot_name, response['ttsText'])

                    if answer.strip() != '':
                        answer = answer
                        if self.pm:
                            self._message(answer)
                        else:
                            self._message('{0} {1}'.format(
                                self._user_color(),
                                answer
                            ))
            except:
                if self.log_level > 0:
                    raise