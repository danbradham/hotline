'''
api.py
------

Exposes objects and functions to user.
'''

from .hotline import HotLine
from .mode import Mode
from .context import Context


def show():
    if not Context.instance():
        raise Exception("Import a context first!")
    else:
        Context.instance()
        return Context.instance().show()
