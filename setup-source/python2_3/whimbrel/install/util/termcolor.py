"""
Generic interface on top of ansii_termcolor.py and windows_termcolor.py
"""

from sys import stdout

try:
    from . import windows_termcolor
    from .windows_termcolor import colored

    def out(*text):
        if isinstance(text, str):
            windows_termcolor.set_default_colors()
            stdout.write(text)
            return
        for c in text:
            if isinstance(c, str):
                windows_termcolor.set_default_colors()
                stdout.write(c)
            else:
                assert isinstance(c, tuple) or isinstance(c, list)
                assert len(c) == 2
                assert isinstance(c[0], str)
                assert isinstance(c[1], int)
                windows_termcolor.set_color(c[1])
                stdout.write(c[0])
                windows_termcolor.set_default_colors()

    def outln(*text):
        out(*text)
        stdout.write("\n")

except ImportError:
    from .ansii_termcolor import colored

    def out(*text):
        if isinstance(text, str):
            stdout.write(text)
        else:
            for c in text:
                stdout.write(str(c))


def outln(*text):
    out(*text)
    stdout.write("\n")
