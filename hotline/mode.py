'''
mode.py
-----------
A Mode object that handles the execution of an input string.

 -  Holds Syntax highlighting patterns and autocompletion list
'''
from .utils import load_settings, PatternFactory

PATTERN_FACTORY = PatternFactory()


class Mode(object):
    '''A Mode object that handles the execution of an input string and
    holds syntax highlighting patterns and a list for autocompletion.

    :param name: Name of the mode e.g. "PY"
    :param handler: Function to handle input_str.
        Must take exactly one string argument to evaluate.
    :param completion_list_meth: A function that generations a completion list.
    :param completion_list: List of words to autocomplete.
    :param syntax: Name of syntax file in settings folder'''

    def __init__(self, name, handler, completer_fn=None,
                 completion_list=None, syntax=None):
        self.name = name
        self.completer_fn = completer_fn
        self.completion_list = completion_list if completion_list else []
        self.__call__ = handler
        if syntax:
            self.set_syntax(syntax)

    def __call__(self, input_str):
        pass

    def completer(self, fn):
        '''Add a function that generates a completion list
        for auto-completion'''
        self.completer_fn = fn
        return fn

    def set_syntax(self, syntax):
        '''Generates modes patterns and multline patterns from a syntax
        json file
        '''
        self.patterns = []
        self.multiline_patterns = []

        syntax_data = load_settings(
            syntax + '.syntax',
            combine_user_defaults=False)
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

    def setup(self, parent):
        '''Called by HotLine instance when modes are cycled.'''
        if self.completer_fn:
            self.completion_list = self.completer_fn()
        parent.mode_button.setText(self.mode.name)
        parent.highlighter.set_rules(self.patterns, self.multiline_patterns)
        parent.hotfield.completer.set_model(self.completion_list)

