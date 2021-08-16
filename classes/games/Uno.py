from classes.Game import Game
from classes.Player import Player
from discord import User, Message
import random


IMAGES: dict[str, str] = {}


class UnoCard:

    def __init__(self, name: str, color: str, number: int, image: str, special=False, symbol=""):
        self.name = name
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
    "r0": UnoCard("r0", "red", 0, ""), "r1": UnoCard("r1", "red", 1, ""), "r2": UnoCard("r2", "red", 2, ""),
    "r3": UnoCard("r3", "red", 3, ""), "r4": UnoCard("r4", "red", 4, ""), "r5": UnoCard("r5", "red", 5, ""),
    "r6": UnoCard("r6", "red", 6, ""), "r7": UnoCard("r7", "red", 7, ""), "r8": UnoCard("r8", "red", 8, ""),
    "r9": UnoCard("r9", "red", 9, ""), "r+2": UnoCard("r+2", "red", -1, "", True, "+2"),
    "r<>": UnoCard("r<>", "red", -1, "", True, "<>"), "rx": UnoCard("rx", "red", -1, "", True, "X"),
    "g0": UnoCard("g0", "green", 0, ""), "g1": UnoCard("g1", "green", 1, ""), "g2": UnoCard("g2", "green", 2, ""),
    "g3": UnoCard("g3", "green", 3, ""), "g4": UnoCard("g4", "green", 4, ""), "g5": UnoCard("g5", "green", 5, ""),
    "g6": UnoCard("g6", "green", 6, ""), "g7": UnoCard("g7", "green", 7, ""), "g8": UnoCard("g8", "green", 8, ""),
    "g9": UnoCard("g9", "green", 9, ""), "g+2": UnoCard("g+2", "green", -1, "", True, "+2"),
    "g<>": UnoCard("g<>", "green", -1, "", True, "<>"), "gx": UnoCard("gx", "green", -1, "", True, "X"),
    "b0": UnoCard("b0", "blue", 0, ""), "b1": UnoCard("b1", "blue", 1, ""), "b2": UnoCard("b2", "blue", 2, ""),
    "b3": UnoCard("b3", "blue", 3, ""), "b4": UnoCard("b4", "blue", 4, ""), "b5": UnoCard("b6", "blue", 5, ""),
    "b6": UnoCard("b6", "blue", 6, ""), "b7": UnoCard("b7", "blue", 7, ""), "b8": UnoCard("b8", "blue", 8, ""),
    "b9": UnoCard("b9", "blue", 9, ""), "b+2": UnoCard("b+2", "blue", -1, "", True, "+2"),
    "b<>": UnoCard("b<>", "blue", -1, "", True, "<>"), "bx": UnoCard("bx", "blue", -1, "", True, "X"),
    "y0": UnoCard("y0", "yellow", 0, ""), "y1": UnoCard("y1", "yellow", 1, ""), "y2": UnoCard("y2", "yellow", 2, ""),
    "y3": UnoCard("y3", "yellow", 3, ""), "y4": UnoCard("y4", "yellow", 4, ""), "y5": UnoCard("y5", "yellow", 5, ""),
    "y6": UnoCard("y6", "yellow", 6, ""), "y7": UnoCard("y7", "yellow", 7, ""), "y8": UnoCard("y8", "yellow", 8, ""),
    "y9": UnoCard("y9", "yellow", 9, ""), "y+2": UnoCard("y+2", "yellow", -1, "", True, "+2"),
    "y<>": UnoCard("y<>", "yellow", -1, "", True, "<>"), "yx": UnoCard("y<>", "yellow", -1, "", True, "X"),
    "+4": UnoCard("+4", "black", -2, "", True), "cc": UnoCard("cc", "black", -3, "", True)
}


default_deck: list[UnoCard] = []  # 76 Number Cards (19 each color), 24 Action cards(6 each color) and 8 wild cards

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


