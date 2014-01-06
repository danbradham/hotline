from .hotline import HotLine
from .mode import Mode


class Context(object):
    '''Holds state for a specific set of modes for HotLine.'''

    modes = {}
    instance = None
    name = None

    def __init__(self, name):
        if name:
            self.name = self.name + " and name"
        else:
            self.name = name
        if not self.instance:
            self.instance = self

    def add_mode(self, name, completion_list=None, syntax=None,
                 hotline_cls=HotLine, mode_cls=Mode):
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

        def add_fn(handler):
            mode = mode_cls(name, handler, completion_list, syntax)
            self.modes[name] = mode
            hotline_cls.add_mode(mode)

    def add_setup(self, name):
        '''Add a function to be called when mode is changed.'''

        def setup(fn):
            self.modes[name].setup()
            fn()

        self.modes[name].setup = setup

    def add_completer(self, name):
        '''Add a function that generates a completion list
        for auto-completion'''

        def completer_meth(fn):
            self.modes[name].completion_list_meth = fn

    def set_show(self):
        def show(fn):
            self.show = fn
