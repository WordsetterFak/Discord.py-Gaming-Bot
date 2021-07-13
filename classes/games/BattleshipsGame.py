from classes.Game import Game
from classes.Player import Player
from time import time
import random


class Tiles:

    def __init__(self, emoji: str):
        self.emoji = emoji

    def __repr__(self):
        return self.emoji


class Water(Tiles):

    def __init__(self):
        super().__init__(":blue_square:")


class DisturbedWater(Tiles):
    # a water tile, that was hit by a shot
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


class Battleship(Ship):
    def __init__(self):
        super().__init__("Battleship", 4)


class AircraftCarrier(Ship):

    def __init__(self):
        super().__init__("Aircraft Carrier", 5)


class BattleshipsPlayer(Player):

    def __init__(self, discord_id: int):
        super().__init__(discord_id)
        self.kills: int = 0
        self.rerolls: int = 3
        self.fleet: list[Tiles] = self.build_fleet()

    def build_fleet(self):

        fleet: list[Tiles] = [Water()] * 100
        expected_ships: int = 0

        def place(ship_to_be_placed: Ship):

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

        for ship in [AircraftCarrier(), Battleship(), Cruiser(), Cruiser(), Destroyer()]:

            expected_ships += ship.size
            fleet = place(ship)

        return fleet

    def reroll(self) -> int:
        if self.rerolls < 1:
            return 0

        self.fleet: list[Tiles] = self.build_fleet()

        self.rerolls -= 1
        return self.rerolls


class BattleshipsGame(Game):

    _player_to_game: dict = {}  # allows player to change fleet in dms
    _channel_to_game: dict = {}

    _MAX = 2
    _NAME = "Battleship"

    _NUMBER_OF_STARTING_SHIPS = 17
    _TIMEOUT = 60  # seconds

    _row_to_number: dict[str, int] = {  # convert row  to number (ex. b -> 10)
        "a": 0, "b": 10, "c": 20, "d": 30, "e": 40, "f": 50, "g": 60, "h": 70, "i": 80, "j": 90
    }

    def __init__(self, players: list[int]):
        super().__init__()

        self.player_ids: list[int] = players
        self.players = [BattleshipsPlayer(self.player_ids[0]), BattleshipsPlayer(self.player_ids[1])]

        self.next = self.players[0]
        self.winner: [BattleshipsPlayer, None] = None

        self.timer: float = 0  # keep track of time between rounds
        self.total_time: float = time()

    def other_player(self):
        return self.players[0] if self.next != self.players[0] else self.players[1]

    def next_round(self):
        self.timer = time()
        self.next = self.other_player()

    def display(self) -> str:
        txt_display = ""

        for i in range(100):
            txt_display += f"{self.next.fleet[i:i+10]}"

        return txt_display

    def check_win(self) -> bool:
        if self.next.kills >= 17:
            return True

        return False

    def timeout(self) -> bool:
        return time() - self.timer > self._TIMEOUT

    def shoot(self, row: str, column: int) -> tuple[str, bool]:
        column -= 1  # list index starts at 0, so the column is offset by 1 to make up for that

        position = self._row_to_number[row] + column

        other_player = self.other_player()

        hit = other_player.fleet[position]
        hit_pos = str(hit)
        destroyed = False

        if isinstance(hit, Ship):
            destroyed = hit.hit()
            other_player.fleet[position] = ExplodedShip()
        elif isinstance(hit, Water):
            other_player.fleet[position] = DisturbedWater()

        return hit_pos, destroyed

    def is_turn(self, discord_id: int) -> bool:
        return discord_id == self.next.discord_id
