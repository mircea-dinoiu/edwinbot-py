# Python imports
import json

# Project imports
from lib.Youtube import *
from manager.Command.Utils import *


class Searching(CommandUtils):
    # youtube
    def command_youtube(self):
        if not self.args:
            self._invalid_usage()
        else:
            try:
                raw = str(
                    request.urlopen(
                        'http://gdata.youtube.com/feeds/api/videos?vq={0}&racy=include&orderby=relevance&max-results=1'
                        .format("+".join(self.args))
                    ).read().decode('utf-8')
                )

                xml_doc = minidom.parseString(raw)
                item_list = xml_doc.getElementsByTagName('entry')

                if not item_list:
                    self._message(self._lang('ERROR_NOT_FOUND').format(
                        highlight(self.args_raw, 'Blue')
                    ))
                else:
                    video = item_list[0]
                    video_id = video.getElementsByTagName('id')[0].firstChild.data.replace(
                        'http://gdata.youtube.com/feeds/api/videos/',
                        ''
                    )
                    video_title = video.getElementsByTagName('title')[0].firstChild.data
                    video_author = video.getElementsByTagName('author')[0].firstChild.firstChild.data

                    if self.pm:
                        url = '<i s="vid://yt:{video_id}" w="126" h="93"/>'.format(
                            video_id=video_id
                        )
                    else:
                        url = 'http://www.youtube.com/watch?v={0}'.format(
                            video_id
                        )

                    self._message(self._lang('YOUTUBE').format(
                        highlight(video_title, flags='b'),
                        highlight(video_author, flags='u'),
                        url
                    ))
            except:
                if self.log_level > 0:
                    raise

    # image
    def command_image(self):
        if not self.args:
            self._invalid_usage()
        else:
            try:
                raw = str(
                    request.urlopen(
                        'http://ajax.googleapis.com/ajax/services/search/images?q={0}&v=1.0'
                        .format('+'.join(self.args))
                    ).read().decode('utf-8')
                )
                results = json.loads(raw)
                image = random.choice(
                    list(results['responseData']['results'])
                )['unescapedUrl']

                if self.pm:
                    message = '<i s="{image}" w="125" h="93.75"/>'.format(
                        image=image
                    )
                else:
                    message = image

                self._message(message)
            except:
                self._message(self._lang('ERROR_NOT_FOUND').format(
                    highlight(self.args_raw, 'Blue')
                ))
                if self.log_level > 0:
                    raise

    # search
    def command_search(self):
        if not self.args:
            self._invalid_usage()
        else:
            try:
                raw = str(
                    request.urlopen(
                        'http://ajax.googleapis.com/ajax/services/search/web?q={0}&v=1.0'
                        .format('%20'.join(self.args))
                    ).read().decode('utf-8')
                )
                results = json.loads(raw)

                result = random.choice(list(results['responseData']['results']))

                message = '{0} -- <i>{1}</i> : {2}'.format(
                    result['unescapedUrl'], result['title'], result['content']
                )

                self._message(message)
            except:
                self._message(self._lang('ERROR_NOT_FOUND').format(
                    highlight(self.args_raw, 'Blue')
                ))
                if self.log_level > 0:
                    raise