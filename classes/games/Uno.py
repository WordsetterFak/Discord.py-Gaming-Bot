from classes.Game import Game
from classes.Player import Player
from discord import User, Message
import random


IMAGES: dict[str, str] = {}


class UnoCard:

    def __init__(self, color: str, number: int, image: str, special=False, symbol=""):
        self.color = color  # red, green, blue, yellow, black
        self.number = number  # 0-9, -1 for non numbered colored cards and -2/-3 for wildcards
        self.image = image
        self.special = special  # +2, reverse, skip turn cards and wild cards

        if symbol == "":
            self.symbol = number

        else:
            self.symbol = symbol  # for display reasons (Ex -> Red X)

    def display(self) -> str:

        if self.color != "black":
            return f"{self.color.capitalize()} {self.symbol}"

        else:

            if self.number == -2:
                return "+4 Card"

            else:
                return "Colour Change"


all_cards: dict[str, UnoCard] = {
    "r0": UnoCard("red", 0, ""), "r1": UnoCard("red", 1, ""), "r2": UnoCard("red", 2, ""),
    "r3": UnoCard("red", 3, ""), "r4": UnoCard("red", 4, ""), "r5": UnoCard("red", 5, ""),
    "r6": UnoCard("red", 6, ""), "r7": UnoCard("red", 7, ""), "r8": UnoCard("red", 8, ""),
    "r9": UnoCard("red", 9, ""), "r+2": UnoCard("red", -1, "", True, "+2"),
    "r<>": UnoCard("red", -1, "", True, "<>"), "rx": UnoCard("red", -1, "", True, "X"),
    "g0": UnoCard("green", 0, ""), "g1": UnoCard("green", 1, ""), "g2": UnoCard("green", 2, ""),
    "g3": UnoCard("green", 3, ""), "g4": UnoCard("green", 4, ""), "g5": UnoCard("green", 5, ""),
    "g6": UnoCard("green", 6, ""), "g7": UnoCard("green", 7, ""), "g8": UnoCard("green", 8, ""),
    "g9": UnoCard("green", 9, ""), "g+2": UnoCard("green", -1, "", True, "+2"),
    "g<>": UnoCard("green", -1, "", True, "<>"), "gx": UnoCard("green", -1, "", True, "X"),
    "b0": UnoCard("blue", 0, ""), "b1": UnoCard("blue", 1, ""), "b2": UnoCard("blue", 2, ""),
    "b3": UnoCard("blue", 3, ""), "b4": UnoCard("blue", 4, ""), "b5": UnoCard("blue", 5, ""),
    "b6": UnoCard("blue", 6, ""), "b7": UnoCard("blue", 7, ""), "b8": UnoCard("blue", 8, ""),
    "b9": UnoCard("blue", 9, ""), "b+2": UnoCard("blue", -1, "", True, "+2"),
    "b<>": UnoCard("blue", -1, "", True, "<>"), "bx": UnoCard("blue", -1, "", True, "X"),
    "y0": UnoCard("yellow", 0, ""), "y1": UnoCard("yellow", 1, ""), "y2": UnoCard("yellow", 2, ""),
    "y3": UnoCard("yellow", 3, ""), "y4": UnoCard("yellow", 4, ""), "y5": UnoCard("yellow", 5, ""),
    "y6": UnoCard("yellow", 6, ""), "y7": UnoCard("yellow", 7, ""), "y8": UnoCard("yellow", 8, ""),
    "y9": UnoCard("yellow", 9, ""), "y+2": UnoCard("yellow", -1, "", True, "+2"),
    "y<>": UnoCard("yellow", -1, "", True, "<>"), "yx": UnoCard("yellow", -1, "", True, "X"),
    "+4": UnoCard("black", -2, "", True), "cc": UnoCard("black", -3, "", True)
}


default_deck: list[UnoCard] = []

for color in ('b', 'y', 'g', 'r'):
    default_deck.append(all_cards[f"{color}0"])
    for _ in range(2):

        default_deck.append(all_cards["+4"])  # add wildcards
        default_deck.append(all_cards["cc"])

        for k in ("+2", "x", "<>"):
            default_deck.append(all_cards[f"{color}{k}"])

        for n in range(1, 10):
            default_deck.append(all_cards[f"{color}{n}"])


class UnoPlayer(Player):

    def __init__(self, discord_id: int, discord_user: User):
        super().__init__(discord_id)
        self.hand: list[UnoCard] = []
        self.discord_user = discord_user


class UnoGame(Game):

    def __init__(self, players: tuple[tuple[int, User]]):
        super().__init__("Uno", 4, 2)
        self.card_pickups = 0  # from +2/+4 cards
        self.non_constructed_players = players  # players not yet constructed into UnoPlayer objects
        self.players: list[UnoPlayer] = []
        self.deck: list[UnoCard] = self.new_deck()
        self.movement = 1  # 1 by default, multiplied by -1 every time a reverse card is dropped
        self.current_pos = 0
        self.ongoing = False

    def new_deck(self) -> list[UnoCard]:
        new_deck = default_deck.copy()
        random.shuffle(new_deck)
        return new_deck

    def current_player(self) -> int:
        return self.players[self.current_pos].discord_id

    def begin_game(self):
        pass


