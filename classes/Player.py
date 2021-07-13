
class Player:
    """
    Used for type hinting and to differentiate game objects from non game objects.
    Also keeps the occupied_players list, which exists to prevent keep track of players who are in a game
    """
    occupied_players: list[int] = []
