from preact import h, render, Component
import __sabaki.go__board as GoBoard
from __sabaki.shudan import Goban

from .errors import InvalidMove
from .utils import to_int, to_char, match_regex, lappend, min, max, copy_board
from .base_rules import Move
from .rules import MultiColourRules, BorderLessRules
from .components import button, plus_minus_button

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
            "players": current_rule.player_meta["current"],
            "ruleIndex": rule_index,
        }

        self.CheckBox = create_two_way_checkbox(self)


    def render(self) -> None:
        """
        Build visual elements of the board on screen.
        """
        board = self.state["board"]
        players = self.state["players"]
        rule_index = self.state["ruleIndex"]
        board_size = self.state["boardSize"]
        vertexSize = self.state["vertexSize"]
        showCoordinates = self.state["showCoordinates"]
        fuzzyStonePlacement = self.state["fuzzyStonePlacement"]
        animateStonePlacement = self.state["animateStonePlacement"]

        rule = self.game_rules[rule_index]

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
                button(
                    "Game Mode",
                    rule.get_name(),
                    lambda evt: self.setState(
                        lambda s: {"ruleIndex": 0 if (s["ruleIndex"] + 1) >= len(self.game_rules) else s["ruleIndex"] + 1},
                    ),
                ),
                plus_minus_button(
                    "Players",
                    players,
                    lambda evt: self.setState(lambda s: {"players": rule.set_num_players(s["players"] - 1)}),
                    lambda evt: self.setState(lambda s: {"players": rule.player_meta["current"]}),
                    lambda evt: self.setState(lambda s: {"players": rule.set_num_players(s["players"] + 1)}),
                ),
                plus_minus_button(
                    "Board Size",
                    board_size,
                    lambda evt: self.setState(lambda s: {"boardSize": rule.set_board_size(s["boardSize"] - 1)}),
                    lambda evt: self.setState(lambda s: {"boardSize": rule.board_meta["current"]}),
                    lambda evt: self.setState(lambda s: {"boardSize": rule.set_board_size(s["boardSize"] + 1)}),
                ),
                plus_minus_button(
                    "Zoom",
                    "•",
                    lambda evt: self.setState(lambda s: {"vertexSize": max(s.vertexSize - 4, 4)}),
                    lambda evt: self.setState(lambda s: {"vertexSize": 24 }),
                    lambda evt: self.setState(lambda s: {"vertexSize": s.vertexSize + 4 }),
                ),
                h(
                    self.CheckBox,
                    {
                        "stateKey": "showCoordinates",
                        "text": "Show coordinates",
                    },
                ),
                button(
                    "Copy Board",
                    "COPY",
                    lambda evt: copy_board(document.getElementsByClassName("shudan-goban")[0] or {}),
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
                        "onVertexMouseUp": self._place_stone(board, rule),
                    },
                ),
            ),
        )

    def _place_stone(self, board, rule):

        def callback(evt, vertex):
            if evt.button != 0:
                return

            move = Move(rule.get_next_player(), vertex)

            try:
                rule.move(move)
            except InvalidMove as err:
                alert(str(err))
                return

            self.setState({"board": rule.board})
            window.location.hash = "#" + rule.save_game()

        return callback



render(h(App), document.getElementById("root"))
