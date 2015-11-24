"""
Output reporting.
"""

from . import termcolor

DECORATION = {'color': 'grey', 'on_color': None, 'attrs': None}
ACTION = {'color': 'yellow', 'on_color': None, 'attrs': ['bold']}
DESCRIPTION = {'color': 'white', 'on_color': None, 'attrs': None}
STATUS = {'color': 'green', 'on_color': None, 'attrs': ['bold']}

MAX_ACTION_LENGTH = 8
MAX_SUMMARY_LENGTH = 60
MAX_RESULT_LENGTH = 10


def action(name, summary):
    """
    Display an action that has started.

    :param name:
    :param summary:
    :return:
    """
    left_padding = ""
    for i in range(0, (MAX_ACTION_LENGTH - min(MAX_ACTION_LENGTH, len(name)))):
        left_padding += " "
    right_padding = " "
    for i in range(0, (MAX_SUMMARY_LENGTH - min(MAX_SUMMARY_LENGTH, len(summary)))):
        right_padding += " "
    termcolor.out(
        termcolor.colored(left_padding + "[", **DECORATION),
        termcolor.colored(name[0:MAX_ACTION_LENGTH], **ACTION),
        termcolor.colored("] ", **DECORATION),
        termcolor.colored(summary[0:MAX_SUMMARY_LENGTH]),
        termcolor.colored(right_padding, **DECORATION))


def status(result):
    left_padding = ""
    for i in range(0, MAX_RESULT_LENGTH - min(MAX_RESULT_LENGTH, len(result))):
        left_padding += " "
    termcolor.outln(
        termcolor.colored(left_padding + "[", **DECORATION),
        termcolor.colored(result[0:MAX_RESULT_LENGTH], **STATUS),
        termcolor.colored("]", **DECORATION))


def waiting():
    termcolor.out(termcolor.colored(".", **DECORATION))


def processing():
    termcolor.out(termcolor.colored(".", **STATUS))


def completed():
    termcolor.outln(termcolor.colored(" completed", **STATUS))


def out(text):
    termcolor.out(text)


def outln(text):
    termcolor.out(text)
