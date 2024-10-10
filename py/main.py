#_ = __pragma__('js', '{}', 'import { h, render, Component } from "preact"')
#_ = __pragma__('js', '{}', 'import GoBoard from "@sabaki/go-board"')
#_ = __pragma__('js', '{}', 'import { Goban } from "@sabaki/shudan"')
#_ = __pragma__('js', '{}', 'import html2canvas from "html2canvas-pro"')
#_ = __pragma__('js', '{}', 'import "@sabaki/shudan/css/goban.css"')
#_ = __pragma__('js', '{}', 'import "../css/main.css"')

from preact import h, render, Component
import __sabaki.go__board as GoBoard
from __sabaki.shudan import Goban
import html2canvas__pro as html2canvas


char_map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_int(character: str) -> int:
    """
    a = 0; b = 1; c = 2; etc...
    """
    return char_map.indexOf(character)


def to_char(number: int) -> str:
    """
    0 = a; 1 = b; 2 = c; etc...
    """
    return char_map[number]


def match_regex(expression: str, search: str) -> List[str]:
    """
    Similar to...

    >>> re.match(expression, search)
    """
    reg = RegExp(expression, "g")
    return reg.exec(search) or ()

def lappend(collection, value):
    collection.push(value)

min = Math.min
max = Math.max


def create_two_way_checkbox(component):

    def callback(state_key, text):
        return h(
            "label",
            {
                "style": {
                    "display": "flex",
                    "alignItems": "center",
                },
            },
            h(
                "input",
                {
                    "style": {
                        "marginRight": ".5em",
                    },
                    "type": "checkbox",
                    "checked": component.state[state_key],
                    "onClick": lambda: component.setState(lambda s: {state_key: not s[state_key]}),
                },
            ),
            h(
                "span",
                {
                    "style": {
                        "userSelect": "none",
                    },
                },
                text,
            ),
        )

    return callback


