# -*- coding: utf-8 -*-
from collections import deque
import sys
import time
from Qt import QtWidgets, QtCore, QtGui
from contextlib import contextmanager
from .utils import keys_to_string
from .anim import *


class ActiveScreen(object):

    @staticmethod
    def active():
        desktop = QtWidgets.QApplication.instance().desktop()
        active = desktop.screenNumber(desktop.cursor().pos())
        return desktop.screenGeometry(active)

    @classmethod
    def top(cls):
        rect = cls.active()
        return int(rect.width() * 0.5), 0

    @classmethod
    def center(cls):
        return cls.active().center().toTuple()


class CommandList(QtWidgets.QListWidget):
    # TODO add support for icons

    def __init__(self, items, lineedit, parent=None):
        super(CommandList, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setMinimumSize(1, 1)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored
        )
        self.parent = parent
        self.lineedit = lineedit
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.itemSelectionChanged.connect(self.parent.activateWindow)
        self.items = items

    @property
    def items(self):
        return (self.item(i) for i in xrange(self.count()))

    @items.setter
    def items(self, value):
        self.clear()
        self.addItems(value)
        self.setGeometry(self._get_geometry())

    def visible_count(self):
        count = 0
        for item in self.items:
            if not item.isHidden():
                count += 1
        return count

    def select_next(self):
        row = self.currentRow()
        while True:
            row += 1
            if row > self.count() - 1:
                return
            if self.item(row).isHidden():
                continue
            self.setCurrentRow(row)
            return

    def select_prev(self):
        row = self.currentRow()
        while True:
            row -= 1
            if row < 0:
                self.setCurrentRow(row)
                return
            if self.item(row).isHidden():
                continue
            self.setCurrentRow(row)
            return

    def is_match(self, letters, item):

        letters = deque(letters.lower())
        l = letters.popleft()
        for char in item.lower():
            if char == l:
                try:
                    l = letters.popleft()
                except IndexError:
                    return True
        return False

    def filter(self, text):

        text = text.strip(' ')
        if not text:
            for item in self.items:
                item.setHidden(False)
            self.setCurrentRow(-1)
        else:
            best_match = -1
            for i, item in enumerate(self.items):
                match = self.is_match(text, item.text())
                if match and best_match < 0:
                    best_match = i
                elif text == item.text():
                    best_match = i
                item.setHidden(not match)
            self.setCurrentRow(best_match)

        self.setGeometry(self._get_geometry())

    def _get_geometry(self):
        visible_count = self.visible_count()
        if not visible_count:
            return QtCore.QRect(-1, -1, 0, 0)

        r = self.parent.rect()
        pos = self.parent.mapToGlobal(QtCore.QPoint(r.right(), r.bottom()))
        width = self.lineedit.width()
        left = pos.x() - width + 1
        top = pos.y() + 1
        height = 72 * min(visible_count, 5)
        return QtCore.QRect(left, top, width, height)

    def show(self):
        self.setCurrentRow(-1)
        super(CommandList, self).show()


class Console(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Console, self).__init__(parent)
        self.setWindowTitle('Hotline Console')
        self.parent = parent
        self.output = QtWidgets.QTextEdit(self)
        self.output.setReadOnly(True)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.hide()
        if event.spontaneous():
            event.accept()
        else:
            event.ignore()

    def write(self, message):
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.insertPlainText(message)
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.repaint()

    def show(self):
        r = self.parent.rect()
        pos = self.parent.mapToGlobal(QtCore.QPoint(r.right(), r.bottom()))
        width = r.width()
        left = pos.x() - width + 1
        top = pos.y() + 72 * 6
        height = 960
        self.setGeometry(QtCore.QRect(left, top, width, height))
        super(Console, self).show()
        self.parent.activate()


