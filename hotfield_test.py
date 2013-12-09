import sip
import sys
for datatype in [
    'QString', 'QVariant', 'QUrl', 'QDate',
    'QDateTime', 'QTextStream', 'QTime']:
    sip.setapi(datatype, 2)
try:
    from PyQt4 import QtGui, QtCore
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
except ImportError, e:
    raise ImportError(e)

def format_text(r, g, b, a=255, style=''):
    color = QtGui.QColor(r, g, b, a)
    fmt = QtGui.QTextCharFormat()
    fmt.setForeground(color)
    if "bold" in style:
        fmt.setFontWeight(QtGui.QFont.Bold)
    if "italic" in style:
        fmt.setFontItalic(True)
    return fmt

HISTYLES = {
    'keywords': format_text(246, 38, 114),
    'operators': format_text(246, 38, 114),
    'delimiters': format_text(255, 255, 255),
    'defclass': format_text(102, 217, 239),
    'classid': format_text(255, 255, 255),
    'baseclasses': format_text(166, 226, 46),
    'defid': format_text(166, 226, 46),
    'string': format_text(230, 219, 116),
    'comment': format_text(117, 113, 94),
    'numbers': format_text(132, 129, 255),
    'parameters': format_text(253, 151, 31),
    }

PY = {
"keywords": [
    "and", "assert", "break", "continue", "del",
    "elif", "else", "except", "exec", "finally",
    "for", "from", "global", "if", "import", "in",
    "is", "lambda", "not", "or", "pass", "print",
    "raise", "return", "try", "while", "yield"],
"operators": [
    "\+", "-", "\*", "\*\*", "/", "//", "\%", "<<", ">>", "\&", "\|", "\^",
    "~", "<", ">", "<=", ">=", "==", "!=", "<>", "=", "\+=", "-=",
    "\*=", "/=", "//=", "\%=", "\&=", "\|=", "\^=", ">>=", "<<=", "\*\*="],
"delimiters": [
    "\(", "\)", "\[", "\]", "\{", "\}"],}


class PyHighlighter(QtGui.QSyntaxHighlighter):
    '''Python syntax highlighter.'''

    def __init__(self, parent):
        super(PyHighlighter, self).__init__(parent)

        self.multiline_rules = [
            (QtCore.QRegExp(r"'''"), 1, HISTYLES['string']),
            (QtCore.QRegExp(r'"""'), 2, HISTYLES['string']),]

        rules = [
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, HISTYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, HISTYLES['string']),
            # class identifier
            (r'\bclass\b\s*(\w+)', 1, HISTYLES['classid']),
            # def identifier
            (r'\bdef\b\s*(\w+)', 1, HISTYLES['defid']),
            # def and class keywords
            (r'\b(def|class)\b', 0, HISTYLES['defclass']),
            # From '#' until a newline
            (r'#[^\n]*', 0, HISTYLES['comment']),
            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, HISTYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, HISTYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, HISTYLES['numbers']),
            (r'\b(True|False)\b', 0, HISTYLES['numbers']),]

        for key, items in PY.iteritems():
            for item in items:
                rules.append((r'\b%s\b' % item, 0, HISTYLES[key]))

        self.rules = [(QtCore.QRegExp(exp), cap_index, fmt) 
            for exp, cap_index, fmt in rules]


    def highlightBlock(self, text):
        '''Formats all text from the highlighters parent.'''

        for expression, cap_index, format in self.rules:
            index = expression.indexIn(text)
            while index >= 0:
                cap = expression.cap(cap_index)
                match = expression.cap()
                length = len(cap)
                self.setFormat(index + match.find(cap), length, format)
                index = expression.indexIn(text, index + match.find(cap) + length)

        self.setCurrentBlockState(0)
        self.multlineBlock(text)


    def multlineBlock(self, text):
        '''Formats and maintains block state for multi-line comments'''

        last_state = self.previousBlockState()
        if last_state in (1, 2):
            end_expression, state, format = self.multiline_rules[last_state - 1]
            end_index = end_expression.indexIn(text)
            if end_index == -1:
                self.setFormat(0, len(text), format)
                self.setCurrentBlockState(last_state)
            else:
                self.setFormat(0, end_index + 3, format)
        else:
            for expression, state, format in self.multiline_rules:
                start_index = expression.indexIn(text)
                if start_index != -1:
                    end_index = expression.indexIn(text, start_index + 3)
                    if end_index == -1:
                        self.setFormat(start_index, len(text) - start_index, format)
                        self.setCurrentBlockState(state)
                    else:
                        self.setFormat(start_index, end_index + 3, format)


