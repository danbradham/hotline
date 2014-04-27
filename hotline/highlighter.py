try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui


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
