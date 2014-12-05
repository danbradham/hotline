'''
highlighter
===========
'''

from PySide import QtCore, QtGui


class PatternFactory(object):
    '''Create patterns for Highlighter.'''

    def __init__(self, colors):
        self.colors = colors

    def format_text(self, r, g, b, a=255, style=''):
        '''Create a QTextCharFormat for Highlighter.'''
        color = QtGui.QColor(r, g, b, a)
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(color)
        if "bold" in style:
            fmt.setFontWeight(QtGui.QFont.Bold)
        if "italic" in style:
            fmt.setFontItalic(True)
        return fmt

    def create(self, name, pattern_name, pattern):
        '''Generates a pattern for use with a QSyntaxHighlighter
        Returns a tuple containing a regex pattern and text formatter
        '''

        try:
            color = self.colors[name][pattern_name]
        except KeyError:
            color = self.colors[name][pattern_name.split('.')[0]]
        except KeyError:
            color = self.colors['defaults']['input_color']

        fmt = self.format_text(*color)

        if 'multiline' in pattern_name:
            start = QtCore.QRegExp(pattern['start'])
            end = QtCore.QRegExp(pattern['end'])
            return start, end, fmt
        else:
            match = QtCore.QRegExp(pattern['match'])
            captures = pattern['captures']
            return match, captures, fmt


class Highlighter(QtGui.QSyntaxHighlighter):
    '''Python syntax highlighter.'''

    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.patterns = []
        self.multiline_patterns = []

    def set_rules(self, patterns, multiline_patterns):
        '''Set patterns and rules for highlighter

        :param patterns: Patterns to highlight.
            A list of tuples such as:
            [(pattern, captures, format)...]
            e.g. [(QtGui.QRegexp("\+"), 0, QtGui.QTextCharFormat())...]
        :param multiline_patterns: Multiline patterns to highlight.
            A list of tuples such as:
            [(start_pattern, end_pattern, format)...]
            e.g. [(QtGui.QRegexp("\\*"),
                   QtGui.QRegexp("*\\"),
                   QtGui.QTextCharFormat())...]'''

        self.patterns = patterns
        self.multiline_patterns = multiline_patterns

    def highlightBlock(self, text):
        '''Formats all text from the highlighters parent.'''

        if self.patterns:
            for match, captures, fmt in self.patterns:
                index = match.indexIn(text)
                while index >= 0:
                    c = match.cap(captures)
                    m = match.cap()
                    length = len(c)
                    self.setFormat(index + m.find(c), length, fmt)
                    index = match.indexIn(text, index + m.find(c) + length)

        if self.multiline_patterns:
            self.setCurrentBlockState(-1)
            self.multlineBlock(text)

    def multlineBlock(self, text):
        '''Formats and maintains block state for multiline comments'''

        last_state = self.previousBlockState()
        if last_state >= 0:
            start, end, fmt = self.multiline_patterns[last_state]
            end_index = end.indexIn(text)
            if end_index == -1:
                self.setFormat(0, len(text), fmt)
                self.setCurrentBlockState(last_state)
            else:
                self.setFormat(0, end_index + 3, fmt)
        else:
            for state, (start, end, fmt) in enumerate(self.multiline_patterns):
                start_index = start.indexIn(text)
                if start_index != -1:
                    end_index = end.indexIn(text, start_index + 3)
                    if end_index == -1:
                        self.setFormat(
                            start_index, len(text) - start_index, fmt)
                        self.setCurrentBlockState(state)
                    else:
                        self.setFormat(start_index, end_index + 3, fmt)
                    return