class InputField(QtWidgets.QLineEdit):

    text_changed = QtCore.Signal(str)

    def __init__(self, placeholder=None, parent=None):
        super(InputField, self).__init__(parent=parent)
        self.setProperty('property', bool(placeholder))
        self.refresh_style()
        self._placeholder = placeholder
        if self._placeholder:
            self.setText(self._placeholder)
            self.setCursorPosition(0)
        self.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.textEdited.connect(self.onTextEdited)
        # self.textChanged.connect(self.onTextChanged)

    def refresh_style(self):
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        _old = self._placeholder
        self._placeholder = value
        if self._text() == _old and value:
            self.setText(value)
            self.setCursorPosition(0)

    def clear(self):
        super(InputField, self).clear()

        if self.placeholder:
            self.setText(self.placeholder)
            self.setCursorPosition(0)

        self.setProperty('placeholder', bool(self.placeholder))
        self.refresh_style()

    def _text(self):
        return super(InputField, self).text()

    def text(self):
        value = self._text()
        if value == self.placeholder:
            value = ''
        return value

    def onCursorPositionChanged(self, old_pos, new_pos):
        if self._text() == self.placeholder:
            self.setCursorPosition(0)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter and self._text() == self.placeholder:
            event.accept()
            return

        super(InputField, self).keyPressEvent(event)

    # def onTextChanged(self, text):
    #     self.text_changed.emit(self.text())

    def onTextEdited(self, text):
        if self.placeholder and self.placeholder in text:
            text = text.split(self.placeholder)[0]
            self.setText(text)
            self.setProperty('placeholder', False)
            self.refresh_style()


