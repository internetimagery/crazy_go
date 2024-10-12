
from .multicolour import MultiColourRules

__all__ = ["BorderLessRules"]


class BorderLessRules(MultiColourRules):
    def get_id(self) -> int:
        return 2

    def get_name(self) -> str:
        return "Borderless"

    def get_description(self) -> str:
        return """
        Go, with no borders. Instead of hitting a boarder, you wrap around.
        """

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
