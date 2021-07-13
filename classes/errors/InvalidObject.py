

class InvalidObject(Exception):
    """
    This error is thrown, whenever a player is assigned to a game, when he is already in one
    """
    def __init__(self, expected_object: str, class_name: str):
        self.message = f"{expected_object} was expected, but {class_name} was given"
        super().__init__(self.message)
