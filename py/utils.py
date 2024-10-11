
__all__ = ("to_int", "to_char", "match_regex", "lappend", "min", "max", "copy_board", "RuntimeError")


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


def lappend(collection: List[T], value: T) -> None:
    """
    Append to list
    """
    collection.push(value)

# Exporting min and max directly
min = Math.min
max = Math.max


def copy_board(board_element) -> None:
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
        board_element,
        {
            "windowWidth": 500,
            "windowHeight": 500,
        },
    ).then(do_copy)


class RuntimeError(Exception):
    pass
