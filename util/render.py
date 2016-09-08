# Python imports
import random


def highlight(string, color_flag=None, flags=''):
    """
    Highlight message

    @type color_flag: str
    @param color_flag: keyword of a color or a HEX code

    @type flags: str
    @param flags: string that can contain any letters of 'u', 'b', 'i'
                  each one of these representing a HTML tag

    @rtype: str
    @return: formatted string
    """
    colors = {
        'Red':         'FF554D',
        'Orange':      'FFA500',
        'Yellow':      'FFFF33',
        'Green':       '7CEE7C',
        'WashedGreen': 'CCFFCC',
        'Blue':        '87CEEB',
        'Pink':        'FF6699',
        'Prune':       '9966FF',
        'WashedPrune': 'CCCCFF',
        'Gray':        '999999',
        'Skin':        'FFEFD5'
    }

    if color_flag in colors:
        color = colors[color_flag]
    else:
        color = color_flag

    if 'b' in flags.lower():
        string = '<b>{0}</b>'.format(string)
    if 'u' in flags.lower():
        string = '<u>{0}</u>'.format(string)
    if 'i' in flags.lower():
        string = '<i>{0}</i>'.format(string)

    if color:
        return '<font color="#{0}">{1}</font>'.format(
            color,
            string
        )
    else:
        return string


def currency(number):
    """
    Separate thousands

    @type number: int
    @param number: the number

    @rtype: str
    @return: The number formatted in the European format
    """
    return '{:,}'.format(number).replace(',', '.')
    

# TODO move at the command level
def slots_machine(cmd, chances):
    """
    Slots machine

    @type cmd: CommandManager
    @param cmd: Command instance

    @type chances: int
    @param chances

    @rtype: dict
    @return: dict containing the integer result and the fruits
    """
    def fruit(lang_key):
        return cmd.bot.lang(lang_key, cmd.lang)

    fruits = [
        {'fruit': fruit('LEMON'), 'color': 'Green'},
        {'fruit': fruit('PEAR'), 'color': 'Yellow'},
        {'fruit': fruit('APPLE'), 'color': 'Green'},
        {'fruit': fruit('ORANGE'), 'color': 'Orange'},
        {'fruit': fruit('CHERRY'), 'color': 'Red'},
        {'fruit': fruit('PRUNE'), 'color': 'Prune'},
        {'fruit': fruit('STRAWBERRY'), 'color': 'Red'},
        {'fruit': fruit('GRAPE'), 'color': 'Green'},
        {'fruit': fruit('BANANA'), 'color': 'Yellow'},
    ]

    if chances < 1:
        chances = 1

    fruit1_number = random.randint(0, chances)
    fruit2_number = random.randint(0, chances)
    fruit3_number = random.randint(0, chances)

    fruit1 = fruit2 = fruit3 = fruits[random.randint(0, len(fruits)-1)]

    result = 0
    
    if fruit1_number == fruit2_number == fruit3_number:
        result = 2
    elif fruit1_number == fruit2_number:
        result = 1
        while fruit3 in [fruit1, fruit2]:
            fruit3 = fruits[random.randint(
                0, len(fruits)-1
            )]
    elif fruit2_number == fruit3_number:
        result = 1
        while fruit1 in [fruit2, fruit3]:
            fruit1 = fruits[random.randint(
                0, len(fruits)-1
            )]
    elif fruit1_number == fruit3_number:
        result = 1
        while fruit2 in [fruit1, fruit3]:
            fruit2 = fruits[random.randint(
                0, len(fruits)-1
            )]
    elif fruit1_number != fruit2_number and fruit1_number != fruit3_number and fruit2_number != fruit3_number:
        result = 0
        while fruit2 in [fruit1]:
            fruit2 = fruits[random.randint(
                0, len(fruits)-1
            )]
        while fruit3 in [fruit1, fruit2]:
            fruit3 = fruits[random.randint(
                0, len(fruits)-1
            )]
    
    return {
        'fruits': [fruit1, fruit2, fruit3],
        'result': result
    }