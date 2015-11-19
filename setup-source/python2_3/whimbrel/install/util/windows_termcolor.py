"""
Layer on top of the windows_color to make it work just like ansii_termcolor.
"""

from . import windows_colors

HIGHLIGHTS = {
    'on_grey': windows_colors.BACKGROUND_GREY,
    'on_red': windows_colors.BACKGROUND_RED,
    'on_green': windows_colors.BACKGROUND_GREEN,
    'on_yellow': windows_colors.BACKGROUND_YELLOW,
    'on_blue': windows_colors.BACKGROUND_BLUE,
    'on_magenta': windows_colors.BACKGROUND_MAGENTA,
    'on_cyan': windows_colors.BACKGROUND_CYAN,
    'on_black': windows_colors.BACKGROUND_BLACK
}

BOLD = windows_colors.FOREGROUND_INTENSITY

COLORS = {
    'grey': windows_colors.FOREGROUND_GREY,
    'red': windows_colors.FOREGROUND_RED,
    'green': windows_colors.FOREGROUND_GREEN,
    'yellow': windows_colors.FOREGROUND_YELLOW,
    'blue': windows_colors.FOREGROUND_BLUE,
    'magenta': windows_colors.FOREGROUND_MAGENTA,
    'cyan': windows_colors.FOREGROUND_CYAN,
    'black': windows_colors.FOREGROUND_BLACK,
}

DEFAULT_COLORS = windows_colors.get_text_attr()
DEFAULT_BACKGROUND = DEFAULT_COLORS & 0x00f0
DEFAULT_FOREGROUND = DEFAULT_COLORS & 0x000f


def set_color(val):
    assert isinstance(val, int)
    windows_colors.set_text_attr(val)


def set_default_colors():
    set_color(DEFAULT_COLORS)


def colored(text, color=None, on_color=None, attrs=None):
    color_index = 0
    if color not in COLORS:
        color_index |= DEFAULT_FOREGROUND
    else:
        color_index |= COLORS[color]

    if on_color not in HIGHLIGHTS:
        color_index |= DEFAULT_BACKGROUND
    else:
        color_index |= HIGHLIGHTS[on_color]

    if attrs is not None:
        for attr in attrs:
            if attr == 'bold':
                color_index |= BOLD

    return (str(text), color_index)


