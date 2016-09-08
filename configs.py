# Python imports
from collections import OrderedDict
import configparser
import sys
import os
import time

# Project imports
from db.RedisDb import RedisDb
from manager.Help import Help
from manager.Lang import Lang
from util.util import get_version
from util import temp

log_level = 0
store = dict()
root_path = os.path.dirname(__file__)

print('\n' + '-' * 50 + '\n')

try:
    begin = time.time()
    start = time.time()
    print('Loading configurations...')
    
    config = configparser.ConfigParser()
    config.read('bot.ini')

    log_level = config['development'].getint('log_level')

    db_params = {
        'host': config['database']['host'],
        'database': config['database'].getint('database'),
        'decode_responses': config['database'].getboolean('decode_responses'),
        'password': config['database']['password']
    }

    print('Loaded configurations ({execution_time:.2f}s)'.format(
        execution_time=round(time.time()-start, 2)
    ))
except:
    print('Error: Configurations cannot be read')
    if log_level > 0:
        raise
    sys.exit()

try:
    start = time.time()
    print('Connecting to the database...')
    
    db = RedisDb(db_params)
    db.connection.ping()
    
    print('Connected to the database ({execution_time:.2f}s)'.format(
        execution_time=round(time.time() - start, 2)
    ))
except:
    print('Error: Could not connect to the database')
    if log_level > 0:
        raise
    sys.exit()

try:
    start = time.time()
    print('Loading configurations...')
    configs = db.get_configs()
    print('Loaded configurations (took {execution_time:.2f}s)'.format(
        execution_time=round(time.time() - start, 2)
    ))
except:
    print('Error: Invalid database structure')
    if log_level > 0:
        raise
    sys.exit()

try:
    start = time.time()
    print('Loading help system...')
    help_mgr = Help(config['paths']['help'])
    print('Help system loaded ({execution_time:.2f}s)'.format(
        execution_time=round(time.time() - start, 2)
    ))
except:
    print('Error: Could not load the help system')
    if log_level > 0:
        raise
    sys.exit()

try:
    start = time.time()
    print('Loading language system...')
    lang_mgr = Lang(root_path)
    print('Language system loaded ({execution_time:.2f}s)'.format(
        execution_time=round(time.time() - start, 2)
    ))
except:
    print('Error: Could not load language system')
    if log_level > 0:
        raise
    sys.exit()

try:
    store = {
        'configs': {
            # General configs
            'default_language': configs['bot_default_lang'],
            # Bot configs
            'bot': {
                'name':       configs['bot_name'],
                'password':   configs['bot_password'],
                'name_color': configs['bot_name_color'],
                'font_color': configs['bot_font_color'],
                'font_face':  configs['bot_font_face'],
                'font_size':  int(configs['bot_font_size'])
            },
            # Command configs
            'command': {
                'prefixes':         list(configs['bot_command_prefixes']),
                'vote_game_needed': int(configs['vote_game_needed']),
                'max_execution_time': config['commands'].getfloat('max_execution_time')
            },
            # PM configs
            'pm': {
                'enable': True,
            },
            # Room configs
            'room': {
                'default_delay':             1,
                'delay_when_flood_warned':   5,
                'flood_warned_grace_period': 100
            },
            # Message configs
            'message': {
                'indentation':     ' ' * 14,
                'big_indentation': ' ' * 22,
                'line_breaker':    '<br>'
            },
            # Cron configs
            'cron_1h':  int(configs['cron_1h']),
            'cron_2h':  int(configs['cron_2h']),
            'cron_3h':  int(configs['cron_3h']),
            'cron_6h':  int(configs['cron_6h']),
            'cron_12h': int(configs['cron_12h']),
            'cron_24h': int(configs['cron_24h']),
            # Ini configs
            'log_directory':      config['paths']['log_directory'],
            'root_path':          root_path,
            'log_level':          log_level
        },
        'info': {
            'boot_time': begin,
            'version':   '{version}-{state}'.format(version=get_version(open('changelog.ini', 'r')),
                                                    state=config['versioning']['version']),
            'website': configs['bot_website']
        },
        'languages': {
            'en': 'English',
            'ro': 'Română'
        },
        'games': {
            'trivia':     'Trivia',

            'fazan':      'Pheasant',
            'pheasant':   'Pheasant',

            'scramble':   'Scramble',

            'math':       'Math',
            'matematica': 'Math',
            'matematică': 'Math',
            'mate':       'Math'
        },
        'modes': {
            'gray':         ' }| ',
            'fish':         ' &gt;&lt;&gt; ',
            'butterfly':    ' 8|8 ',
            'snow':         ' *snow* '
        },
        'aliases': help_mgr.aliases,
        'help': help_mgr.commands,
        'lang': lang_mgr.lang,
        'whois':          db.get_whois_entries(),
        'listen':         db.get_listen_entries(),
        'auto_delete':    db.get_auto_delete_entries(),

        'bet_list':       temp.load('bet_list', root_path, dict()),
        'shapeshiftings': temp.load('shapeshiftings', root_path, dict()),
        'redirects':      temp.load('redirects', root_path, dict()),
        'speak':          temp.load('speak', root_path, set()),
        'vote_game':      temp.load('vote_game', root_path, dict()),
        'cannons':        temp.load('cannons', root_path, dict()),
        'lotteries':      temp.load('lotteries', root_path, {
            'level': {
                'users': OrderedDict(),
                'running': False,  # lottery session is running
                'duration': 3600,  # 1 hour
                'needed_users': 10,  # number of users needed to end the lottery session
                'ticket_price': 10,  # ticket price that will be multiplied by user's level
                'last_ticket': 0,  # time of the last ticket bought
                'message_count': 0,  # count the keep alive messages
                'session_end': 0,  # session end
                'last_message': 0,  # time of the last keep alive message
                'message_interval': 600,  # 10 minutes
                'max_tickets_per_user': 3  # maximum number of tickets that can be bought by an user
            },
            'coins': {
                'users': OrderedDict(),
                'running': False,  # lottery session is running
                'duration': 600,  # 10 minutes
                'needed_users': 5,  # number of users needed to end the lottery session
                'ticket_price': 0,  # the ticket price for the current session (is set dynamically)
                'last_ticket': 0,  # time of the last ticket bought
                'message_count': 0,  # count the keep alive messages
                'session_end': 0,  # session end
                'last_message': 0,  # time of the last keep alive message
                'message_interval': 150,  # 2.5 minutes
                'max_tickets_per_user': 2  # maximum number of tickets that can be bought by an user
            }
        })
    }

    db.store = store
    
    print('\nAll extensions were loaded, ready to start {bot_name} ({execution_time:.2f}s)'.format(
        bot_name=configs['bot_name'],
        execution_time=round(time.time() - begin, 2)
    ))
except:
    print('Error: Invalid database structure')
    if log_level > 0:
        raise
    sys.exit()