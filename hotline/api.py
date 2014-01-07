'''
api.py
------

Exposes objects and functions to user.
'''

from .hotline import HotLine
from .mode import Mode
import sys

SHOW_FN = None


def add_mode(*args, **kwargs):
    '''Decorator to create and add a mode to HotLine. Has the same parameters
    as Mode.__init__.

    :param name: Name of the mode e.g. "PY"
    :param handler: Function to handle input_str.
        Must take exactly one string argument to evaluate.
    :param completion_fn: A function that generations a completion list.
    :param completion_list: List of words to autocomplete.
    :param syntax: Name of syntax file in settings folder'''

    def mode_wrapper(fn):
        mode = Mode(handler=fn, *args, **kwargs)
        HotLine.add_mode(mode)
        return mode
    return mode_wrapper


def show():
    """show hotline...

    Should instance HotLine and call inst.enter():
    try:
        hl.enter()
    except:
        hl = HotLine(parent=parent_window)
        hl.enter()
    """
    return SHOW_FN()


def set_show():
    '''Sets hotline.show to decorated fn.'''

    def show_wrapper(fn):
        setattr(sys.modules[__name__], "SHOW_FN", fn)
        return fn
    return show_wrapper
