

class InGameError(Exception):
    """
    This error is thrown, whenever a player is assigned to a game, when he is already in one
    """
    def __init__(self, discord_id: int):
        self.message = f"Player #{discord_id} is already in a game"
        super().__init__(self.message)
