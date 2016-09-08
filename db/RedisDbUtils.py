# Python imports
import time

# Project imports
from util.util import explode
from model.DbUtils import DbUtils


class RedisDbUtils(DbUtils):
    def swap_entries(self, entry1_id, entry2_id):
        entry1_data = self._db.connection.hgetall(entry1_id)
        entry2_data = self._db.connection.hgetall(entry2_id)

        self._db.connection.hmset(entry1_id, entry2_data)
        self._db.connection.hmset(entry2_id, entry1_data)

    def get_info(self, key, store=None):
        sep = '.'
        keys = explode(key, sep)

        if not store:
            store = self._db.store['info']

        current_value = store[keys[0]]

        if len(keys) > 1:
            return self.get_info(sep.join(keys[1:]), current_value)
        else:
            return current_value

    def get_configs(self):
        try:
            return self._db.store['configs']
        except:
            configs = self._db.connection.hgetall('configs')
            if {} == configs:
                configs = None
            
            return configs

    def get_config(self, key, store=None):
        sep = '.'
        keys = explode(key, sep)

        if not store:
            store = self._db.store['configs']

        current_value = store[keys[0]]

        if len(keys) > 1:
            return self.get_config(sep.join(keys[1:]), current_value)
        else:
            return current_value

    def set_config(self, key, value, operation=None, persistent=True):
        if 'add' == operation:
            value += self.get_config(key)
        elif 'substract' == operation:
            value = self.get_config(key) - value
        
        self._db.store['configs'][key] = value

        if persistent:
            self._db.connection.hset('configs', key, value)
    
    def get_users(self):
        users = self._db.connection.keys('users:*')

        return [user[6:] for user in sorted(users)]
        
    def get_users_count(self):
        try:
            return len(self._db.connection.keys('users:*'))
        except:
            return 0
        
    def get_user_data(self, uid, field=None):
        uid = uid.strip().lower()

        if field:
            result = self._db.connection.hget('users:' + uid, field)
            
            # Numbers
            if field in [
                'last_level_update_at',

                'bank',
                'bank_earnings',

                'coins',
                'coins_spent'

                'admin',
                'ignored',
                'level',
                'parked',
                'parked_until',

                'register_time'
            ]:
                result = int(result or 0)
            # Strings
            elif field in ['uid', 'nick', 'registered_on']:
                if 'uid' == field:
                    result = uid
                else:
                    result = result if (result and result.strip()) else None
            elif field == 'lang':
                result = result if (result and result.strip())\
                    else self._db.get_config('default_language')
            # Lists
            elif field in ['restricted_commands', 'restricted_games']:
                result = set(result.split(',')) if (result and len(result)) else set()
            
            return result
        else:
            user_data = self._db.connection.hgetall('users:' + uid)
            
            result = {
                'uid': uid,
                'last_level_update_at': int(user_data.get('last_level_update_at') or 0),

                'lang': user_data.get('lang') or self._db.get_config('default_language'),
                'nick': (user_data.get('nick') or '').strip(),

                'register_time': int(user_data.get('register_time') or 0),
                'registered_on': user_data.get('registered_on') or '',

                'bank': int(user_data.get('bank') or 0),
                'bank_earnings': int(user_data.get('bank_earnings') or 0),
                'coins': int(user_data.get('coins') or 0),
                'coins_spent': int(user_data.get('coins_spent') or 0),

                'admin': int(user_data.get('admin') or 0),
                'ignored': int(user_data.get('ignored') or 0),
                'level': int(user_data.get('level') or 0),
                'parked': int(user_data.get('parked') or 0),
                'parked_until': int(user_data.get('parked_until') or 0),

                'restricted_commands': set(user_data['restricted_commands'].split(','))
                if (
                    'restricted_commands' in user_data
                    and 0 != len(user_data['restricted_commands'])
                ) else set(),
                'restricted_games': set(user_data['restricted_games'].split(','))
                if (
                    'restricted_games' in user_data
                    and 0 != len(user_data['restricted_games'])
                ) else set()
            }

            return result
    
    def add_user(self, uid, data):
        user_data = {
            'last_level_update_at': data.get('last_level_update_at') or int(time.time()),

            'lang': data.get('lang') or self._db.get_config('default_language'),
            'nick': data.get('nick') or '',

            'bank': data.get('bank') or 0,
            'bank_earnings': data.get('bank_earnings') or 0,
            'coins': data.get('coins') or 0,
            'coins_spent': data.get('coins_spent') or 0,

            'admin': data.get('admin') or 0,
            'ignored': data.get('ignored') or 0,
            'level': data.get('level') or 1,
            'parked': data.get('parked') or 0,
            'parked_until': data.get('parked_until') or 0,

            'restricted_commands': ','.join(list(data.get('restricted_commands') or set())),
            'restricted_games': ','.join(list(data.get('restricted_games') or set())),

            'register_time': int(time.time()),
            'registered_on': data.get('registered_on') or ''
        }
        
        self._db.connection.hmset('users:' + uid, user_data)
        
    def update_user(self, uid, data):
        # Restrictions are being passed as sets
        if 'restricted_commands' in data:
            data['restricted_commands'] = ','.join(list(data['restricted_commands']))
        if 'restricted_games' in data:
            data['restricted_games'] = ','.join(list(data['restricted_games']))

        # This field is passed as NoneType
        if 'nick' in data:
            data['nick'] = data['nick'] or ''

        # Automatically set the <last level update at> field when level is specified
        if 'level' in data:
            data['last_level_update_at'] = int(time.time())

        self._db.connection.hmset('users:' + uid, data)

    def remove_user(self, uid):
        self._db.connection.delete('users:' + uid)

    def merge_users(self, uid1, uid2, uid):
        user1_data = self.get_user_data(uid1)
        user2_data = self.get_user_data(uid2)

        # Create user data
        user_data = {
            'bank': user1_data['bank'] + user2_data['bank'],
            'bank_earnings': user1_data['bank_earnings'] + user2_data['bank_earnings'],
            'coins': user1_data['coins'] + user2_data['coins'],
            'coins_spent': user1_data['coins_spent'] + user2_data['coins_spent'],

            'admin': max(user1_data['admin'], user2_data['admin']),
            'level': max(user1_data['level'], user2_data['level']),
            'parked': max(user1_data['parked'], user2_data['parked']),
            'parked_until': max(user1_data['parked_until'], user2_data['parked_until']),

            'restricted_commands': user1_data['restricted_commands'] | user2_data['restricted_commands'],
            'restricted_games': user1_data['restricted_games'] | user2_data['restricted_games'],

            'lang': user1_data['lang']
            if user1_data['lang'] != self._db.get_config('default_language')
            else user2_data['lang']
        }

        # Get the ignored flag from the user with the higher level
        if user1_data['level'] > user2_data['level']:
            user_data['ignored'] = user1_data['ignored']
        else:
            user_data['ignored'] = user2_data['ignored']

        if uid == uid1:
            user_data['nick'] = user1_data['nick'] or user2_data['nick']

            user_data['last_level_update_at'] = user1_data['last_level_update_at']

            user_data['register_time'] = user1_data['register_time'] or user2_data['register_time']
            user_data['registered_on'] = user1_data['registered_on'] or user2_data['registered_on']
        else:
            user_data['nick'] = user2_data['nick'] or user1_data['nick']

            user_data['last_level_update_at'] = user2_data['last_level_update_at']

            user_data['register_time'] = user2_data['register_time'] or user1_data['register_time']
            user_data['registered_on'] = user2_data['registered_on'] or user1_data['registered_on']

        override_uid = uid1 if uid1 != uid else uid2

        # Execute database modifications on user table
        self.remove_user(override_uid)
        self.update_user(uid, user_data)

        # Execute database modifications on definitions table
        definitions = self.get_definitions()

        for definition in definitions:
            definition_data = self.get_definition_data(definition)
            if definition_data['initiator'] == override_uid:
                self.update_definition(definition, {
                    'initiator': uid
                })

        # Execute database modifications on rooms table
        rooms = self.get_rooms()

        for room in rooms:
            room_data = self.get_room_data(room)
            if room_data['initiator'] == override_uid:
                self.update_room(room, {
                    'initiator': uid
                })

    def get_rooms(self, blacklisted=None):
        returned_rooms = []
        
        rooms = self._db.connection.keys('rooms:*')
        
        if len(rooms):
            for room in sorted(rooms):
                if blacklisted is None:
                    returned_rooms.append(room[6:])
                elif blacklisted:
                    if int(self._db.connection.hget(room, 'blacklisted')) == 1:
                        returned_rooms.append(room[6:])
                else:
                    if int(self._db.connection.hget(room, 'blacklisted')) == 0:
                        returned_rooms.append(room[6:])
                    
        return returned_rooms
        
    def get_rooms_count(self):
        try:
            return len(self._db.connection.keys('rooms:*'))
        except:
            return 0
        
    def get_room_data(self, room_name):
        room_name = room_name.lower()
        
        room_data = self._db.connection.hgetall('rooms:' + room_name)
        
        if room_data == {}:
            return None
        else:
            return {
                'name': room_name,
                'initiator': room_data['initiator'],
                'blacklisted': int(room_data.get('blacklisted') or 0),
                'sleep': int(room_data.get('sleep') or 0),
                'lang': room_data.get('lang') or self._db.get_config('default_language'),
                'game': room_data.get('game') or None,
                'default': int(room_data.get('default') or 0),
                'delay': float(room_data.get('delay') or self._db.get_config('room.default_delay'))
            }
        
    def add_room(self, room_name, data):
        room_data = {
            'initiator': data.get('initiator'),
            'blacklisted': data.get('blacklisted') or 0,
            'sleep': data.get('sleep') or 0,
            'lang': data.get('lang') or self._db.get_config('default_language'),
            'game': data.get('game') or '',
            'default': data.get('default') or 0,
            'delay': data.get('delay') or self._db.get_config('room.default_delay')
        }
        
        self._db.connection.hmset('rooms:' + room_name, room_data)
        
    def update_room(self, room_name, data):
        if 'game' in data:
            data['game'] = data['game'] or ''

        self._db.connection.hmset('rooms:' + room_name, data)
    
    def remove_room(self, room_name):
        self._db.connection.delete('rooms:' + room_name)

    def get_definitions(self):
        definitions = self._db.connection.keys('definitions:*')

        return [definition[12:] for definition in definitions]

    def get_definitions_count(self):
        try:
            return len(self._db.connection.keys('definitions:*'))
        except:
            return 0
        
    def get_definition_data(self, keyword):
        raw_data = self._db.connection.hgetall('definitions:' + keyword.lower())

        definition_data = {
            'keyword': keyword,
            'definition': raw_data.get('definition'),
            'initiator': raw_data.get('initiator')
        }

        return definition_data
        
    def update_definition(self, keyword, data):
        self._db.connection.hmset('definitions:' + keyword.lower(), data)
        
    def remove_definition(self, keyword):
        self._db.connection.delete('definitions:' + keyword.lower())

    def set_whois(self, shared_uid, data):
        self._db.connection.hmset('whois:' + shared_uid, {
            'uids': ','.join(data['uids']),
            'last_update': data['last_update']
        })

    def remove_whois(self, shared_uid):
        self._db.connection.delete('whois:' + shared_uid.lower())

    def get_whois_entries(self):
        whois_entries = self._db.connection.keys('whois:*')

        result = dict()

        for shared_uid in whois_entries:
            key = shared_uid[6:]
            data = self._db.connection.hgetall(shared_uid)

            result[key] = dict()
            result[key]['uids'] = data['uids'].split(',')
            result[key]['last_update'] = int(data['last_update'])

        return result

    def set_listen(self, string, uids):
        self._db.connection.set('listen:' + string.lower(), ','.join(uids))

    def remove_listen(self, string):
        self._db.connection.delete('listen:' + string.lower())

    def get_listen_entries(self):
        listen_entries = self._db.connection.keys('listen:*')

        result = dict()

        for entry in listen_entries:
            result[entry[7:]] = self._db.connection.get(entry).split(',')

        return result

    def get_seen(self, uid):
        seen_data = self._db.connection.hgetall('seen:' + uid.lower())
        if {} == seen_data:
            return None
        else:
            return seen_data

    def set_seen(self, uid, data):
        table_name = 'seen'

        self._db.connection.hmset('{table_name}:{uid}'.format(
            table_name=table_name,
            uid=uid.lower()
        ), data)

    def get_seen_entries(self, return_data=False):
        table_name = 'seen'
        start_from = len(table_name) + 1

        seen_users = self._db.connection.keys('{table_name}:*'.format(
            table_name=table_name
        ))

        if return_data:
            seen_entries = dict()

            for each in seen_users:
                uid = each[start_from:]
                seen_entries[uid] = self.get_seen(uid)
        else:
            return [each[start_from:] for each in seen_users]

    def get_auto_delete_entries(self):
        auto_delete_entries = self._db.connection.keys('autodelete:*')

        return [auto_delete[11:] for auto_delete in auto_delete_entries]

    def add_auto_delete(self, uid, data):
        self._db.store['auto_delete'].append(uid.lower())
        self._db.connection.hmset('autodelete:' + uid.lower(), data)

    def remove_auto_delete(self, uid):
        self._db.store['auto_delete'].remove(uid.lower())
        self._db.connection.delete('autodelete:' + uid.lower())