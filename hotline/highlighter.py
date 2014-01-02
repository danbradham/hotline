try:
    from PyQt4 import QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore


class Highlighter(QtGui.QSyntaxHighlighter):
    '''Python syntax highlighter.'''

    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)

    def set_rules(self, patterns, multiline_patterns=None):
        '''Set patterns and rules for highlighter

        :param patterns: Patterns to highlight. A list of tuples.
            [(pattern, captures, format)...]
            e.g. [(QtGui.QRegexp("\+"), 0, QtGui.QTextCharFormat())...]
        :param multiline_patterns: Multiline patterns to highlight. A list of tuples.
            [(start_pattern, end_pattern, format)...]
            e.g. [(QtGui.QRegexp("\\*"), QtGui.QRegexp("*\\"), QtGui.QTextCharFormat())...]'''

        self.patterns = patterns
        self.multiline_patterns = multiline_patterns

    def highlightBlock(self, text):
        '''Formats all text from the highlighters parent.'''

        for match, captures, format in self.patterns:
            index = match.indexIn(text)
            while index >= 0:
                c = match.cap(captures)
                m = match.cap()
                length = len(c)
                self.setFormat(index + m.find(c), length, format)
                index = match.indexIn(text, index + m.find(c) + length)

        self.setCurrentBlockState(-1)
        self.multlineBlock(text)

    def multlineBlock(self, text):
        '''Formats and maintains block state for multiline comments'''

        last_state = self.previousBlockState()
        if last_state >= 0:
            start, end, format = self.multiline_rules[last_state]
            end_index = end.indexIn(text)
            if end_index == -1:
                self.setFormat(0, len(text), format)
                self.setCurrentBlockState(last_state)
            else:
                self.setFormat(0, end_index + 3, format)
        else:
            for start, end, format in self.multiline_rules:
                start_index = start.indexIn(text)
                if start_index != -1:
                    end_index = end.indexIn(text, start_index + 3)
                    if end_index == -1:
                        self.setFormat(start_index, len(text) - start_index, format)
                        self.setCurrentBlockState(state)
                    else:
                        self.setFormat(start_index, end_index + 3, format)