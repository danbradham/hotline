'''
core.py
=======

Core elements of HotLine.
'''

from weakref import WeakSet
from .highlighter import PatternFactory
from .settings import Settings

PATTERN_FACTORY = PatternFactory()


class History(object):
    '''Maintains input history for HotLine'''
    _history = ['']
    _history_index = 0

    def add(self, input_str):
        if input_str:
            try:
                ind = self._history.index(input_str)
                if ind != 1:
                    self._history.insert(1, input_str)
            except ValueError:
                self._history.insert(1, input_str)
        self._history_index = 0

    def next(self):
        if self._history_index > 0:
            self._history_index -= 1
        return self._history[self._history_index]

    def prev(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
        return self._history[self._history_index]


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
        hotline.hotfield.set_completer_model(self.completer_list)