class App(Component):

    def __init__(self, props):
        super().__init__(props)

        board_size = 9
        max_players = 2
        game_mode = 1
        game_hash = window.location.hash[1:]

        if game_hash:
            board_size = to_int(game_hash[0])
            game_mode = 1 if to_int(game_hash[1]) >= 10 else 0
            max_players = to_int(game_hash[1]) - 10 if game_mode else 0
        else:
            window.location.hash = "#" + to_char(board_size) + to_char(max_players + (10 if game_mode else 0))

        self.state = {
            "board": GoBoard.fromDimensions(board_size),
            "boardSize": board_size,
            "vertexSize": 24,
            "showCoordinates": False,
            "fuzzyStonePlacement": True,
            "animateStonePlacement": True,
            "isBusy": False,
            "players": max_players,
            "gamemode": game_mode,
        }

        self.CheckBox = create_two_way_checkbox(self)

        moves = match_regex(r"[\-a-zA-Z]{3}", game_hash[2:])
        for i in range(len(moves)):
            move = moves[i]
            player = to_int(move[0]) - 10
            if move != "---":
                vtx = [to_int(move[1]), to_int(move[2])]
                note, new_board, captures = self.move(self.state["board"], player + 1, vtx, game_mode)
                self.setState({"board": new_board})



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

    def render(self) -> None:
        """
        Build visual elements of the board on screen.
        """
        board = self.state["board"]
        players = self.state["players"]
        gamemode = self.state["gamemode"]
        board_size = self.state["boardSize"]
        vertexSize = self.state["vertexSize"]
        showCoordinates = self.state["showCoordinates"]
        fuzzyStonePlacement = self.state["fuzzyStonePlacement"]
        animateStonePlacement = self.state["animateStonePlacement"]

        game_hash = window.location.hash
        if len(game_hash) < 4:
            window.location.hash = "#" + to_char(board_size) + to_char(players + (10 if gamemode else 0))
            if board_size != board.width:
                self.setState({"board": GoBoard.fromDimensions(board_size)})

        return h(
            "section",
            {
                "style": {
                    "display": "grid",
                    "gridTemplateColumns": "15em auto",
                    "gridColumnGap": "1em",
                },
            },
            h(
                "form",
                {
                    "style": {
                        "display": "flex",
                        "flexDirection": "column",
                    },
                },
                h(
                    "p",
                    {
                        "style": {
                            "margin": "0 0 .5em 0"
                        },
                    },
                    "Zoom: ",
                    h(
                        "button",
                        {
                            "type": "button",
                            "onClick": lambda evt: self.setState(lambda s: {"vertexSize": max(s.vertexSize - 4, 4)}),
                        },
                        "-",
                    ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "title": "Reset",
                        "onClick": lambda evt: self.setState({"vertexSize": 24 }),
                    },
                    "•"
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"vertexSize": s.vertexSize + 4 }),
                    },
                    "+"
                ),
            ),
            h(
                "p",
                {
                    "style": {
                        "margin": "0 0 .5em 0",
                    },
                },
                "Players: ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"players": max(s.players - 1, 2)}),
                    },
                    "-"
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "title": "Reset",
                        "onClick": lambda evt: self.setState(lambda s: {"players": to_int(window.location.hash[2])}),
                    },
                    players,
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"players": min(s.players + 1, 6), }),
                    },
                    "+"
                ),
            ),
            h(
                "p",
                {
                    "style": {
                        "margin": "0 0 .5em 0"
                    },
                },
                "Board Size: ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"boardSize": max(s["boardSize"] - 1, 4)}),
                    },
                    "-"
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "title": "Reset",
                        "onClick": lambda evt: self.setState(lambda s: {"boardSize": to_int(window.location.hash[1])}),
                    },
                    board_size,
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"boardSize": min(s["boardSize"] + 1, 19), }),
                    },
                    "+"
                )
            ),
            h(
                "p",
                {
                    "style": {
                        "margin": "0 0 .5em 0",
                    },
                },
                "Game Mode: ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"gamemode": 0 if s["gamemode"] else 1}),
                    },
                    "Normal" if gamemode else "Borderless",
                ),
                " ",
            ),
            h(
                self.CheckBox,
                {
                    "stateKey": "showCoordinates",
                    "text": "Show coordinates",
                },
            ),
            h(
                "input",
                {
                    "style": {
                        "marginRight": ".5em",
                    },
                    "type": "button",
                    "value": "Copy Board",
                    "onClick": lambda: self._copy_move(document.getElementsByClassName("shudan-goban")[0]),
                },
            ),
            h(
                "div",
                {},
                h(
                    Goban,
                    {
                        "innerProps": {
                            "onContextMenu": lambda evt: evt.preventDefault(),
                        },
                        "vertexSize": vertexSize,
                        "animate": True,
                        "signMap": self.state.board.signMap,
                        "showCoordinates": showCoordinates,
                        "fuzzyStonePlacement": True,
                        "animateStonePlacement": True,
                        "onVertexMouseUp": self._place_stone(board, players),
                    },
                ),
            ),
        ),
    )

    def _place_stone(self, board, players):

        def callback(evt, vertex):
            if evt.button != 0:
                return

            players_hash = to_int(window.location.hash[2])
            game_mode = 1 if players_hash >= 10 else 0
            moves = window.location.hash[3:]
            index = len(moves) - 3
            player = to_int(moves[index]) - 10 if len(moves) else -1
            player += 1
            if player >= players:
                player = 0

            note, new_board, captures = self.move(board, player + 1, vertex, game_mode)
            if note:
                alert(note)
                return

            if captures:
                print(captures)

            self.setState({"board": new_board})
            window.location.hash += to_char(player + 10) + to_char(vertex[0]) + to_char(vertex[1])

        return callback

    def _copy_move(self, element):
        def do_copy(canvas):
            game_state = window.location.hash[1:]
            data = canvas.toDataURL()
            blob = Blob(
                [f'<img src="{data}"><hr><code>{game_state}</code>'],
                {"type":"text/html"},
            )
            navigator.clipboard.write([
                ClipboardItem({
                    "text/html": blob
                })
            ]).then(lambda: alert("Copied"))

        html2canvas(
            element,
            {
                "windowWidth": 500,
                "windowHeight": 500,
            },
        ).then(do_copy)





render(h(App), document.getElementById("root"))
