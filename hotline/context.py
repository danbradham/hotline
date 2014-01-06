import hotline


class Context(object):
    '''Holds state for a specific set of modes for HotLine.'''

    __shared = {}

    def __init__(self):
        self.__dict__ = self.__shared
        self._instance = self
        self.modes = self.__dict__.get("modes", {})
        self.show = self.__dict__.get("show", None)

    @classmethod
    def instance(cls):
        return cls.__shared.get("_instance", None)

    def add_mode(self, name, completion_list=None, syntax=None,
                 hotline_cls=hotline.HotLine, mode_cls=hotline.Mode):
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
            mode = mode_cls(name, handler,
                            completion_list=completion_list, syntax=syntax)
            self.modes[name] = mode
            hotline_cls.add_mode(mode)
            return handler
        return wrapped_handler

    def add_completer(self, name):
        '''Add a function that generates a completion list
        for auto-completion'''

        def wrapped_completer(completer):
            self.modes[name].completion_list_meth = completer
            return completer
        return wrapped_completer

    def set_show(self):
        '''Add a show function to context object.'''
        def wrapped(fn):
            self.show = fn
            return fn
        return wrapped