class Dialog(QtWidgets.QWidget):

    accept = QtCore.Signal()
    reject = QtCore.Signal()
    focus_out = QtCore.Signal()

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.width = 960
        self.height = 96
        self.pinned = False
        self.accepted = False
        self.rejected = False
        self._animation = 'slide'
        self._position = 'center'

        self.setWindowTitle('Hotline')
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored
        )
        self.setMinimumSize(1, 1)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.input_field = InputField(parent=self)
        self.input_field.setFixedHeight(96)
        self.input_field.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed,
        )
        self.commandlist = CommandList([], self.input_field, self)
        self.commandlist.itemClicked.connect(self.accept)
        self.input_field.textChanged.connect(self.commandlist.filter)
        def focusOutEvent(event):
            if self.pinned:
                event.ignore()
                return
            self.rejected = True
            self.focus_out.emit()
            event.accept()
        self.input_field.focusOutEvent = focusOutEvent
        self.input_field.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.console = Console(self)

        self.hk_up = QtWidgets.QShortcut(self)
        self.hk_up.setKey('Up')
        self.hk_up.activated.connect(self.commandlist.select_prev)
        self.hk_dn = QtWidgets.QShortcut(self)
        self.hk_dn.setKey('Down')
        self.hk_dn.activated.connect(self.commandlist.select_next)
        self.hk_return = QtWidgets.QShortcut(self)
        self.hk_return.setKey('Return')
        self.hk_return.activated.connect(self.on_accept)
        self.hk_esc = QtWidgets.QShortcut(self)
        self.hk_esc.setKey('Esc')
        self.hk_esc.activated.connect(self.on_reject)
        self.hk_ctrl_p = QtWidgets.QShortcut(self)
        self.hk_ctrl_p.setKey('Ctrl+P')
        self.hk_ctrl_p.activated.connect(self.toggle_pin)
        self.focus_out.connect(self.hide)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.input_field)
        self.setLayout(self.layout)

    def on_accept(self):
        self.accepted = True
        self.rejected = False
        self.accept.emit()

    def on_reject(self):
        self.accepted = False
        self.rejected = True
        self.reject.emit()

    def toggle_pin(self):
        self.pinned = not self.pinned

    @contextmanager
    def pin(self):
        '''Context manager used to suppress focus out events'''

        if self.pinned:
            try:
                yield
            finally:
                pass

        else:
            self.pinned = True
            try:
                yield
            finally:
                self.pinned = False

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, value):
        if value not in ('slide', 'fade'):
            raise ValueError('animation must be "slide" or "fade" not ' + str(value))

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if value not in ('center', 'top'):
            raise ValueError('position must be "center" or "top" not ' + str(value))

    def get_result(self):
        item = self.commandlist.selectedItems()
        if item:
            return item[0].text()
        return self.input_field.text()

    def await_result(self):

        app = QtWidgets.QApplication.instance()
        while True:
            time.sleep(0.01)
            app.processEvents()
            if self.accepted or self.rejected:
                break

        if self.accepted:
            return self.get_result()
        if self.rejected:
            return

    def exec_(self):
        self.show()
        return super(Dialog, self).exec_()

    def hide(self):
        if self.pinned:
            return
        self._hide()

    def _hide(self):
        self.commandlist.hide()
        super(Dialog, self).hide()

    def get_position(self):
        if self.position == 'top':
            pos = ActiveScreen.top()
            return pos[0] - self.width * 0.5, pos[1]

        pos = ActiveScreen.center()
        return pos[0] - self.width * 0.5, pos[1] - self.height * 0.5

    def slide_group(self, pos):
        start = (pos[0], pos[1], self.width, 0)
        end = (pos[0], pos[1], self.width, self.height)
        self.setGeometry(*start)
        group = parallel_group(
            self,
            fade_in(self, duration=50),
            resize(
                self,
                start_value=start,
                end_value=end,
            ),
        )
        group.stateChanged.connect(self.animation_handler)

        crect = self.commandlist._get_geometry()
        self.commandlist.setGeometry(crect)
        group.addAnimation(fade_in(self.commandlist, duration=50))
        if crect.height() <= 1:
            return group

        start = (crect.left(), start[1], crect.width(), 0)
        self.commandlist.setGeometry(*start)
        end = (crect.left(), end[1] + self.height, crect.width(), crect.height())
        group.addAnimation(
            resize(
                self.commandlist,
                start_value=start,
                end_value=end,
            )
        )
        return group

    def fade_in_group(self, pos):
        self.setGeometry(pos[0], pos[1], self.width, self.height)
        self.commandlist.setGeometry(self.commandlist._get_geometry())
        group = parallel_group(self, fade_in(self), fade_in(self.commandlist))
        group.stateChanged.connect(self.animation_handler)
        return group

    def animation_handler(self, *state_change):
        state = QtCore.QAnimationGroup
        self.pinned = {
            (state.Stopped, state.Running): False,  # Stopped
            (state.Running, state.Stopped): True,  # Started
            (state.Running, state.Paused): True,  # Unpaused
            (state.Paused, state.Running): False,  # Paused
        }[state_change]

    def activate(self):
        self.raise_()
        self.activateWindow()
        self.input_field.setFocus()

    def closeEvent(self, event):
        self.on_reject()
        self._hide()
        event.accept()

    def _show(self):
        self.accepted = False
        self.rejected = False
        with self.pin():
            super(Dialog, self).show()
            self.commandlist.show()

    def show(self, anim_typ=None, lefttop=None):
        self.setGeometry(QtCore.QRect(0, 0, 960, 1))
        self._show()
        lefttop = lefttop or self.get_position()
        anim_typ = anim_typ or self.animation
        group = getattr(self, anim_typ + '_group')(lefttop)
        group.start(group.DeleteWhenStopped)
        self.activate()


class ModesDialog(Dialog):

    def __init__(self, parent=None):
        super(ModesDialog, self).__init__(parent)

        self.mode_button = QtWidgets.QPushButton(self)
        self.mode_button.setFixedHeight(96)
        self.mode_button.setMinimumWidth(96)
        self.mode_button.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed,
        )
        self.mode_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.layout.insertWidget(0, self.mode_button)

        self.hk_tab = QtWidgets.QShortcut(self)
        self.hk_tab.setKey('Tab')
        self.hk_shift_tab = QtWidgets.QShortcut(self)
        self.hk_shift_tab.setKey('Shift+Tab')
