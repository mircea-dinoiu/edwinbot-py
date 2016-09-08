# Python imports
import re
import os
import warnings
import math
from urllib import request

# Third Party imports
from bs4 import BeautifulSoup


def get_level_price(level):
    """
    @type level: int
    @param level: level to get the price for

    @rtype: int
    @return: the level price
    """
    return round(math.sqrt(level)**math.sqrt(level)) * 60


def close_html_tags(html_string):
    """
    Close HTML tags in string

    @type html_string: str
    @param html_string: the string containing HTML tags

    @rtype: str
    @return: the string with all the unclosed HTML tags closed
    """
    warnings.filterwarnings('ignore')
    return str(BeautifulSoup(html_string))


def log_command(command):
    """Output a command call to the log"""
    log_message = '[{connection_name}] {username}: {message}'.format(
        connection_name=command.connection_name,
        username=command.user.name,
        message='{prefix}{command_match}{args}'.format(
            prefix=command.prefix,
            command_match=command.details['match'],
            args=(' ' if command.args_raw else '') + command.args_raw
        )
    )
    
    command.bot.logger.write(log_message, show_time=True, show_date=True, after='\n', brackets=False)


def is_anon(uid):
    """
    Chatango specific feature
    
    A anonymous user can have:
    "!" before name meaning that the anonymous user has no name
    "#" before name meaning that the anonymous user has a name
    "*" before name meaning that the anonymous user sent a PM message to the bot

    @param uid: user's uid
    """
    if uid.startswith(('!', '#', '*')):
        return True
    else:
        return False


def html_entities(word):
    """
    Convert a word to html entities
    
    Replace every character with it's HTML version for ASCII code

    @param word: the word
    """
    return ''.join(['&#{0};'.format(ord(char)) for char in word])


def adjust_version(version):
    """
    Adjust version method
    Make sure that the last version indicator is made of two digits
    Increase the version indicators if one of the indicators exceeds its range

    @type version: str
    @param version: version string matching matching x.x.xx string where x is a digit

    @rtype: str
    @return: adjusted version string
    """
    version = [int(each) for each in version.split('.')]

    if len(version) > 3 and version[3] > 9:
        version[3] = 0
        version[2] += 1
    if len(version) > 2 and version[2] > 9:
        version[2] = 0
        version[1] += 1
    if version[1] > 9:
        version[1] = 0
        version[0] += 1

    if len(version) > 3 and not version[3]:
        del version[3]
        if not version[2]:
            del version[2]
    elif len(version) > 2 and not version[2]:
        del version[2]

    version = [str(each) for each in version]

    return '.'.join(version)


def get_version(file):
    """"
    Get bot version
    
    Use changelog.ini given file to search for the last version specified in a changeset
    If no version was found, return 1.0

    @param file: file stream
    """
    version = '1.0'
    for line in file:
        match_obj = re.match("- [A-Z]+ \(([0-9]+[.][0-9][.]?[0-9]?[.]?[0-9]?)\).*", line)
        if match_obj:
            version = match_obj.group(1)
            break
    return adjust_version(version)


def special_number(number_string, reference=None):
    """
    Get special number
    
    Cleaning a string by removing commas, spaces and dots
    Use "m" as final character to specify that this number represents millions
    Use "k" as final character to specify that this number represents thousands
    Use "all" to return the specified reference

    @type number_string: str
    @param number_string: a string that has to look like a number

    @type reference: int
    @param reference: specify this if you want to return its value when the number_string is "all"

    @rtype: int
    @return: integer number
    """
    try:
        number = number_string.lower().replace(',', '').replace(' ', '').replace('.', '')

        if isinstance(reference, int) and number_string == 'all':
            return reference
        else:
            if number.endswith('k'):
                number = number[:-1] + '000'
            elif number.endswith('m'):
                number = number[:-1] + '000000'

            return int(number)
    except ValueError:
        return None


def everything_between(string, before, after):
    """
    Get the substring between two substrings in a string

    @type string: str
    @param string: the string

    @type before: str
    @param before: the substring on the left

    @type after: str
    @param after: the substring on the right

    @rtype: str
    @return: the string in the middle
    """
    try:
        start = string.index(before) + len(before)
        end = string.index(after, start)
        return string[start:end]
    except ValueError:
        return ""


def get_bg_time(uid):
    """
    Get bg time of a user

    @type uid: str
    @param uid: user's uid

    @rtype: int
    @return: user's last bg expiration time or None if user never had bg
    """
    try:
        url = 'http://pst.chatango.com/profileimg/{0}/{1}/{2}/mod1.xml'.format(
            uid[0],
            uid[1] if 1 != len(uid) else uid[0],
            uid
        )
        response = request.urlopen(url)
    except:
        response = None

    return_value = None

    if response:
        try:
            data = response.read().decode()
        except:
            data = ''
        try:
            return_value = re.compile(r"<d>(.*?)</d>", re.IGNORECASE).search(data).group(1)
        except:
            return_value = None

    return int(return_value) if return_value else None


def percentage(part, whole):
    """
    Percentage method

    @type part: float
    @param part: x%

    @type whole: int
    @param whole: the number

    @rtype: float
    @return: percentage number
    """
    return (float(part) * float(whole)) / 100


def strip_html(msg):
    """Strip HTML."""
    li = msg.split("<")
    if len(li) == 1:
        return li[0]
    else:
        ret = list()
        for data in li:
            data = data.split(">", 1)
            if len(data) == 1:
                ret.append(data[0])
            elif len(data) == 2:
                ret.append(data[1])
        return "".join(ret)


def explode(string, separator=' ', limit=-1):
    """
    Split a string by a separator and strips all the elements returning a list of non-empty strings

    @type string: str
    @param string: any string

    @type separator: str
    @param separator: string to split the list by

    @type limit: int
    @param limit: maximum splits

    @rtype: list
    @return: the list generated from string's split
    """
    if not isinstance(string, str):
        raise TypeError
    else:
        my_list = [each.strip() for each in string.split(separator, limit)]
        ret = []

        for each in my_list:
            if each:
                ret.append(each)

        return ret


def get_unique_items(my_list):
    """
    Get the unique elements of a list in a list

    @type my_list: list
    @param my_list: list to remove duplicates from

    @rtype: list
    @return: the list without duplicates
    """
    if not isinstance(my_list, list):
        raise TypeError
    else:
        return list(set(my_list))


def generate_path(root_path='/', file_name='', dirs=list(), make_dirs=False, sep='/'):
    """
    Generate directory/file path

    If the returned value is a directory path, it will always have a leading separator
    If the returned value is a file path, there will be no leading separator for the path

    @type root_path: str
    @param root_path: path to start from

    @type file_name: str
    @param file_name: the file name to generate a path for

    @type dirs: list
    @param dirs: extra directories between the root path and the file name

    @type make_dirs: bool
    @param make_dirs: True to create the directories specified, False otherwise

    @type sep: str
    @param sep: separator to use between files/directories

    @rtype: str
    @return: the generated path
    """
    file_name = file_name.strip()

    path = '{root_path}{separator}'.format(
        root_path=root_path,
        separator=(sep if sep != root_path[-1:] else '') + ''
    )

    if dirs or file_name:
        if dirs:
            path += sep.join(dirs) + sep
        if make_dirs:
            try:
                os.makedirs(path)
            except:
                pass
        if file_name:
            path += file_name
    elif make_dirs:
        try:
            os.makedirs(path)
        except:
            pass

    return path