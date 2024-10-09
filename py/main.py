#_ = __pragma__('js', '{}', 'import { h, render, Component } from "preact"')
#_ = __pragma__('js', '{}', 'import GoBoard from "@sabaki/go-board"')
#_ = __pragma__('js', '{}', 'import { Goban } from "@sabaki/shudan"')
#_ = __pragma__('js', '{}', 'import html2canvas from "html2canvas-pro"')
#_ = __pragma__('js', '{}', 'import "@sabaki/shudan/css/goban.css"')
#_ = __pragma__('js', '{}', 'import "../css/main.css"')

from preact import h, render, Component

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


def create_two_way_checkbox(component):
    pass


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
            window.location.hash = "#" + to_char(board_size) + to_char(max_players + 10 if game_mode else 0)

        print("HERE!", game_hash)


render(h(App), document.getElementById("root"))
