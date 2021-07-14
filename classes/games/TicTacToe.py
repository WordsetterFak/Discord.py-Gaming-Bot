from classes.Game import Game
from classes.Player import Player


class TicTacToePlayer(Player):

    def __init__(self, discord_id: int, symbol: str):
        super().__init__(discord_id)
        self.symbol = symbol


class TicTacToeGame(Game):

    def __init__(self):
        super().__init__("TicTacToe", 2, 2)
