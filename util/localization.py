def format_number(number, many_text, one_text, lang='en', apply_functions=list()):
    """
    Format number by locale

    @type number: int/float
    @param number: the number to format

    @type many_text: str
    @param many_text: text to use when number is not 1

    @type one_text: str
    @param one_text: text to use when number equals 1

    @type lang: str
    @param lang: language to use for formatting

    @type apply_functions: list
    @param apply_functions: list of functions to apply on the number (not on the text)

    @rtype: str
    @return: formatted number
    """
    if isinstance(number, float) and int(number) == number:
        number = int(number)

    raw_number = number

    for function in apply_functions:
        number = function(number)

    if 'ro' == lang:
        if 1 == abs(raw_number):
            return_value = str(number) + ' ' + one_text
        else:
            if isinstance(raw_number, float):
                fractional_part = int(str(raw_number).split('.')[1])
                raw_number = fractional_part

            if (
                0 == raw_number
                or abs(raw_number) % 100 in range(1, 20)
            ):
                return_value = str(number) + ' ' + many_text
            else:
                return_value = str(number) + ' de ' + many_text
    else:
        if 1 == abs(raw_number):
            return_value = str(number) + ' ' + one_text
        else:
            return_value = str(number) + ' ' + many_text

    return return_value