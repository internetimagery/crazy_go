import __sabaki.go__board as GoBoard

from .utils import to_int, to_char, lappend, RuntimeError, match_regex, min, max


__all__ = ("load_game_rule", "MultiColourRules", "BorderLessRules")


def load_game_rule(game_hash: str, rules: List[BaseRules]) -> BaseRules:
    """
    Load game from stored url hash
    """
    if not len(rules):
        raise RuntimeError("There needs to be at least one rule")
    if not len(game_hash):
        return rules[0]
    rule_id = to_int(game_hash[0])
    for rule in rules:
        if rule_id == rule.get_id():
            rule.load_game(game_hash[1:])
            return rule

    raise RuntimeError("Rule provided not one of the requested rules")



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
        raise RuntimeError("Override this")

    def get_name(self) -> str:
        """
        Name visible on screen
        """
        raise RuntimeError("Override this")

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
            move = {
                "player": to_int(moves[i][0]),
                "vtx": (to_int(moves[i][1]), to_int(moves[i][2])),
            }
            lappend(self.moves, move)
            note, new_board, captures = self.move(self.board, move)
            self.board = new_board

    def save_game(self) -> str:
        """
        Save game data to url hash
        """
        meta_state = to_char(self.get_id()) + to_char(self.player_meta["current"]) + to_char(self.board_meta["current"])
        for move in self.moves:
            meta_state += to_char(move["player"]) + to_char(move["vtx"][0]) + to_char(move["vtx"][1])
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

    def move(self, board: GoBoard, sign: int, vertex: Tuple[int, int]) -> Tuple[str, GoBoard, int]:
        raise RuntimeError("Need to provide some logic")

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
        neighbours = board.getNeighbors(vertex)

        if self.state["gamemode"]:
            # Normal game mode
            return neighbours

        # Borderless game mode. Neighbors cross the boundary between sides.
        if vertex[0] == 0:
            lappend(neighbours, [board.width-1, vertex[1]])
        if vertex[1] == 0:
            lappend(neighbours, [vertex[0], board.height-1])
        if vertex[0] == board.width-1:
            lappend(neighbours, [0, vertex[1]])
        if vertex[1] == board.height-1:
            lappend(neighbours, [vertex[0], 0])

        return neighbours



class MultiColourRules(BaseRules):

    def get_id(self) -> int:
        return 1

    def get_name(self) -> str:
        return "Normal"

    def move(self, board: GoBoard, sign: int, vertex: Tuple[int, int]) -> Tuple[str, GoBoard, int]:
        """
        Apply move to the board
        """
        new_board = board
        captures = 0
        note = ""

        if sign and board.get(vertex):
            note = "Illegal move: stone exists"
            return note, new_board, captures

        if not sign:
            new_board = board.set(vertex, 0)
            return note, new_board, captures

        new_board = new_board.set(vertex, sign)

        to_remove = []
        play_liberties = 0
        for neighbour in self.get_neighbors(new_board, vertex):
            value = new_board.get(neighbour)
            if not value or value == sign:
                play_liberties += 1
                continue
            chain = self.get_chain(new_board, neighbour, sign)
            liberties = 0
            for vtx in chain:
                for space in self.get_neighbors(new_board, vtx):
                    if not board.get(space):
                        liberties += 1
            if not liberties:
                for vtx in chain:
                    lappend(to_remove, vtx)

        if not len(to_remove) and not play_liberties:
            note = "Illegal move: self capture";
            new_board = new_board.set(vertex, 0)
            return note, new_board, captures

        # Capture
        for vtx in to_remove:
            new_board = new_board.set(vtx, 0)
            captures += 1

        return note, new_board, captures


class BorderLessRules(BaseRules):
    def get_id(self) -> int:
        return 2

    def get_name(self) -> str:
        return "Borderless"
