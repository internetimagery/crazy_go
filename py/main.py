from preact import h, render, Component
import __sabaki.go__board as GoBoard
from __sabaki.shudan import Goban
import html2canvas__pro as html2canvas

from .utils import to_int, to_char, match_regex, lappend, min, max, copy_board
from .rules import load_game_rule, MultiColourRules, BorderLessRules

# Bundle other assets
JS('import "@sabaki/shudan/css/goban.css"')
JS('import "../css/main.css"')



def create_two_way_checkbox(component):

    def callback(data):
        state_key = data["state_key"]
        text = data["text"]
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
        self.game_rules = [MultiColourRules(), BorderLessRules()]

        rule_index = 0
        current_rule = self.game_rules[rule_index]

        game_hash = window.location.hash[1:]
        if not game_hash:
            window.location.hash = "#" + current_rule.save_game()
        else:
            rule_id = to_int(game_hash[0])
            for i in range(len(self.game_rules)):
                if rule_id == self.game_rules[i].get_id():
                    current_rule = self.game_rules[i]
                    current_rule.load_game(game_hash[1:])
                    break

        self.state = {
            "board": current_rule.board,
            "boardSize": current_rule.board_meta["current"],
            "vertexSize": 24,
            "showCoordinates": False,
            "fuzzyStonePlacement": True,
            "animateStonePlacement": True,
            "isBusy": False,
            "players": current_rule.player_meta["max"],
            "gameRule": current_rule,
        }

        self.CheckBox = create_two_way_checkbox(self)


    def render(self) -> None:
        """
        Build visual elements of the board on screen.
        """
        board = self.state["board"]
        players = self.state["players"]
        rule = self.state["gameRule"]
        board_size = self.state["boardSize"]
        vertexSize = self.state["vertexSize"]
        showCoordinates = self.state["showCoordinates"]
        fuzzyStonePlacement = self.state["fuzzyStonePlacement"]
        animateStonePlacement = self.state["animateStonePlacement"]

        # Game has not started. GUI options still available...
        if not len(rule.moves):
            players = rule.set_num_players(players)
            board_size = rule.set_board_size(board_size)
            window.location.hash = "#" + rule.save_game()
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
                        "onClick": lambda evt: self.setState(lambda s: {"players": rule.set_num_players(s["players"] - 1)}),
                    },
                    "-"
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "title": "Reset",
                        "onClick": lambda evt: self.setState(lambda s: {"players": rule.player_meta["current"]}),
                    },
                    players,
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"players": rule.set_num_players(s["players"] + 1)}),
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
                        "onClick": lambda evt: self.setState(lambda s: {"boardSize": rule.set_board_size(s["boardSize"] - 1)}),
                    },
                    "-"
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "title": "Reset",
                        "onClick": lambda evt: self.setState(lambda s: {"boardSize": rule.board_meta["current"]}),
                    },
                    board_size,
                ),
                " ",
                h(
                    "button",
                    {
                        "type": "button",
                        "onClick": lambda evt: self.setState(lambda s: {"boardSize": rule.set_board_size(s["boardSize"] + 1)}),
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
                    rule.get_name(),
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
                    "onClick": lambda: copy_board(document.getElementsByClassName("shudan-goban")[0]),
                },
            ),
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



render(h(App), document.getElementById("root"))
