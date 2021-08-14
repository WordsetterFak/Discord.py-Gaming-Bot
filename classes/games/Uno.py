from classes.Game import Game
from classes.Player import Player
from discord import User, Message


class UnoCard:

    def __init__(self, color: str, number: int, image: str):
        self.color = color
        self.number = number
        self.image = image
        self.plus2 = False


class SpecialCard:
    pass


class UnoPlayer(Player):

    def __init__(self, discord_id: int):
        super().__init__(discord_id)


class UnoGame(Game):

    def __init__(self):
        super().__init__("Uno", 4, 1)
