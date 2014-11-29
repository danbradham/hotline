from collections import deque
from types import MethodType
from ..ui.highlighter import PatternFactory
from ..settings import Settings, KeySettings
from ..history import History

PATTERN_FACTORY = PatternFactory()


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
        if syntax:
            self.set_syntax(syntax)

    def set_syntax(self, syntax):
        '''Generates modes patterns and multline patterns from a syntax
        json file
        '''

        syntax_data = Settings(syntax + '.syntax', combine_user_defaults=False)
        if syntax_data:
            syntax_name = syntax_data['name']
            for pattern_name, pattern in syntax_data['patterns'].iteritems():
                if pattern_name.startswith('multiline'):
                    self.multiline_patterns.append(
                        PATTERN_FACTORY.create(
                            syntax_name, pattern_name, pattern))
                else:
                    self.patterns.append(
                        PATTERN_FACTORY.create(
                            syntax_name, pattern_name, pattern))

    def setup(self, hotline):
        '''Called by HotLine instance when modes are cycled.'''

        if self.completer_fn:
            self.completer_list = self.completer_fn()
        hotline.mode_button.setText(self.name)
        hotline.highlighter.set_rules(self.patterns, self.multiline_patterns)
        hotline.editor.set_completer_model(self.completer_list)


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

    def __init__(self):
        self.hotline = None
        self.multiline = False
        self.autocomplete = False
        self.pinned = False
        self.history = History()
        self.keysettings = KeySettings()
        self.store = Settings("store.hotline-settings")

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
