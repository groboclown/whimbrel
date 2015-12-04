"""
A Windows and ANSII coloring library.
"""

from sys import stdout

__ALL__ = ['out', 'outln']
VERSION = (1, 0, 0)

try:
    # Colors text in console mode application (win32).
    # Uses ctypes and Win32 methods SetConsoleTextAttribute and
    # GetConsoleScreenBufferInfo.
    #
    # source: https://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
    #
    # $Id: color_console.py 534 2009-05-10 04:00:59Z andre $
    from ctypes import windll, Structure, c_short, c_ushort, byref

    SHORT = c_short
    WORD = c_ushort


    class COORD(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("X", SHORT),
            ("Y", SHORT)
        ]


    class SMALL_RECT(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("Left", SHORT),
            ("Top", SHORT),
            ("Right", SHORT),
            ("Bottom", SHORT)
        ]


    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ("dwSize", COORD),
            ("dwCursorPosition", COORD),
            ("wAttributes", WORD),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", COORD)
        ]

    # winbase.h
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # wincon.h
    FOREGROUND_BLACK     = 0x0000
    FOREGROUND_BLUE      = 0x0001
    FOREGROUND_GREEN     = 0x0002
    FOREGROUND_CYAN      = 0x0003
    FOREGROUND_RED       = 0x0004
    FOREGROUND_MAGENTA   = 0x0005
    FOREGROUND_YELLOW    = 0x0006
    FOREGROUND_GREY      = 0x0007
    FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

    BACKGROUND_BLACK     = 0x0000
    BACKGROUND_BLUE      = 0x0010
    BACKGROUND_GREEN     = 0x0020
    BACKGROUND_CYAN      = 0x0030
    BACKGROUND_RED       = 0x0040
    BACKGROUND_MAGENTA   = 0x0050
    BACKGROUND_YELLOW    = 0x0060
    BACKGROUND_GREY      = 0x0070
    BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

    stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo


    def get_text_attr():
        """Returns the character attributes (colors) of the console screen
        buffer."""
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
        return csbi.wAttributes


    def set_text_attr(color):
        """Sets the character attributes (colors) of the console screen
        buffer. Color is a combination of foreground and background color,
        foreground and background intensity."""
        SetConsoleTextAttribute(stdout_handle, color)

    HIGHLIGHTS = {
        'on_grey': BACKGROUND_GREY,
        'on_red': BACKGROUND_RED,
        'on_green': BACKGROUND_GREEN,
        'on_yellow': BACKGROUND_YELLOW,
        'on_blue': BACKGROUND_BLUE,
        'on_magenta': BACKGROUND_MAGENTA,
        'on_cyan': BACKGROUND_CYAN,
        'on_black': BACKGROUND_BLACK
    }

    BOLD = FOREGROUND_INTENSITY

    COLORS = {
        'grey': FOREGROUND_GREY,
        'red': FOREGROUND_RED,
        'green': FOREGROUND_GREEN,
        'yellow': FOREGROUND_YELLOW,
        'blue': FOREGROUND_BLUE,
        'magenta': FOREGROUND_MAGENTA,
        'cyan': FOREGROUND_CYAN,
        'black': FOREGROUND_BLACK,
    }

    DEFAULT_COLORS = get_text_attr()
    DEFAULT_BACKGROUND = DEFAULT_COLORS & 0x00f0
    DEFAULT_FOREGROUND = DEFAULT_COLORS & 0x000f


    def set_color(val):
        assert isinstance(val, int)
        set_text_attr(val)


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

        return str(text), color_index


    def out(*text):
        if isinstance(text, str):
            set_default_colors()
            stdout.write(text)
            return
        for c in text:
            if isinstance(c, str):
                set_default_colors()
                stdout.write(c)
            else:
                assert isinstance(c, tuple) or isinstance(c, list)
                assert len(c) == 2
                assert isinstance(c[0], str)
                assert isinstance(c[1], int)
                set_color(c[1])
                stdout.write(c[0])
                set_default_colors()

except ImportError:
    # from the great "termcolor.py" library.
    # Copyright (c) 2008-2011 Volvox Development Team
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.
    #
    # Author: Konstantin Lepa <konstantin.lepa@gmail.com>
    import os

    ATTRIBUTES = dict(
            list(zip([
                'bold',
                'dark',
                '',
                'underline',
                'blink',
                '',
                'reverse',
                'concealed'
                ],
                list(range(1, 9))
                ))
            )
    del ATTRIBUTES['']

    HIGHLIGHTS = dict(
            list(zip([
                'on_black',
                'on_red',
                'on_green',
                'on_yellow',
                'on_blue',
                'on_magenta',
                'on_cyan',
                'on_grey'
                ],
                list(range(40, 48))
                ))
            )

    COLORS = dict(
            list(zip([
                'black',
                'red',
                'green',
                'yellow',
                'blue',
                'magenta',
                'cyan',
                'grey',
                ],
                list(range(30, 38))
                ))
            )

    RESET = '\033[0m'


    def colored(text, color=None, on_color=None, attrs=None):
        """Colorize text.

        Available text colors:
            red, green, yellow, blue, magenta, cyan, white.

        Available text highlights:
            on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

        Available attributes:
            bold, dark, underline, blink, reverse, concealed.

        Example:
            colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
            colored('Hello, World!', 'green')

        :param text: text to format in the requested color
        :param color: font color
        :param on_color: background color
        :param attrs: additional font attributes
        """
        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (COLORS[color], text)

            if on_color is not None:
                text = fmt_str % (HIGHLIGHTS[on_color], text)

            if attrs is not None:
                for attr in attrs:
                    text = fmt_str % (ATTRIBUTES[attr], text)

            text += RESET
        return text

    def out(*text):
        if isinstance(text, str):
            stdout.write(text)
        else:
            for c in text:
                stdout.write(str(c))
        stdout.flush()


def outln(*text):
    out(*text)
    stdout.write("\n")
