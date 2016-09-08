# Python imports
import time
import re

# Project imports
from util.util import get_version, adjust_version

FILE_PATH = 'changelog.ini'


def show_menu():
    print('\n' + '-' * 50 + '\n')
    menu = [
        '[1] BUG FIX',
        '[2] ENHANCEMENT',
        '[3] BIG ENHANCEMENT',
        '[4] CHANGE REQUEST',
        '[5] BIG CHANGE REQUEST',
        '[0] exit'
    ]

    print('\n'.join(menu))
    print('\n')


def listen():
    show_menu()

    # Prepare the lines list
    lines = list()

    # Open the changelog file
    file_in = open(FILE_PATH, 'r')
    # Get current version
    version = get_version(file_in)

    print('Current version: {version}'.format(
        version=version
    ))

    try:
        get = input('Change type: ')
        c_type = int(get)
        assert(c_type in range(0, 6))

        # Exit?
        if c_type == 0:
            return

        get = input('Change description: ')
        c_desc = get.strip(' \t\n\r')

        if c_desc:
            file_in.seek(0)
            # Put all lines in a list
            for line in file_in:
                new_line = line.strip(' \t\n\r')
                if new_line:
                    lines.append(new_line)
            file_in.close()

            # Get the current day
            now = time.localtime()
            today = time.strftime('[%d.%m.%Y]', now)

            # Add the current day to the log files if not already inserted
            for line in lines:
                match_obj = re.match("(\[[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9]\])", line)
                if match_obj:
                    if match_obj.group(1) != today:
                        lines.insert(0, today)
                    break

            # Set the new version
            version = [int(each) for each in version.split('.')]

            if len(version) < 3:
                version.append(0)
            if len(version) < 4:
                version.append(0)

            if c_type == 1:
                version[3] += 1
                c_type = 'BUG'

            elif c_type == 2:
                version[2] += 1
                version[3] = 0
                c_type = 'ENH'

            elif c_type == 3:
                version[1] += 1
                version[2] = 0
                version[3] = 0
                c_type = 'ENH'

            elif c_type == 4:
                version[3] += 1
                c_type = 'CHR'

            elif c_type == 5:
                c_type = 'CHR'
                version[2] += 1
                version[3] = 0

            version = adjust_version('.'.join([str(int(each)) for each in version]))

            print('New version: {version}'.format(
                version=version
            ))

            # Confirm
            confirm = input('Is there any error? y/n ')
            if confirm.lower() != 'y':
                # Create the log line
                log = '- {type} ({version}): {description}'.format(
                    type=c_type,
                    version=version,
                    description=c_desc
                )

                # Insert the new log into the changelog
                lines.insert(1, log)

                # Output the data to the file
                file_out = open(FILE_PATH, 'w')
                file_out.write('\n'.join(lines))
                file_out.close()
        else:
            print('Change description too short')
            file_in.close()
    except AssertionError:
        print('Invalid change type specified')
    except ValueError:
        print('Invalid change type specified')
    except EOFError:
        pass

    listen()

listen()