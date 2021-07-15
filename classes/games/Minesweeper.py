from classes.Game import Game
from discord import User
import random

NUMBER_OF_BOMBS = 11  # Minesweeper is 9x9
SIZE = 9


class Tiles:

    def __init__(self, emoji: str):
        self.emoji = emoji

    def __repr__(self):
        return self.emoji


class Bomb(Tiles):

    def __init__(self):
        super().__init__(":boom:")

    def __repr__(self):
        return "X"

class Flag(Tiles):

    def __init__(self):
        super().__init__(":golf:")
        self.number = 0


class UnrevealedTile(Tiles):

    def __init__(self):
        super().__init__(":black_square_button:")


class Tile(Tiles):

    number_to_emoji: dict[str, str] = {
        "0": ":white_large_square:", "1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:",
        "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:"
    }

    def __init__(self, number: int):
        super().__init__(self.number_to_emoji[str(number)])
        self.number = number

    def __repr__(self):
        return str(self.number)


class MinesweeperBoard:

    def __init__(self):
        self.display_board: list[Tiles] = [UnrevealedTile()] * (SIZE ** 2)
        self.board: list[Tiles] = self.create_board()
        self.place_flag()

    def create_board(self):

        unprocessed_tile = UnrevealedTile()

        board = [unprocessed_tile] * (SIZE ** 2)

        bombs_placed = 0

        while bombs_placed < NUMBER_OF_BOMBS:

            random_spot = random.randint(0, SIZE ** 2 - 1)

            if not isinstance(board[random_spot], Bomb):

                board[random_spot] = Bomb()
                bombs_placed += 1

        for n, tile in enumerate(board):

            if not isinstance(tile, Bomb):

                surrounding_bombs = 0

                # horizontal check

                if n % SIZE != 0:  # ensure n is not the furthest left in the row

                    if isinstance(board[n - 1], Bomb):  # left

                        surrounding_bombs += 1

                if (n + 1) % SIZE != 0:  # ensure n is not the furthest right in the row

                    if isinstance(board[n + 1], Bomb):  # left

                        surrounding_bombs += 1

                # vertical checks

                if n > SIZE - 1:  # ensure n is not in the top row

                    if isinstance(board[n - SIZE], Bomb):

                        surrounding_bombs += 1

                if n + SIZE < SIZE ** 2:  # ensure n is not in the bottom row

                    if isinstance(board[n + SIZE], Bomb):

                        surrounding_bombs += 1

                # diagonal checks ( something is going wrong here # FIXME)

                if n % SIZE != 0 and n > SIZE - 1:  # upper left diagonal

                    if isinstance(board[n - SIZE - 1], Bomb):

                        surrounding_bombs += 1

                if n % SIZE != 0 and n + SIZE < SIZE ** 2:  # bottom left diagonal

                    if isinstance(board[n + SIZE - 1], Bomb):

                        surrounding_bombs += 1

                if (n + 1) % SIZE != 0 and n > SIZE - 1:  # upper right diagonal

                    if isinstance(board[n - SIZE + 1], Bomb):

                        surrounding_bombs += 1

                if (n + 1) % SIZE != 0 and n + SIZE < SIZE ** 2:  # bottom right diagonal

                    if isinstance(board[n + SIZE + 1], Bomb):

                        surrounding_bombs += 1

                board[n] = Tile(surrounding_bombs)

        return board

    def place_flag(self):
        pass


class MinesweeperGame(Game):
    """
    This is a singeplayer game, accessible only in dms
    """

    def __init__(self, player_disc: User):
        super().__init__("Minesweeper", 1, 1)
        self.player = player_disc
