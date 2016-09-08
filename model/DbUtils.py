# Python imports
import abc


class DbUtils:
    def __init__(self, database):
        self._db = database

    @abc.abstractclassmethod
    def swap_entries(self, entry1_id, entry2_id):
        """
        Swaps two entries in database

        @type entry1_id: str
        @param entry1_id: first entry id

        @type entry2_id: str
        @param entry2_id: second entry id
        """
        pass

    @abc.abstractmethod
    def get_info(self, key, store=None):
        """
        Get info by key

        @type key: str
        @param key: info's key

        @type store: dict
        @param store: store to get the info from

        @rtype: object
        @return: the requested info
        """
        pass

    @abc.abstractclassmethod
    def get_configs(self):
        """Get all configs"""
        pass

    @abc.abstractclassmethod
    def get_config(self, key, store=None):
        """
        Get config by key

        @type key: str
        @param key: config's key

        @type store: dict
        @param store: store to get the config from

        @rtype: object
        @return: the config
        """
        pass

    @abc.abstractclassmethod
    def set_config(self, key, value, operation=None, persistent=True):
        """
        Set config value

        @param key: config's key
        @param value: the value to be set for the config
        @param operation: mathematical operations

        @type persistent: bool
        @param persistent: True if the config should be saved to the database, False otherwise
        """
        pass

    @abc.abstractclassmethod
    def get_users(self):
        """Get all users"""
        pass

    @abc.abstractclassmethod
    def get_users_count(self):
        """Get users count"""
        pass

    @abc.abstractclassmethod
    def get_user_data(self, uid, field=None):
        """
        Get level of an user

        @param uid: user's id
        @param field: get just one field
        """
        pass

    @abc.abstractclassmethod
    def add_user(self, uid, data):
        """
        Add user with data

        @param uid: user's id
        @param data: dict containing user data
        """
        pass

    @abc.abstractclassmethod
    def update_user(self, uid, data):
        """
        Update user data

        @param uid: user's uid
        @param data: dict containing user data
        """
        pass

    @abc.abstractclassmethod
    def remove_user(self, uid):
        """
        Remove user from database

        @param uid: user's uid
        """
        pass

    @abc.abstractclassmethod
    def merge_users(self, uid1, uid2, uid):
        """
        Merge two users into one user
        uid has to be one of uid1 or uid2

        @type uid: str
        @param uid: merged user

        @type uid1: str
        @param uid1: first user

        @type uid2: str
        @param uid2: second user
        """
        pass

    @abc.abstractclassmethod
    def get_rooms(self, blacklisted=None):
        """
        Get rooms

        @param blacklisted: None for all rooms
                            True for only blacklisted rooms
                            False for only whitelisted rooms
        """
        pass

    @abc.abstractclassmethod
    def get_rooms_count(self):
        """Get rooms count"""
        pass

    @abc.abstractclassmethod
    def get_room_data(self, room_name):
        """
        Get room data

        @param room_name: room's name
        """
        pass

    @abc.abstractclassmethod
    def add_room(self, room_name, data):
        """
        Add room with data

        @param room_name: room's name
        @param data: dict containing room data
        """
        pass

    @abc.abstractclassmethod
    def update_room(self, room_name, data):
        """
        Update room data

        @param room_name: room's name
        @param data: dict containing room data
        """
        pass

    @abc.abstractclassmethod
    def remove_room(self, room_name):
        """
        Remove room

        @param room_name: room's name
        """
        pass

    @abc.abstractclassmethod
    def get_definitions(self):
        """Get all definitions"""
        pass

    @abc.abstractclassmethod
    def get_definitions_count(self):
        """Get definitions count"""
        pass

    @abc.abstractclassmethod
    def get_definition_data(self, keyword):
        """
        Get definition

        @param keyword: definition's key
        """
        pass

    @abc.abstractclassmethod
    def update_definition(self, keyword, data):
        """
        Update definition data

        @param keyword: definition's key
        @param data: dict of definition data
        """
        pass

    @abc.abstractclassmethod
    def remove_definition(self, keyword):
        """
        Remove definition

        @param keyword: definition's key
        """
        pass

    @abc.abstractclassmethod
    def set_whois(self, shared_uid, user_uids):
        """
        Set whois entry

        @type shared_uid: int
        @param shared_uid: shared uid

        @type user_uids: list
        @param user_uids: user uids
        """
        pass

    @abc.abstractmethod
    def remove_whois(self, shared_uid):
        """
        Remove whois entry

        @type shared_uid: str
        @param shared_uid: key to delete by
        """
        pass

    @abc.abstractclassmethod
    def get_whois_entries(self):
        """
        Get all whois entries as a dictionary

        @rtype: dict
        @return: dictionary of whois entries
        """
        pass

    @abc.abstractclassmethod
    def set_listen(self, string, uids):
        """
        Set listen entry

        @type string: str
        @param string: word(s) to listen

        @type uids: list
        @param uids: user uids
        """
        pass

    @abc.abstractmethod
    def remove_listen(self, string):
        """
        Remove listen entry

        @type string: str
        @param string: word(s) listened
        """
        pass

    @abc.abstractclassmethod
    def get_listen_entries(self):
        """
        Get all listen entries as a dictionary

        @rtype: dict
        @return: dictionary of listen entries
        """
        pass

    @abc.abstractmethod
    def set_seen(self, uid, data):
        """
        Set seen entry

        @type uid: str
        @param uid: user's uid

        @type data: dict
        @param data: seen data
        """
        pass

    @abc.abstractmethod
    def get_seen(self, uid):
        """
        Get seen entry

        @type uid: str
        @param uid: user's uid to retrieve data for
        """
        pass

    @abc.abstractmethod
    def get_seen_entries(self, return_data=False):
        """
        Get all seen entries

        @type return_data: bool
        @param return_data: if True, it will be returned a dictionary containing all users and their seen data
                            otherwise, it will just return the seen user list

        @rtype: list|dict
        @return: list or dictionary depending on the return_data flag
        """
        pass

    @abc.abstractmethod
    def get_auto_delete_entries(self):
        """
        Get all auto delete entries as a list

        @rtype: list
        @return: list of auto delete entries
        """
        pass

    @abc.abstractmethod
    def add_auto_delete(self, uid, data):
        """
        Add auto delete entry

        @type uid: str
        @param uid: user's uid

        @type data: dict
        @param data: auto delete data
        """
        pass

    @abc.abstractmethod
    def remove_auto_delete(self, uid):
        """
        Delete auto delete entry

        @type uid: str
        @param uid: user's uid
        """
        pass