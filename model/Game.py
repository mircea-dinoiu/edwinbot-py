# Python imports
import abc

# Project imports
from util.render import *
from util.localization import *


class Game:
    def __init__(self, room):
        self.game_name = None
        self.error = False
        self.skip = False
        self.last_message = None

        self.bot = room.manager
        self.db = self.bot.db
        self.room = room
        self.game_name = self._lang(self.__class__.__name__.upper() + '_GAME')

    @abc.abstractmethod
    def action(self, user, user_data, message):
        """
        Action method

        This method will be called on almost every message that doesn't
        represent a command and it will be used to keep the game up

        @type user: User
        @param user: User object

        @type user_data: dict
        @param user_data: user data retrieved from database

        @type message: str
        @param message: message received from user
        """
        pass
        
    def reload(self, room):
        """
        Reloads a game

        Sets the error flag to False then recall the __init__ method

        @type room: Room
        @param room: Room object
        """
        self.error = False
        self.__init__(room)
        
    def stop(self):
        """
        Stop the game

        Sets the error flag to True and the Bot manager will unlink the game from the room object
        """
        self.error = True

    # UTIL METHODS

    def _lang(self, key):
        """
        Util method to get a message related to the current room's language

        @type key: str
        @param key: lang message's key

        @rtype: str
        @return: the lang message
        """
        return self.bot.lang(key, self.room.lang)

    def _message(self, message, save=False):
        """
        Send a message on the room then save it as the last message if requested

        @type message: str
        @param message: message to send

        @type save: bool
        @param save: True if you want to save the message as the last message, False otherwise
        """
        # Don't send any messages if the game was stopped in some other place and the thread is still running
        if self.error:
            return

        # Add the game name before a message
        before = '[ {0} ] '.format(
            highlight(self.game_name, 'Orange')
        )
        after = message

        # Save the message if requested
        if save:
            self.last_message = before + after

        # Send the message
        self.room.message(before + after)

    def _format_coins(self, coins):
        """
        Format coins

        @type coins: int
        @param coins: coins

        @rtype: str
        @return: formatted coins
        """
        return self.bot.format_coins(coins, self.room.lang)

    def _user_color(self, user):
        """
        Get user colored name or nick name if is set

        @type user: User
        @param user: user

        @rtype: str
        @return: colored user name
        """
        #if user.nick is None:
        #    user.nick = self.db.get_user_data(user.uid, 'nick')
        #
        #if user.nick:
        #    return highlight(user.nick, 'Skin')
        #else:
        #    return highlight(
        #        user.name,
        #        'Green' if (user in self.room.get_user_list('all')) else 'Gray'
        #    )
        return highlight(
            user.name,
            'Green' if (user in self.room.get_user_list()) else 'Gray'
        )

    def _get_name(self):
        """Get game name"""
        return self.game_name
    
    name = property(_get_name)