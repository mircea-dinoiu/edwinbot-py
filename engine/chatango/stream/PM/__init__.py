# Project imports
from engine.chatango.common.Stream import Stream
from engine.chatango.stream.PM.Handlers import Handlers


class PM(Stream, Handlers):
    # Authentication ID
    def get_auth_id(self):
        return self._auth_id

    # Contacts
    def get_contacts(self):
        return self._contacts

    # Block list
    def get_block_list(self):
        return self._block_list

    def get_unblock_list(self):
        return self._unblock_list

    auth_id = property(get_auth_id)
    contacts = property(get_contacts)
    block_list = property(get_block_list)
    unblock_list = property(get_unblock_list)