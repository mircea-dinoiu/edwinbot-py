# Project imports
from util.util import get_unique_items
from engine.chatango.common.Stream import Stream
from engine.chatango.stream.Room.Handlers import Handlers


class Room(Stream, Handlers):
    # User list
    def get_user_list(self, mode=None, unique=None, memory=None):
        ul = None
        if mode is None:
            mode = 'registered'

        if unique is None:
            unique = self._user_list_unique

        if memory is None:
            memory = self._user_list_memory

        if mode == 'recent':
            ul = [each.user for each in self._history[-memory:]]
        elif mode == 'registered':
            ul = self._user_list
        elif mode == 'active':
            recent = [each.user for each in self._history[-memory:]]
            online = self._user_list
            ul = list(set(recent) & set(online))
        elif mode == 'all':
            recent = [each.user for each in self._history[-memory:]]
            online = self._user_list
            ul = get_unique_items(recent + online)

        if unique and mode != 'active':
            return get_unique_items(ul)
        else:
            return ul

    # User uids
    def get_user_uids(self):
        return [user.uid for user in self._user_list]

    # User names
    def get_user_names(self):
        return [user.name for user in self._user_list]

    # Recent list
    def get_recent_list(self):
        return self._recent_list

    # User
    def get_user(self):
        return self._manager.user

    # Owner
    def get_owner(self):
        return self._owner

    # Owner name
    def get_owner_name(self):
        return self._owner.name

    # Moderators
    def get_mods(self):
        return self._mods

    # Moderator uids
    def get_mod_uids(self):
        return [user.uid for user in self._mods]

    # Moderator names
    def get_mod_names(self):
        return [user.name for user in self._mods]

    # User count
    def get_user_count(self):
        return self._user_count

    # Ban list
    def get_ban_list(self):
        return [record[2] for record in self._ban_list]

    def get_unban_list(self):
        return [record[2] for record in self._unban_list]

    # Banned words
    def get_banned_words(self):
        return self._banned_words

    # History
    def get_history(self):
        return self._history

    # Messages
    def get_messages(self):
        return self._msgs

    # Flood
    def get_flood(self):
        return self._flood

    def set_flood(self, flood):
        self._flood = flood

    # Sleep
    def get_sleep(self):
        return self._sleep

    def set_sleep(self, sleep):
        self._sleep = sleep

    # Language
    def get_lang(self):
        return self._lang

    def set_lang(self, lang):
        self._lang = lang

    # Game
    def get_game(self):
        return self._game

    def set_game(self, game):
        self._game = game

    # Games
    def get_games(self):
        return self._games

    def set_games(self, games):
        self._games = games

    # Mode
    def get_mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = mode

    # Lock
    def get_lock(self):
        return self._lock

    def set_lock(self, lock):
        self._lock = lock

    # Default
    def get_default(self):
        return self._default

    def set_default(self, default):
        self._default = default

    # Login fail
    def get_login_fail(self):
        return self._login_fail

    def set_login_fail(self, login_fail):
        self._login_fail = login_fail

    # Delay
    def get_delay(self):
        return self._delay

    def set_delay(self, delay):
        self._delay = delay

    # Wait until
    def set_wait_until(self, wait_until):
        self._wait_until = wait_until + ((self._rate_limit + 1) if self._rate_limit else self._delay)

    user_list = property(get_user_list)
    usernames = property(get_user_names)
    user = property(get_user)
    owner = property(get_owner)
    owner_name = property(get_owner_name)
    mods = property(get_mods)
    mod_names = property(get_mod_names)
    user_count = property(get_user_count)
    ban_list = property(get_ban_list)
    unban_list = property(get_unban_list)
    banned_words = property(get_banned_words)
    recent_list = property(get_recent_list)
    messages = property(get_messages)
    delay = property(get_delay, set_delay)

    sleep = property(get_sleep, set_sleep)
    flood = property(get_flood, set_flood)
    lang = property(get_lang, set_lang)
    game = property(get_game, set_game)
    games = property(get_games, set_games)
    mode = property(get_mode, set_mode)
    lock = property(get_lock, set_lock)
    default = property(get_default, set_default)
    login_fail = property(get_login_fail, set_login_fail)