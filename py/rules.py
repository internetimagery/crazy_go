import __sabaki.go__board as GoBoard

from .errors import InvalidMove
from .utils import lappend
from .base_rules import BaseRules, Move


__all__ = ("MultiColourRules", "BorderLessRules")


class MultiColourRules(BaseRules):
    """
    Go with 2 or more players!
    """

    def get_id(self) -> int:
        return 1

    def get_name(self) -> str:
        return "Normal"

    def move(self, move: Move) -> None:
        """
        Apply move to the board
        Player zero is empty space.
        """
        board = self.board
        new_board = self.board
        captures = 0

        vertex = move.vertex
        player = move.player

        if player and board.get(vertex):
            raise InvalidMove("Illegal move: stone exists")

        move = {"player": player, "vtx": vertex, "captures": 0}
        lappend(self.moves, move)

        # Player zero is empty space. Clearing space.
        if not player:
            new_board = board.set(vertex, 0)
            move = {"player": player, "vtx": vertex}
            lappend(self.moves, move)
            self.board = new_board
            return

        new_board = new_board.set(vertex, player)

        to_remove = []
        play_liberties = 0
        for neighbour in self.get_neighbors(new_board, vertex):
            value = new_board.get(neighbour)
            if not value or value == player:
                play_liberties += 1
                continue
            chain = self.get_chain(new_board, neighbour, player)
            liberties = 0
            for vtx in chain:
                for space in self.get_neighbors(new_board, vtx):
                    if not board.get(space):
                        liberties += 1
            if not liberties:
                for vtx in chain:
                    lappend(to_remove, vtx)

        if not len(to_remove) and not play_liberties:
            raise InvalidMove("Illegal move: self capture")
            new_board = new_board.set(vertex, 0)
            self.board = new_board
            return

        # Capture
        for vtx in to_remove:
            new_board = new_board.set(vtx, 0)
            captures += 1

        self.board = new_board


class BorderLessRules(MultiColourRules):
    def get_id(self) -> int:
        return 2

    def get_name(self) -> str:
        return "Borderless"

    def get_neighbors(self, board: GoBoard, vertex: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Collect stones around the given stone
        Neighbors cross the boundary between sides.
        """
        neighbours = board.getNeighbors(vertex)
        if vertex[0] == 0:
            lappend(neighbours, [board.width-1, vertex[1]])
        if vertex[1] == 0:
            lappend(neighbours, [vertex[0], board.height-1])
        if vertex[0] == board.width-1:
            lappend(neighbours, [0, vertex[1]])
        if vertex[1] == board.height-1:
            lappend(neighbours, [vertex[0], 0])
        return neighbours
