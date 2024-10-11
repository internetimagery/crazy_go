
__all__ = ("NotImplementedError", "GameError", "InvalidMove")

class NotImplementedError(Exception):
    pass

class GameError(Exception):
    pass


class InvalidMove(GameError):
    pass
