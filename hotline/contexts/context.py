import os
import collections
import types
from ..config import LOADERS, SUPPORTED_TYPES


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

    def set_syntax(self, pattern_factory, syntax_data):
        '''Generates modes patterns and multline patterns from a syntax
        json file
        '''

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

    def setup(self, app):
        '''Called by HotLine instance when modes are cycled.'''
        from ..ui.highlighter import PatternFactory

        if self.syntax and not self.patterns and not self.multiline_patterns:
            for typ in SUPPORTED_TYPES:
                syntax_filename = '{}.{}'.format(self.syntax, typ)
                syntax_path = app.config.relative_path(syntax_filename)
                if os.path.exists(syntax_path):
                    syntax_data = LOADERS[typ](syntax_path)

            pattern_factory = PatternFactory(app.config['COLORS'])
            self.set_syntax(pattern_factory, syntax_data)

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
                    handler=types.MethodType(v, self),
                    name=v.name.upper(),
                    completer_fn=v.completer_fn,
                    completer_list=v.completer_list,
                    syntax=v.syntax
                    )

                modes.append(m)

        self._modes = collections.deque(modes)

        return self


class Context(object):
    '''A context object holding all Mode objects.'''

    __metaclass__ = MetaContext

    def __init__(self, app):
        self.app = app

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
        self.mode.setup(self.app)

    def next_mode(self):
        self._modes.rotate(-1)
        self.mode.setup(self.app)
