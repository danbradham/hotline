'''
hotfield.py
-----------
A QTextEdit widget that maintains input history.

 -  Keyboard shortcuts loaded from keys.settings
 -  Emits returnPressed, modeToggled, multilineToggled for use with
    a parent class.
'''

from collections import deque
from functools import partial
from .utils import load_keys

#Try PyQt then PySide imports
try:
    from PyQt4 import QtGui, QtCore
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
except ImportError:
    from PySide import QtGui, QtCore

KEYSET = load_keys()


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


class Completer(QtGui.QCompleter):

    def __init__(self, parent):
        self.completion_model = QtGui.QStringListModel([])
        super(Completer, self).__init__(self.completion_model, parent)
        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def set_model(self, completion_list):
        self.completion_model.setStringList(completion_list)


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
        self.completer = Completer(self)
        self.completer.activated.connect(self.insertCompletion)
        self._multiline = False
        self.document().contentsChanged.connect(self.adjust_size)

        #Setup Hotkeys
        key_methods = {
            "Toggle Multiline": self.key_multiline,
            "Toggle Modes": self.key_modes,
            "Execute": self.key_execute,
            "Previous in History": self.key_prev,
            "Next in History": self.key_next}

        for mode, key_shortcuts in KEYSET.iteritems():
            for name, seq in key_shortcuts.iteritems():
                if mode == 'standard':
                    meth = key_methods['name']
                else:
                    meth = partial(key_methods['name'], multiline_key=True)
                if mode == "standard":
                    shortcut = QtGui.QShortcut(
                        seq, self, context=QtCore.Qt.WidgetShortcut)
                    shortcut.activated.connect(meth)

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

    def insertCompletion(self, completion):
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[len(self.completer.completionPrefix()):])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QtGui.QTextEdit.focusInEvent(self, event)

    def key_multiline(self, multiline_key=False):
        self.multiline = False if self.multiline else True
        self.multilineToggled.emit(self.multiline)

    def key_modes(self, multiline_key=False):
        if multiline_key or not self.multiline:
            self.modeToggled.emit()

    def key_execute(self, multiline_key=False):
        if multiline_key or not self.multiline:
            plaintext = self.toPlainText()
            self.returnPressed.emit(plaintext)
            self.history.add(plaintext)
            self.clear()

    def key_prev(self, multiline_key=False):
        if multiline_key or not self.multiline:
            self.setText(self.history.prev())

    def key_next(self, multiline_key=False):
        if multiline_key or not self.multiline:
            self.setText(self.history.next())

    def keyPressEvent(self, event):
        completer_popup = self.completer.popup()
        is_completing = completer_popup.isVisible()
        is_multiline = self.multiline
        key = event.key()
        if is_completing:
            if key in (QtCore.Qt.Key_Enter,
                       QtCore.Qt.Key_Return,
                       QtCore.Qt.Key_Escape,
                       QtCore.Qt.Key_Tab,
                       QtCore.Qt.Key_Backtab):
                event.ignore()
                return

            completion_prefix = self.textUnderCursor()
            if len(completion_prefix) < 3:
                completer_popup.hide()
                return
            if completion_prefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(completion_prefix)
                completer_popup.setCurrentIndex(
                    self.completer.completionModle().index(0, 0))

            cr = self.cursorRect()
            cr.setWidth(
                completer_popup.sizeHintForColumn(0)
                + completer_popup.verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)

        else:
            # Tab insertion for multline mode
            if (key == QtCore.Qt.Key_Tab and is_multiline):
                self.insertPlainText('    ')
            else:
                super(HotField, self).keyPressEvent(event)
