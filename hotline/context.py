from collections import deque
from types import MethodType
from .core import Mode


def add_mode(name=None, completer_fn=None, completer_list=None, syntax=None):
    '''Class method decorator for objects of MetaContext type.
    Has the same signature as Mode.__init__.

    :param name: Name of the mode e.g. "PY"
    :param handler: Function to handle input_str.
        Must take exactly one string argument to evaluate.
    :param completion_fn: A function that generations a completion list.
    :param completion_list: List of words to autocomplete.
    :param syntax: Name of syntax file in settings folder'''

    def mode_wrapper(fn):

        fn.is_handler = True
        fn.name = name
        fn.completer_fn = completer_fn
        fn.completer_list = completer_list
        fn.syntax = syntax

        return fn

    return mode_wrapper


class MetaContext(type):
    '''Metaclass for Context objects. Each class method decorated with the
    add_mode decorator is wrapped in a Mode object and added to _modes class
    attribute.'''

    def __new__(cls, name, bases, attrs):

        self = super(MetaContext, cls).__new__(cls, name, bases, attrs)

        modes = []
        for k, v in self.__dict__.items():
            is_handler = getattr(v, "is_handler", False)
            if is_handler:
                m = Mode(
                    handler=MethodType(v, self),
                    name=k.upper() if len(k) < 4 else k[:4].upper(),
                    completer_fn=v.completer_fn,
                    completer_list=v.completer_list,
                    syntax=v.syntax
                    )

                modes.append(m)

        setattr(self, "_modes", deque(modes))

        return self


class Context(object):
    '''A context object holding all Mode objects.'''

    __metaclass__ = MetaContext

    def __init__(self):
        self.hotline = None

    @property
    def modes(self):
        return self._modes

    @property
    def mode(self):
        '''Returns current mode.'''
        return self._modes[0]

    @property
    def run(self):
        '''Returns current handler'''
        return self.mode.handler

    def prev_mode(self):
        self._modes.rotate(1)
        self.mode.setup(self.hotline)

    def next_mode(self):
        self._modes.rotate(-1)
        self.mode.setup(self.hotline)

    def show(self, HotLineCls):
        '''Overwrite with any special behavior necessary.'''
        if not self.hotline:
            self.hotline = HotLineCls()
        self.hotline.enter()
