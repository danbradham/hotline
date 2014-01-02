import os
import json
import sys
from collections import deque
from .highlighter import Highlighter

#Try PyQt then PySide imports
try:
    from PyQt4 import QtGui, QtCore
    import sip
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
except ImportError:
    from PySide import QtGui, QtCore


def rel_path(path):
    fullpath = os.path.join(os.path.dirname(__file__), os.path.abspath(path))
    if os.path.exists(fullpath):
        return fullpath
    return None


def load_settings(which, combine_user_defaults=True):
    defaults_path = rel_path("settings/defaults/" + which)
    user_path = rel_path("settings/user/" + which)

    try:
        with open(defaults) as f:
            defaults = json.load(f)
    except OSError:
        defaults = {}
    try:
        with open(user) as f:
            user = json.load(f)
    except OSError:
        user = {}

    if combine_user_defaults:
        settings = defaults.update(user)
    else:
        settings = user if user else defaults
    return settings


class History(object):
    _history = deque([''])

    def add(self, input_str):
        if not input_str in self._history:
            self._history.append(input_str)

    def next(self):
        self._history.rotate(-1)
        return self._history[0]

    def prev(self):
        self._history.rotate(1)
        return self._history[0]


def format_text(r, g, b, a=255, style=''):
    '''Create a QTextCharFormat for Highlighter.'''
    color = QtGui.QColor(r, g, b, a)
    fmt = QtGui.QTextCharFormat()
    fmt.setForeground(color)
    if "bold" in style:
        fmt.setFontWeight(QtGui.QFont.Bold)
    if "italic" in style:
        fmt.setFontItalic(True)
    return fmt


def create_pattern(name, pattern):
    if 'multiline' in name:
        start = QtGui.QRegexp(pattern['start'])
        end = QtGui.QRegexp(pattern['end'])
        captures = pattern['captures']
        format = format_text()
    else:
        match = QtGui.QRegexp(pattern['match'])
        captures = pattern['captures']
        format = format_text()

class Mode(object):

    def __init__(self, name, syntax=None):
        self.name = name
        self.load_syntax(syntax)

    def load_syntax(self, syntax):
        syntax_data = load_settings(syntax + '.syntax', combine_user_defaults=False)
        if syntax_data:
            syntax_name = syntax_data['name']
            for pattern_name, pattern in syntax_data['patterns'].iteritems():
                self.multiline_patterns.append()

    def setup(self):
        pass

    def handler(self, input_str):
        pass


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

        self.history = History()
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
        doc_height = self.document().size().height()
        doc_width = self.document().idealWidth()
        if doc_width > 322 and self.multiline:
            self.setFixedWidth(doc_width)
            self.parent().setFixedWidth(doc_width + 78)
        else:
            self.setFixedWidth(322)
            self.parent().setFixedWidth(400)
        if self.multiline:
            self.setFixedHeight(doc_height)
            self.parent().setFixedHeight(doc_height + 4)
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
            self.history.add(plaintext)
            self.clear()
        # Previous History
        elif ((key == QtCore.Qt.Key_Up and not self.multiline) or
            (key == QtCore.Qt.Key_Up and mod == QtCore.Qt.ControlModifier)):
            self.setText(self.history.prev())
        # Next History
        elif ((key == QtCore.Qt.Key_Down and not self.multiline) or
            (key == QtCore.Qt.Key_Down and mod == QtCore.Qt.ControlModifier)):
            self.setText(self.history.next())
        else:
            super(HotField, self).keyPressEvent(event)


class HotLine(QtGui.QDialog):
    '''A popup dialog with a single QLineEdit(HotField) and several modes of input.'''

    _modes = deque()

    def __init__(self, parent=None):
        super(HotLine, self).__init__(parent)

        # Create and connect ui widgets
        self.hotfield = HotField()
        self.hotfield.modeToggled.connect(self.next_mode)
        self.hotfield.returnPressed.connect(self.handle_input)
        # Add python highlighter to hotfield
        self.highlighter = Highlighter(self.hotfield)
        # Add popup completer to hotfield
        self.mode_button = QtGui.QPushButton()
        self.mode_button.clicked.connect(self.next_mode)
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
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(28)

        self.setStyleSheet(self.style)

    @property
    def mode(self):
        '''Returns current mode.'''
        if self._modes:
            return self._modes[0]
        return Mode('Null')

    def add_mode(self, mode):
        '''Mode registering decorator.'''
        self.mode_button.setText(self.mode.name)
        def decorated_handler(fn):
            #register mode and handler with HotLine
            self._modes.append(mode)
            return fn
        return decorated_handler

    def prev_mode(self):
        self._modes.rotate(1)
        self.mode_button.setText(self.mode.name)

    def next_mode(self):
        self._modes.rotate(1)
        self.mode_button.setText(self.mode.name)

    def handle_input(self, input_str):
        self.mode.handler(str(input_str))
        self.exit()

    def toggle_multiline(self):
        self.hotfield.multiline = False if self.hotfield.multiline else True
        self.hotfield.setFocus()

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.hotfield.setFocus()

    def exit(self):
        self.close()


if __name__ == "__main__":
    import signal
    app = QtGui.QApplication(sys.argv)

    hl = HotLine()
    hl.enter()

    def sigint_handler(*args):
        sys.exit(app.exec_())
    signal.signal(signal.SIGINT, sigint_handler)
    sys.exit(hl.exec_())