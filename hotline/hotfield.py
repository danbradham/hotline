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
    _history = ['']
    _history_index = 0

    def add(self, input_str):
        if not input_str in self._history:
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


class HotField(QtGui.QTextEdit):
    '''A QTextEdit widget with history'''

    returnPressed = QtCore.Signal(str)
    next_mode = QtCore.Signal()
    prev_mode = QtCore.Signal()
    multilineToggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(HotField, self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(24)
        self.setFixedWidth(322)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.setFont(font)

        self.history = History()
        self.completer_model = QtGui.QStringListModel([])
        self.completer = QtGui.QCompleter(self.completer_model, self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)
        self._multiline = False
        self.document().contentsChanged.connect(self.adjust_size)

        #Setup Hotkeys
        self.key_methods = {
            "Toggle Multiline": self.key_multiline,
            "Next Mode": self.key_next_mode,
            "Prev Mode": self.key_prev_mode,
            "Execute": self.key_execute,
            "Previous in History": self.key_prev,
            "Next in History": self.key_next}

    @property
    def multiline(self):
        return self._multiline

    @multiline.setter
    def multiline(self, value):
        self._multiline = value
        self.adjust_size()

    def set_completer_model(self, completer_list):
        print completer_list
        self.completer_model.setStringList(completer_list)

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

    def key_multiline(self):
        self.multiline = False if self.multiline else True
        self.multilineToggled.emit(self.multiline)

    def key_next_mode(self):
        self.next_mode.emit()

    def key_prev_mode(self):
        self.prev_mode.emit()

    def key_execute(self):
        plaintext = self.toPlainText()
        self.returnPressed.emit(plaintext)
        self.history.add(plaintext)
        self.clear()

    def key_prev(self):
        self.setText(self.history.prev())

    def key_next(self):
        self.setText(self.history.next())

    def to_key_sequence(self, key, modifiers):
        key = QtGui.QKeySequence(key).toString()
        mods = []
        if modifiers & QtCore.Qt.ShiftModifier:
            mods.append("Shift+")
        if modifiers & QtCore.Qt.ControlModifier:
            mods.append("Ctrl+")
        if modifiers & QtCore.Qt.AltModifier:
            mods.append("Alt+")
        if modifiers & QtCore.Qt.MetaModifier:
            mods.append("Meta+")
        mod = ''.join(mods)
        if key == "Return":
            key = "Enter"
        if key == "Backtab":
            key = "Tab"
        return QtGui.QKeySequence.fromString(mod + key)

    def keyPressEvent(self, event):
        completer_popup = self.completer.popup()
        is_completing = completer_popup.isVisible()
        is_multiline = self.multiline
        key = event.key()
        mod = event.modifiers()
        key_seq = self.to_key_sequence(key, mod)

        #Singleline Hotkeys
        if not is_multiline and not is_completing:
            for name, seq in KEYSET['standard'].iteritems():
                if key_seq.matches(seq):
                    self.key_methods[name]()
                    return
        #Multiline Hotkeys
        if is_multiline and not is_completing:
            for name, seq in KEYSET['multiline'].iteritems():
                if key_seq.matches(seq):
                    self.key_methods[name]()
                    return

        #Tab Insertion as spaces
        if (
            key == QtCore.Qt.Key_Tab
            or key == QtCore.Qt.Key_Backtab
            and not is_completing
        ):
            self.insertPlainText('    ')
            return

        #Ignore event while completing
        if is_completing:
            if key in (
                QtCore.Qt.Key_Enter,
                QtCore.Qt.Key_Return,
                QtCore.Qt.Key_Escape,
                QtCore.Qt.Key_Tab,
                QtCore.Qt.Key_Backtab
            ):
                event.ignore()
                return

        #Insert keypress
        super(HotField, self).keyPressEvent(event)

        completion_prefix = self.textUnderCursor()
        if len(completion_prefix) < 3:
            completer_popup.hide()
            return
        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            completer_popup.setCurrentIndex(
                self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(
            completer_popup.sizeHintForColumn(0)
            + completer_popup.verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)
