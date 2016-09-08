# Python imports
from collections import OrderedDict

# Project imports
from util.localization import format_number


def format_seconds_to_long_string(seconds, lang, lang_dict):
    """
    Format seconds to long string

    E.g.: if seconds = 300125, the function will return 3 days, 11 hours, 22 minutes and 5 seconds

    @type seconds: float/int
    @param seconds: seconds

    @type lang: str
    @param lang: language key

    @type lang_dict: dict
    @param lang_dict: dictionary containing language messages

    @rtype: str
    @return: the formatted string
    """
    if 0 == seconds:
        return format_number(
            0,
            lang_dict['SECONDS'][0][lang],
            lang_dict['SECOND'][0][lang],
            lang
        )
    else:
        ret = []

        mapping = OrderedDict()
        mapping['year'] = 3600 * 24 * 365
        mapping['month'] = 3600 * 24 * 30
        mapping['day'] = 3600 * 24
        mapping['hour'] = 3600
        mapping['minute'] = 60
        mapping['second'] = 1

        for each in mapping:
            float_value = seconds / mapping[each]
            value = int(float_value)
            if value > 0:
                if 'second' != each:
                    seconds -= mapping[each] * value
                else:
                    value = float_value or value
                ret.append(format_number(
                    value,
                    lang_dict['{0}s'.format(each).upper()][0][lang],
                    lang_dict['{0}'.format(each).upper()][0][lang],
                    lang
                ))
            elif 'second' == each and float_value > 0:
                ret.append(format_number(
                    float_value,
                    lang_dict['{0}s'.format(each).upper()][0][lang],
                    lang_dict['{0}'.format(each).upper()][0][lang],
                    lang
                ))

        if len(ret) > 1:
            result = ' {0} '.format(lang_dict['AND'][0][lang]).join([
                ', '.join(ret[:-1]),
                ret[-1]
            ])
        else:
            result = ret[0]

        return result


def format_seconds_to_short_string(seconds):
    """
    Format seconds to short string

    E.g.: if seconds = 300125, the function will return 3d 11h 22m 5s

    @type seconds: float/int
    @param seconds: seconds

    @rtype: str
    @return: the formatted string
    """
    seconds = round(seconds)
    ret = ''

    year = 3600 * 24 * 365
    month = 3600 * 24 * 30
    day = 3600 * 24
    hour = 3600
    minute = 60

    years = int(seconds / year)
    if years:
        seconds -= year * years
        ret += str(years) + 'y'

    months = int(seconds / month)
    if months:
        seconds -= month * months
        ret += (' ' if ret else '') + str(months) + 'm'

    days = int(seconds / day)
    if days:
        seconds -= day * days
        ret += (' ' if ret else '') + str(days) + 'd'

    hours = int(seconds / hour)
    if hours:
        seconds -= hour * hours
        ret += (' ' if ret else '') + str(hours) + 'h'

    minutes = int(seconds / minute)
    if minutes:
        seconds -= minute * minutes
        ret += (' ' if ret else '') + str(minutes) + 'm'

    if seconds:
        ret += (' ' if ret else '') + str(seconds) + 's'

    if not ret:
        ret = '0s'

    return ret