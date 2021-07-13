from classes.errors.InGameError import InGameError
from classes.errors.InvalidObject import InvalidObject


class Player:
    """
    Abstract Player class, for template purposes
    """
    def __init__(self, discord_id: int):
        self._discord_id: int = discord_id
        self._game = None  # Game object or None

    def get_discord_id(self):
        return self._discord_id

    def get_current_game(self):
        return self._game

    def assign_to_game(self, game):
        if self._game is not None:
            raise InGameError(self._discord_id)

        if hasattr(game, "get_players"):
            self._game = game
        else:
            raise InvalidObject("<class 'classes.Game.Game'>", game.__class__)

    def remove_from_game(self):
        self._game = None
