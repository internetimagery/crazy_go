from preact import h

__all__ = ("button", "plus_minus_button")


def button(label, value, press_func):
    return h(
        "p",
        {
            "style": {
                "margin": "0 0 .5em 0",
            },
        },
        label + ": ",
        h(
            "button",
            {
                "type": "button",
                "onClick": press_func,
            },
            value,
        ),
        " ",
    )


def plus_minus_button(label, state, minus_func, reset_func, plus_func):
    return h(
        "p",
        {
            "style": {
                "margin": "0 0 .5em 0",
            },
        },
        label + ": ",
        h(
            "button",
            {
                "type": "button",
                "onClick": minus_func,
            },
            "-"
        ),
        " ",
        h(
            "button",
            {
                "type": "button",
                "title": "Reset",
                "onClick": reset_func,
            },
            state,
        ),
        " ",
        h(
            "button",
            {
                "type": "button",
                "onClick": plus_func,
            },
            "+"
        ),
    )
