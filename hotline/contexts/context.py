from collections import deque
from types import MethodType
from ..ui.highlighter import PatternFactory
from ..config import Config, config_path


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


class Mode(object):
    '''A Mode object that handles the execution of an input string and
    holds syntax highlighting patterns and a list for autocompletion.

    :param handler: Function to handle input_str.
        Must take exactly one string argument to evaluate.
    :param name: Name of the mode e.g. "PY"
    :param completer_fn: A function that generations a completion list.
    :param completer_list: List of words to autocomplete.
    :param syntax: Name of syntax file in settings folder'''

    def __init__(self, handler, name=None, completer_fn=None,
                 completer_list=None, syntax=None):
        self.name = name
        self.completer_fn = completer_fn
        self.completer_list = completer_list if completer_list else []
        self.handler = handler
        self.patterns = []
        self.multiline_patterns = []
        self.syntax = syntax

    def set_syntax(self, syntax):
        '''Generates modes patterns and multline patterns from a syntax
        json file
        '''

        syntax_data = Config(config_path('{}.json'.format(syntax)))
        pattern_factory = PatternFactory(self.app.config['COLORS'])
        if syntax_data:
            syntax_name = syntax_data['name']
            for pattern_name, pattern in syntax_data['patterns'].iteritems():
                if pattern_name.startswith('multiline'):
                    self.multiline_patterns.append(
                        pattern_factory.create(
                            syntax_name, pattern_name, pattern))
                else:
                    self.patterns.append(
                        pattern_factory.create(
                            syntax_name, pattern_name, pattern))

    def setup(self):
        '''Called by HotLine instance when modes are cycled.'''

        if self.syntax and not self.patterns and not self.multiline_patterns:
            self.set_syntax(self.syntax)

        if self.completer_fn:
            self.completer_list = self.completer_fn()


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
                    name=v.name.upper(),
                    completer_fn=v.completer_fn,
                    completer_list=v.completer_list,
                    syntax=v.syntax
                    )

                modes.append(m)

        self._modes = deque(modes)

        return self


class Context(object):
    '''A context object holding all Mode objects.'''

    __metaclass__ = MetaContext

    def __init__(self, app):
        self.app = app
        for mode in self._modes:
            mode.app = app

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

    def get_mode(self, name):
        for mode in self._modes:
            if mode.name == name:
                return mode

    def set_mode(self, name):
        stop = self.mode
        while True:
            if self.mode.name == name:
                break

            self.next_mode()

            if stop == self.mode:
                break

    def prev_mode(self):
        self._modes.rotate(1)
        self.mode.setup()

    def next_mode(self):
        self._modes.rotate(-1)
        self.mode.setup()
