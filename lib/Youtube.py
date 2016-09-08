# Python imports
from urllib import request
from xml.dom import minidom


class Video:
    def __init__(self, video_id):
        self._id = video_id
        raw = str(
            request.urlopen(
                'http://gdata.youtube.com/feeds/api/videos/{0}'.format(video_id)
            ).read().decode('utf-8')
        )
        xml_doc = minidom.parseString(raw)
        self._title = xml_doc.getElementsByTagName('title')[0].firstChild.data
        self._author = xml_doc.getElementsByTagName('author')[0].firstChild.firstChild.data

    def get_url(self):
        return 'http://www.youtube.com/watch?v={0}'.format(
            self._id
        )

    def get_id(self):
        return self._id
    
    def get_title(self):
        return self._title
    
    def get_author(self):
        return self._author
        
    url = property(get_url)
    vid = property(get_id)
    title = property(get_title)
    author = property(get_author)