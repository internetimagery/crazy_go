import __sabaki.go__board as GoBoard

from ..errors import InvalidMove
from ..utils import lappend
from .base import BaseRules, Move


__all__ = ["MultiColourRules"]


class MultiColourRules(BaseRules):
    """
    Go with 2 or more players!
    """

    def get_id(self) -> int:
        return 1

    def get_name(self) -> str:
        return "Normal"

    def get_description(self) -> str:
        return """
        Regular Go. But with an option to play multicolour/multiplayer.
        In three or more player games, opponents connected count as one group.
        """

    def move(self, move: Move) -> None:
        """
        Apply move to the board
        Player zero is empty space.
        """
        vertex = move.vertex
        player = move.player

        if player and self.board.get(vertex):
            raise InvalidMove("Illegal move: stone exists")

        # Player zero is empty space. Clearing space.
        if not player:
            new_board = self.board.set(vertex, 0)
            self.board = new_board
            lappend(self.moves, move)
            return

        # Place stone
        new_board = self.board.set(vertex, player)

        # Check if the move is valid and if it captures anything
        to_remove = []
        play_liberties = 0
        for neighbour in self.get_neighbors(new_board, vertex):
            value = new_board.get(neighbour)
            # Check for empty spots or connections to same groups
            if not value or value == player:
                play_liberties += 1
                continue

            # Check if we are capturing other group
            chain = self.get_chain(new_board, neighbour, player)
            liberties = 0
            for vtx in chain:
                for space in self.get_neighbors(new_board, vtx):
                    if not self.board.get(space):
                        liberties += 1
            if not liberties:
                for vtx in chain:
                    lappend(to_remove, vtx)

        if not len(to_remove) and not play_liberties:
            raise InvalidMove("Illegal move: self capture")

        # Capture
        captures = 0
        for vtx in to_remove:
            new_board = new_board.set(vtx, 0)
            captures += 1

        self.board = new_board
        move.captures = captures
        lappend(self.moves, move)


