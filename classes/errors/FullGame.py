class FullGame(Exception):
    """
    This error is thrown, whenever a player is assigned to a game, when he is already in one
    """
    def __init__(self, game_name: str):
        self.message = f"{game_name} is full"
        super().__init__(self.message)