class HotField(QtGui.QTextEdit):
    '''A QTextEdit widget with history'''

    returnPressed = QtCore.Signal(str)
    modeToggled = QtCore.Signal()
    multilineToggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(HotField, self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(24)
        self.setFixedWidth(322)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(0)

        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setStyleHint(QtGui.QFont.Monospace)
        self.setFont(font)

        self.history = []
        self.history_index = 0
        self._multiline = False
        self.document().contentsChanged.connect(self.adjust_size)

    @property
    def multiline(self):
        return self._multiline

    @multiline.setter
    def multiline(self, value):
        self._multiline = value
        self.adjust_size()

    def adjust_size(self):
        doc_size = self.document().size()
        if doc_size.width() > 322:
            self.setFixedWidth(doc_size.width())
            self.parent().setMaximumWidth(doc_size.width())
        else:
            self.setFixedWidth(322)
            self.parent().setMaximumWidth(400)
        if self.multiline:
            self.setFixedHeight(doc_size.height())
            self.parent().setFixedHeight(doc_size.height()+4)
        else:
            self.setFixedHeight(24)
            self.parent().setFixedHeight(28)


    def keyPressEvent(self, event):
        key = event.key()
        mod = event.modifiers()
        text = event.text()
        plaintext = self.toPlainText()
        # Multiline Hotkey
        if (key == QtCore.Qt.Key_M and mod == QtCore.Qt.ControlModifier):
            self.multiline = False if self.multiline else True
            self.multilineToggled.emit(self.multiline)
        # Tab insertion for multline mode
        elif (key == QtCore.Qt.Key_Tab and
            self.multiline):
            self.insertPlainText('    ')
        # Mode Switching
        elif ((key == QtCore.Qt.Key_Tab and not self.multiline) or 
            (key == QtCore.Qt.Key_Tab and mod == QtCore.Qt.ControlModifier)):
            self.modeToggled.emit()
        # Execute Hotfield
        elif ((key == QtCore.Qt.Key_Enter and not self.multiline) or 
            (key == QtCore.Qt.Key_Enter and mod == QtCore.Qt.ControlModifier) or 
            (key == QtCore.Qt.Key_Return and not self.multiline) or 
            (key == QtCore.Qt.Key_Return and mod == QtCore.Qt.ControlModifier)):
            self.returnPressed.emit(plaintext)
            self.history.append(plaintext)
            self.history_index = len(self.history)
            self.clear()
        # Previous History
        elif ((key == QtCore.Qt.Key_Up and not self.multiline) or
            (key == QtCore.Qt.Key_Up and mod == QtCore.Qt.ControlModifier)):
            if text:
                self.history[self.history_index] = plaintext
            if self.history_index:
                self.history_index -= 1
            self.setText(self.history[self.history_index])
        # Next History
        elif ((key == QtCore.Qt.Key_Down and not self.multiline) or
            (key == QtCore.Qt.Key_Down and mod == QtCore.Qt.ControlModifier)):
            self.history_index += 1
            if self.history_index < len(self.history):
                self.setText(self.history[self.history_index])
            elif self.history_index == len(self.history):
                self.clear()
        else:
            super(HotField, self).keyPressEvent(event)

class HotLine(QtGui.QDialog):
    '''A popup dialog with a single QLineEdit(HotField) and several modes of input.'''

    style = '''QPushButton {
                    border:0;
                    background: none;}
                QPushButton:pressed {
                    border:0;
                    border-top: 1px solid rgb(15, 15, 15);
                    border-left: 1px solid rgb(15, 15, 15);
                    color: rgb(0, 35, 55);
                    background: rgb(115, 115, 115)}
                QPushButton:checked {
                    border:0;
                    border-top: 1px solid rgb(15, 15, 15);
                    border-left: 1px solid rgb(15, 15, 15);
                    color: rgb(0, 35, 55);
                    background: rgb(115, 115, 115)}
                QLineEdit {
                    background-color: none;
                    border: 0;
                    border-bottom: 1px solid rgb(42, 42, 42);
                    padding-left: 10px;
                    padding-right: 10px;
                    height: 20;}
                QLineEdit:focus {
                    outline: none;
                    background: none;
                    border: 0;
                    height: 20;}'''

    modes = ['PY', 'MEL', 'SEL', 'REN', 'NODE']

    def __init__(self, parent=None):
        super(HotLine, self).__init__(parent)

        # Create and connect ui widgets
        self.hotfield = HotField()
        self.hotfield.modeToggled.connect(self.toggle_modes)
        self.hotfield.returnPressed.connect(self.evaluate)
        # Add python highlighter to hotfield
        highlighter = PyHighlighter(self.hotfield)
        # Add popup completer to hotfield
        self.mode_button = QtGui.QPushButton('PY')
        self.mode_button.clicked.connect(self.toggle_modes)
        self.mode_button.setSizePolicy(
            QtGui.QSizePolicy.Fixed, 
            QtGui.QSizePolicy.Fixed)
        self.mode_button.setFixedWidth(50)
        self.mode_button.setFixedHeight(24)
        self.mode_button.setToolTip(
            "Switch HotLine Mode\n"
            "Tab in Single-line Mode\n"
            "CTRL + Tab in Multi-line Mode")
        self.multiline_button = QtGui.QPushButton('=')
        self.multiline_button.clicked.connect(self.toggle_multiline)
        self.multiline_button.setSizePolicy(
            QtGui.QSizePolicy.Fixed, 
            QtGui.QSizePolicy.Fixed)
        self.multiline_button.setFixedWidth(24)
        self.multiline_button.setFixedHeight(24)
        self.multiline_button.setCheckable(True)
        self.multiline_button.setToolTip(
            "Toggle Multi-line Mode\n"
            "CTRL + M\n"
            "Multi-Line mode modifies existing hotkeys to use CTRL modifier\n"
            "CTRL + Enter executes code\n"
            "CTRL + Up and Down flips through history")
        self.hotfield.multilineToggled.connect(self.multiline_button.setChecked)

        # Layout widgets and set stretch policies
        self.layout = QtGui.QGridLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.addWidget(self.mode_button, 0, 0)
        self.layout.addWidget(self.hotfield, 0, 1, 2, 1)
        self.layout.addWidget(self.multiline_button, 0, 2)
        self.setLayout(self.layout)

        # Set dialog flags and size policy
        self.setWindowFlags(
            QtCore.Qt.Popup|\
            QtCore.Qt.FramelessWindowHint|\
            QtCore.Qt.WindowStaysOnTopHint)
        self.setObjectName('HotLine')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(28)
        self.setStyleSheet(self.style)

        # Set initial mode to 0: "PY"
        self.mode = 0

    def toggle_multiline(self):
        self.hotfield.multiline = False if self.hotfield.multiline else True
        self.hotfield.setFocus()

    def toggle_modes(self):
        if self.mode == len(self.modes) - 1:
            self.mode = 0
        else:
            self.mode += 1

        self.mode_button.setText(self.modes[self.mode])
        self.hotfield.setFocus()

    def evaluate(self, text):
        print text

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.hotfield.setFocus()

    def exit(self):
        self.hotfield.clear()
        self.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    hl = HotLine()
    hl.enter()

    sys.exit(app.exec_())