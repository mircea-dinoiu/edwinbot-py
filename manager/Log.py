# Python imports
import time
import os
import sys

# Third party imports
from unidecode import unidecode


class Log(object):
    def __init__(self, path='', directory='mylogs', on_terminal=True):
        self.on_terminal = on_terminal
        self.terminal = sys.stdout
        
        self.path = path + ('/' if '/' != path[-1:] else '')
        self.directory = directory
        self.date = tuple()

    def write(self, message, before='', after='', show_time=None, show_date=None, brackets=None):
        # Getting the current time
        now = time.localtime()

        year = time.strftime('%Y', now)
        month = time.strftime('%m', now)
        day = time.strftime('%d', now)

        # On empty message is preferred not to print out the time
        if message.strip(' \t\n\r'):
            if show_time is None:
                show_time = True
            if brackets is None:
                brackets = True
        else:
            if show_time is None:
                show_time = False
            if brackets is None:
                brackets = False

        date_time = ''

        # Choose between date/time/date&time
        if show_time and show_date:
            date_time = time.strftime('%Y-%m-%d %H:%M:%S', now)
        elif show_time:
            date_time = time.strftime('%H:%M:%S', now)
        elif show_date:
            date_time = time.strftime('%Y-%m-%d', now)

        # Is the date/time written with brackets?
        if brackets:
            date_time = '[' + date_time + ']'

        # Add the date/time to the message
        if date_time:
            message = '{date_time} {message}'.format(
                date_time=date_time,
                message=message
            )

        # Add after and before strings
        message = before + message + after

        # If is terminal
        if self.on_terminal:
            date = (year, month, day)
            if self.date != date:
                self.date = date
                self.write(time.strftime('%Y-%m-%d', now), before='\n', after='\n\n')
            self.terminal.write(unidecode(message))

        # Set the directory that the files will be saved in
        directory = self.path + self.directory + '/{0}/{1}'.format(year, month)

        # Create directories if they are not already existing
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the message to the file
        with open('{0}/{1}.txt'.format(directory, day), 'a+', encoding='utf-8') as log_file:
            log_file.write(message)
            
    def flush(self):
        pass