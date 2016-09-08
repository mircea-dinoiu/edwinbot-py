# Python imports
import urllib.parse
import urllib.request
from hashlib import md5
from collections import OrderedDict


class Cleverbot:
    api_url = 'http://www.cleverbot.com/webservicemin'

    def __init__(self):
        """ The data that will get passed to Cleverbot's web API """
        self.data = OrderedDict()
        self.clean_dict()

    @staticmethod
    def __util_string_at_index(strings, index):
        if len(strings) > index:
            return strings[index]
        else:
            return ''
        
    def clean_dict(self):
        self.data.clear()
        self.data['start'] = 'y'
        self.data['icognoid'] = 'wsf'
        self.data['fno'] = '0'
        self.data['sub'] = 'Say'
        self.data['islearning'] = '1'
        self.data['cleanslate'] = 'false'

    def chat(self, message):
        # Set the current message
        self.data['stimulus'] = message

        data = urllib.parse.urlencode(self.data)
        data_to_digest = data[9:35]
        
        data_digest = md5(data_to_digest.encode('ascii')).hexdigest()

        self.data['icognocheck'] = data_digest
        post_data = urllib.parse.urlencode(self.data).encode('ascii')
        req = urllib.request.Request(self.api_url, post_data)
        url_response = urllib.request.urlopen(req)
        response = url_response.read().decode('utf-8')
        
        response_values = response.split('\r')
        #self.data['??'] = _util_string_at_index(response_values, 0)
        self.data['sessionid'] = self.__util_string_at_index(response_values, 1)
        self.data['logurl'] = self.__util_string_at_index(response_values, 2)
        self.data['vText8'] = self.__util_string_at_index(response_values, 3)
        self.data['vText7'] = self.__util_string_at_index(response_values, 4)
        self.data['vText6'] = self.__util_string_at_index(response_values, 5)
        self.data['vText5'] = self.__util_string_at_index(response_values, 6)
        self.data['vText4'] = self.__util_string_at_index(response_values, 7)
        self.data['vText3'] = self.__util_string_at_index(response_values, 8)
        self.data['vText2'] = self.__util_string_at_index(response_values, 9)
        self.data['prevref'] = self.__util_string_at_index(response_values, 10)
        #self.data['??'] = self.__util_string_at_index(response_values, 11)
        self.data['emotionalhistory'] = self.__util_string_at_index(response_values, 12)
        self.data['ttsLocMP3'] = self.__util_string_at_index(response_values, 13)
        self.data['ttsLocTXT'] = self.__util_string_at_index(response_values, 14)
        self.data['ttsLocTXT3'] = self.__util_string_at_index(response_values, 15)
        self.data['ttsText'] = self.__util_string_at_index(response_values, 16)
        self.data['lineRef'] = self.__util_string_at_index(response_values, 17)
        self.data['lineURL'] = self.__util_string_at_index(response_values, 18)
        self.data['linePOST'] = self.__util_string_at_index(response_values, 19)
        self.data['lineChoices'] = self.__util_string_at_index(response_values, 20)
        self.data['lineChoicesAbbrev'] = self.__util_string_at_index(response_values, 21)
        self.data['typingData'] = self.__util_string_at_index(response_values, 22)
        self.data['divert'] = self.__util_string_at_index(response_values, 23)

        if len(self.data['ttsText'].strip()) < 1:
            self.clean_dict()
            self.chat(message)
            
        # Return Cleverbot's response
        return self.data

if __name__ == "__main__":
    cb = Cleverbot()

    while True:
        myMessage = input('You: ')
        print('Bot: ' + cb.chat(myMessage)['ttsText'])