'''
api.py
------

Exposes objects and functions to user.
'''

from .hotline import HotLine
from .mode import Mode
import sys


def create_mode(completion_list=None, syntax=None):
    '''Decorator used to create a Mode object and add it to HotLine plus
    register it with the Context.

    :param name: Name of the mode e.g. "PY"
    :param completion_list: List of words to autocomplete.(optional)
    :param syntax: Name of syntax file in settings folder.(optional)
    :param hotline_cls: Class or Subclass of HotLine Object.(optional)
        Used for extending HotLine. Not necessary unless you're looking to
        change the default behaviour of HotLine.
    :param mode_cls: Class or Subclass of Mode object.(optional)
        Used for extending Mode. Not necessary unless you're looking to
        change the default behaviour of Modes.'''

    def wrapped_handler(handler):
        mode = Mode(handler.__name__, handler,
                    completion_list=completion_list, syntax=syntax)
        HotLine.add_mode(mode)
        setattr(sys.modules[__name__], handler.__name__, mode)
        return mode
    return wrapped_handler
