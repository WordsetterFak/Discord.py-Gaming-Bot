from classes.errors.FullGame import FullGame
from classes.errors.InvalidObject import InvalidObject


class Game:
    """
    Abstract Game class, for template purposes
    """
    _MAX = 0
    _NAME = "Default Game"

    def __init__(self):
        self._players: list = []  # player_list

    def get_players(self) -> tuple:
        return tuple(self._players.copy())

    def start(self):
        pass

    def conclude(self):
        pass

    def add_player(self, player):
        if len(self._players) + 1 > self._MAX:
            raise FullGame(self._NAME)

        if hasattr(player, "get_discord_id"):
            self._players.append(player)
        else:
            raise InvalidObject("<class 'classes.Player.Player'>", player.__class__)
