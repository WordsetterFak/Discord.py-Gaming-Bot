from classes.Game import Game
from classes.Player import Player
import random


EMOJIS = (":blue_square:", )


class Tiles:

    def __init__(self, emoji: str):
        self.emoji = emoji

    def __repr__(self):
        return self.emoji


class Water(Tiles):

    def __init__(self):
        super().__init__(":blue_square:")


class ExplodedShip(Tiles):

    def __init__(self):
        super().__init__(":boom:")


class Ship(Tiles):

    def __init__(self, name: str, size: int):
        super().__init__(":ship:")
        self.name = name
        self.size = size


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
        super().__init__()
        self.discord_id: int = discord_id
        self.fleet: list[Tiles] = []
        self.kills: int = 0
        self.rerolls: int = 3

    def build_fleet(self):

        fleet: list[Tiles] = [Water()] * 100

        def place_random(ship: Ship, fleet_copy: list[Tiles]):
            core = random.randint(0, 99)
            placed_parts = 0

            orientation = random.choice(["horizontal", "vertical"])

            if orientation == "vertical":
                adjust = 10
                upper_edge = core
                lower_edge = core

                for _ in range(ship.size):
                    next_placement_choices = []

                    if upper_edge not in range(10):
                        next_placement_choices.append("upper_edge")

                    if lower_edge not in range(90, 100):
                        next_placement_choices.append("lower_edge")

                    next_placement = random.choice(next_placement_choices)

                    if next_placement == "upper_edge":
                        fleet_copy[core - adjust] = ship
                        upper_edge = core - adjust
                    else:
                        fleet_copy[core + adjust] = ship
                        lower_edge = core + adjust
            else:
                adjust = 1
                right_edge = core  # TODO
                left_edge = core

            if placed_parts != ship.size:  # ship placement collided with pre-existing ship
                place_random(ship, fleet.copy())

            return fleet_copy

        self.fleet = fleet


class Battleship(Game):

    _games: dict = {}
    _MAX = 2
    _NAME = "Battleship"
    _NUMBER_OF_STARTING_SHIPS = 17

    def __init__(self, players: list[int]):
        super().__init__()
        self.player_ids: list[int] = players
