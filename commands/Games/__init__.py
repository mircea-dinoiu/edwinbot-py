# Project imports
from manager.Command.Utils import *
from util.games import *


class Games(CommandUtils):
    # games
    def command_games(self):
        games = list()
        for gameKey in self.db.store['games']:
            game_class_name = self.db.store['games'][gameKey]
            if game_class_name not in games:
                games.append(game_class_name)

        if 0 == len(games):
            self._message(self._lang('NO_GAMES').format(
                self._user_color()
            ))
        else:
            self._message(self._lang('GAMES').format(
                ', '.join([
                    highlight(self._game_name(game, True), 'Orange')
                    for game in games
                ])
            ))

    # game
    def command_game(self):
        if self.room.game:
            self._message(self._lang('GAME_RUNNING').format(
                highlight(self.room.game.name, 'Orange'),
                self._user_color()
            ))
        else:
            self._message(self._lang('NO_GAME_RUNNING').format(
                self._user_color()
            ))

    # startgame
    def command_startgame(self):
        if not self.args:
            self._message(self._lang('ERROR_NO_GAME_SPECIFIED').format(
                self._user_color()
            ))
        else:
            if self.room.game:
                self._message(self._lang('ERROR_GAME_IN_PROGRESS').format(
                    highlight(self.room.game.name, 'Orange'),
                    self._user_color()
                ))
            else:
                game_class_name = self._game_name(self.args[0])
                if game_class_name:
                    game_class = globals()[game_class_name]
                    self.room.game = game_class(self.room)

                    # Updating game in db (storing the class name, not the key)
                    self.db.update_room(self.room.name, {
                        'game': game_class_name
                    })
                else:
                    self._message(self._lang('ERROR_GAME_INEXISTENT').format(
                        highlight(self.args[0], 'Orange'),
                        self._user_color()
                    ))

    # stopgame
    def command_stopgame(self):
        if self.room.game:
            self._message(self._lang('SUCCESS_GAME_HAS_BEEN_STOPPED').format(
                highlight(self.room.game.name, 'Orange')
            ))
            self.room.game.stop()

            # Updating game in db
            self.db.update_room(self.room.name, {
                'game': ''
            })
        else:
            self._message(self._lang('ERROR_NO_GAME_RUNNING').format(
                self._user_color()
            ))

    # restartgame
    def command_restartgame(self):
        if self.room.game:
            self.room.game.reload(self.room)
        else:
            self._message(self._lang('ERROR_NO_GAME_RUNNING').format(
                self._user_color()
            ))

    # pausegame
    def command_pausegame(self):
        if self.room.game:
            self._message(self._lang('SUCCESS_GAME_HAS_BEEN_PAUSED').format(
                highlight(self.room.game.name, 'Orange')
            ))
            self.room.game.skip = True
        else:
            self._message(self._lang('ERROR_NO_GAME_RUNNING').format(
                self._user_color()
            ))

    # resumegame
    def command_resumegame(self):
        if self.room.game and self.room.game.skip:
            self._message(self._lang('SUCCESS_GAME_HAS_BEEN_RESUMED').format(
                highlight(self.room.game.name, 'Orange')
            ))
            if self.room.game.last_message:
                self._message(self.room.game.last_message)
            self.room.game.skip = False
        elif not self.room.game:
            self._message(self._lang('ERROR_NO_GAME_RUNNING').format(
                self._user_color()
            ))
        else:
            self._message(self._lang('ERROR_GAME_ALREADY_RUNNING').format(
                highlight(self.room.game.name, 'Orange'),
                self._user_color()
            ))

    # votegame
    def command_votegame(self):
        votes_needed = self.db.get_config('command.vote_game_needed')

        # No game specified error message
        if not self.args:
            self._message(self._lang('ERROR_NO_GAME_SPECIFIED').format(
                self._user_color()
            ))
        else:
            game_class_name = self._game_name(self.args[0])
            if game_class_name:
                # First game vote? prepare the dict
                if self.room.name not in self.db.store['vote_game']:
                    self._reset_vote_game_list()

                # Add a user to the vote game list
                self.db.store['vote_game'][self.room.name][game_class_name].add(self.user.uid)

                if votes_needed - len(self.db.store['vote_game'][self.room.name][game_class_name]):
                # Print out the game voted message
                    self._message(self._lang('SUCCESS_GAME_VOTED').format(
                        highlight(self._game_name(game_class_name, True), 'Orange'),
                        self._user_color(),
                        votes_needed - len(self.db.store['vote_game'][self.room.name][game_class_name])
                    ))

                # Trying to find out if a game has won
                for game_class_name in self.db.store['vote_game'][self.room.name]:
                    # Found the winner game
                    if 5 <= len(self.db.store['vote_game'][self.room.name][game_class_name]):
                        # Print out the vote ended message
                        self._message(self._lang('VOTE_GAME_ENDED').format(
                            highlight(
                                self._game_name(game_class_name, True),
                                'Orange'
                            )
                        ))

                        # Reset vote game list
                        self._reset_vote_game_list()

                        # Start the game
                        game_class = globals()[game_class_name]

                        # Stop the actual game if is running
                        if self.room.game:
                            self.room.game.stop()

                        # Link the game to the room
                        self.room.game = game_class(self.room)

                        # Make the change in the db
                        self.db.update_room(self.room.name, {
                            'game': game_class_name
                        })

                        # Stop the for loop
                        break
            else:
                self._message(self._lang('ERROR_GAME_INEXISTENT').format(
                    highlight(self.args[0], 'Orange'),
                    self._user_color()
                ))