from classes.Game import Game
from classes.Player import Player
import random


class Tiles:

    def __init__(self, emoji: str):
        self.emoji = emoji

    def __repr__(self):
        return self.emoji


class Water(Tiles):

    def __init__(self):
        super().__init__(":blue_square:")


class HitWater(Tiles):

    def __init__(self):
        super().__init__(":radio_button:")


class ExplodedShip(Tiles):

    def __init__(self):
        super().__init__(":boom:")


class Ship(Tiles):

    def __init__(self, name: str, size: int):
        super().__init__(":ship:")
        self.name = name
        self.size = size
        self.remaining = size

    def hit(self) -> bool:
        self.remaining -= 1

        if self.remaining <= 0:
            return True  # Ship was completely destroyed

        return False


class Destroyer(Ship):

    def __init__(self):
        super().__init__("Destroyer", 2)


class Cruiser(Ship):

    def __init__(self):
        super().__init__("Cruiser", 3)


class Dreadnought(Ship):
    # named Dreadnought, since the game class is named Battleship
    def __init__(self):
        super().__init__("Battleship", 4)


class AircraftCarrier(Ship):

    def __init__(self):
        super().__init__("Aircraft Carrier", 5)


class BattleshipPlayer(Player):

    def __init__(self, discord_id: int):
        super().__init__(discord_id)
        self.kills: int = 0
        self.rerolls: int = 3
        self.fleet: list[Tiles] = self.build_fleet()
        self.opponent = None

    def build_fleet(self):

        fleet: list[Tiles] = [Water()] * 100
        expected_ships: int = 0

        def place_random(ship_to_be_placed: Ship):

            while True:

                fleet_copy = fleet.copy()

                core = random.randint(0, 99)
                fleet_copy[core] = ship_to_be_placed

                orientation = random.choice(["horizontal", "vertical"])

                if orientation == "vertical":
                    adjust = 10  # next vertical element
                else:
                    adjust = 1  # next horizontal element

                minus_edge = core  # upper edge or left edge depending on orientation
                plus_edge = core  # lower edge or right edge depending on orientation

                for _ in range(ship.size - 1):  # the -1 represents the core that has already been placed
                    next_placement_choices = []

                    if orientation == "vertical":

                        if minus_edge > 9:
                            next_placement_choices.append("minus_edge")

                        if plus_edge < 90:
                            next_placement_choices.append("plus_edge")

                    else:  # horizontal

                        if minus_edge % 10 != 0:
                            next_placement_choices.append("minus_edge")

                        if (plus_edge + 1) % 10 != 0:
                            next_placement_choices.append("plus_edge")

                    next_placement = random.choice(next_placement_choices)

                    if next_placement == "minus_edge":

                        minus_edge -= adjust
                        fleet_copy[minus_edge] = ship_to_be_placed

                    else:

                        plus_edge += adjust
                        fleet_copy[plus_edge] = ship_to_be_placed

                if len([x for x in fleet_copy if isinstance(x, Ship)]) == expected_ships:  # no ship collision occurred
                    return fleet_copy

        for ship in [AircraftCarrier(), Dreadnought(), Cruiser(), Cruiser(), Destroyer()]:
            expected_ships += ship.size
            fleet = place_random(ship)

        return fleet


class Battleship(Game):

    _games: dict = {}
    _MAX = 2
    _NAME = "Battleship"
    _NUMBER_OF_STARTING_SHIPS = 17

    def __init__(self, players: list[int]):
        super().__init__()
        self.player_ids: list[int] = players
