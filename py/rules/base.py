import __sabaki.go__board as GoBoard

from ..errors import NotImplementedError
from ..utils import to_int, to_char, lappend, match_regex, min, max

__all__ = ("BaseRules", "Move")


class Move:
    """
    Individual move
    """
    def __init__(self, player: int, vertex: List[int, int], captures: int = 0):
        self.player = player
        self.vertex = vertex
        self.captures = captures


    @classmethod
    def fromStr(self, move: str) -> Move:
        return Move(
            to_int(move[0]),
            (to_int(move[1]), to_int(move[2])),
        )

    def toStr(self) -> str:
        return to_char(self.player) + to_char(self.vertex[0]) + to_char(self.vertex[1])



class BaseRules:
    """
    Encapsulate game logic
    """
    def __init__(self) -> None:
        self.player_meta = {"min": 2, "max": 6, "default": 2, "current": 2}
        self.board_meta = {"min": 4, "max": 19, "default": 9, "current": 9}
        self.board = GoBoard.fromDimensions(self.board_meta["current"])
        self.moves = []

    def get_id(self) -> int:
        """
        Return a unique ID for the rule.
        """
        raise NotImplementedError("Override this")

    def get_name(self) -> str:
        """
        Name visible on screen
        """
        raise NotImplementedError("Override this")

    def get_description(self) -> str:
        """
        Description visible on screen
        """
        raise NotImplementedError("Override this")

    def move(self, move: Move) -> None:
        """
        Make a move in the game
        """
        raise NotImplementedError("Override this")

    def get_next_player(self) -> int:
        """
        Get player that is going next
        """
        if len(self.moves):
            next_player = self.moves[-1].player + 1
            if next_player <= self.player_meta["current"]:
                return next_player
        return 1

    def load_game(self, game_hash: str) -> None:
        """
        Load game data to url hash
        """
        if len(game_hash):
            self.player_meta["current"] = to_int(game_hash[0])
            self.board_meta["current"] = to_int(game_hash[1])
        else:
            self.player_meta["current"] = self.player_meta["default"]
            self.board_meta["current"] = self.board_meta["default"]

        self.moves = [] # Reset moves and board
        self.board = GoBoard.fromDimensions(self.board_meta["current"])

        moves = match_regex(r"[a-zA-Z]{3}", game_hash[2:])
        for i in range(len(moves)):
            move = Move.fromStr(moves[i])
            self.move(move)

    def save_game(self) -> str:
        """
        Save game data to url hash
        """
        meta_state = to_char(self.get_id()) + to_char(self.player_meta["current"]) + to_char(self.board_meta["current"])
        for move in self.moves:
            meta_state += move.toStr()
        return meta_state

    def set_num_players(self, players:int) -> int:
        """
        Set player number, fitting within the defined range
        """
        self.player_meta["current"] = min(self.player_meta["max"], max(self.player_meta["min"], players))
        return self.player_meta["current"]

    def set_board_size(self, size:int) -> int:
        """
        Set board size, fitting within the defined range
        """
        self.board_meta["current"] = min(self.board_meta["max"], max(self.board_meta["min"], size))
        return self.board_meta["current"]

    def get_chain(self, board: GoBoard, vertex: Tuple[int, int], player: int) -> List[Tuple[int, int]]:
        """
        Get list of vertices that represent the whole connected group
        """
        chain = []
        value = board.get(vertex)
        if not value:
            return chain

        is_player = value == player
        seen = Set()
        queue = [vertex]
        while len(queue):
            vtx = queue.pop()

            key = str(vtx)
            if key in seen:
                continue
            seen.add(key)

            val = board.get(vtx)
            if not val:
                continue

            # If isPlayer then we want only colours of that player.
            # Else we want any other colour that is not that player.
            if (is_player and val != player) or (not is_player and val == player):
                continue

            lappend(chain, vtx)
            for neighbour in self.get_neighbors(board, vtx):
                lappend(queue, neighbour)

        return chain

    def get_neighbors(self, board: GoBoard, vertex: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Collect stones around the given stone
        """
        return board.getNeighbors(vertex)
