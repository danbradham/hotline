# -*- coding: utf-8 -*-
from collections import deque
import sys
import time
from Qt import QtWidgets, QtCore, QtGui
from contextlib import contextmanager
from .utils import event_loop
from .anim import *


def get_unit(style):
    label = QtWidgets.QLabel('UNIT')
    label.setStyleSheet(style)
    return label.sizeHint().height()


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
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
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
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.parent = parent
        self.output = QtWidgets.QTextEdit(self)
        self.output.setReadOnly(True)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def write(self, message):
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.insertPlainText(message)
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.repaint()

    def show(self):
        if self.isVisible():
            return
        r = self.parent.rect()
        pos = self.parent.mapToGlobal(QtCore.QPoint(r.right(), r.bottom()))
        width = r.width()
        left = pos.x() - width + 1
        top = pos.y() + 72 * 6
        height = width
        self.setGeometry(QtCore.QRect(left, top, width, height))
        super(Console, self).show()


class InputField(QtWidgets.QLineEdit):

    focusOut = QtCore.Signal(object)

    def __init__(self, placeholder=None, parent=None):
        super(InputField, self).__init__(parent=parent)
        self.parent = parent
        self.setProperty('property', bool(placeholder))
        self.refresh_style()
        self._placeholder = placeholder
        if self._placeholder:
            self.setText(self._placeholder)
            self.setCursorPosition(0)
        self.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.textEdited.connect(self.onTextEdited)

    def focusOutEvent(self, event):
        event.accept()
        self.focusOut.emit(event)

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

    @property
    def is_placeholder(self):
        return self._text() == self._placeholder

    def clear(self):
        super(InputField, self).clear()

        if self._placeholder:
            self.setText(self.placeholder)
            self.setCursorPosition(0)

        self.setProperty('placeholder', bool(self.placeholder))
        self.refresh_style()

    def _text(self):
        return super(InputField, self).text()

    def text(self):
        value = self._text()
        if value == self._placeholder:
            value = ''
        return value

    def setText(self, text):
        super(InputField, self).setText(text)
        self.setProperty('placeholder', text == self._placeholder)
        self.refresh_style()

    def onCursorPositionChanged(self, old_pos, new_pos):
        if self.is_placeholder:
            self.setCursorPosition(0)

    def keyPressEvent(self, event):
        enter_pressed = event.key() == QtCore.Qt.Key_Enter
        if enter_pressed and self.is_placeholder:
            event.accept()
            return
        super(InputField, self).keyPressEvent(event)

    def onTextEdited(self, text):
        if self._placeholder and self._placeholder in text:
            text = text.split(self.placeholder)[0]
            self.setText(text)
            self.setProperty('placeholder', False)
            self.refresh_style()


class Dialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.parent = parent
        self._set_sizes()
        self._alt_f4_pressed = False
        self._animation = 'slide'
        self._position = 'center'
        self.pinned = False

        self.setWindowTitle('Hotline')
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored
        )
        self.setMinimumSize(1, 1)

        self.mode_button = QtWidgets.QPushButton(self)
        self.mode_button.setFixedHeight(self._height)
        self.mode_button.setMinimumWidth(self._height)
        self.mode_button.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed,
        )
        self.mode_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mode_button.hide()

        self.input_field = InputField(parent=self)
        self.input_field.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.commandlist = CommandList([], self.input_field, self)
        self.commandlist.itemClicked.connect(self.accept)
        self.input_field.textChanged.connect(self.commandlist.filter)
        self.input_field.focusOut.connect(self.reject)

        self.console = Console(self)

        self.hk_up = QtWidgets.QShortcut(self)
        self.hk_up.setKey('Up')
        self.hk_up.activated.connect(self.commandlist.select_prev)
        self.hk_dn = QtWidgets.QShortcut(self)
        self.hk_dn.setKey('Down')
        self.hk_dn.activated.connect(self.commandlist.select_next)
        self.hk_return = QtWidgets.QShortcut(self)
        self.hk_return.setKey('Return')
        self.hk_return.activated.connect(self.accept)
        self.hk_esc = QtWidgets.QShortcut(self)
        self.hk_esc.setKey('Esc')
        self.hk_esc.activated.connect(self.reject)
        self.hk_ctrl_p = QtWidgets.QShortcut(self)
        self.hk_ctrl_p.setKey('Ctrl+P')
        self.hk_ctrl_p.activated.connect(self.toggle_pin)
        self.hk_ctrl_up = QtWidgets.QShortcut(self)
        self.hk_ctrl_up.setKey('Ctrl+Up')
        self.hk_ctrl_dn = QtWidgets.QShortcut(self)
        self.hk_ctrl_dn.setKey('Ctrl+Down')
        self.hk_alt_f4 = QtWidgets.QShortcut(self)
        self.hk_tab = QtWidgets.QShortcut(self)
        self.hk_tab.setKey('Tab')
        self.hk_shift_tab = QtWidgets.QShortcut(self)
        self.hk_shift_tab.setKey('Shift+Tab')
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.mode_button)
        self.layout.addWidget(self.input_field)
        self.setLayout(self.layout)

    def _get_font_unit(self):
        label = QtWidgets.QLabel('UNIT')
        label.setStyleSheet(self.styleSheet())
        return label.sizeHint().height()

    def _set_sizes(self):
        self._font_unit = self._get_font_unit()
        self._height = self._font_unit * 2.4
        self._width = self._height * 10
        self._default_rect = QtCore.QRect(0, -1, self._width, 1)

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

    def text(self):
        item = self.commandlist.selectedItems()
        if item:
            return item[0].text()
        return self.input_field.text()

    def _start_alt_f4_timer(self):
        self._alt_f4_pressed = True

        def _finished():
            self._alt_f4_pressed = False

        QtCore.QTimer.singleShot(500, _finished)

    def accept(self):
        self.accepted.emit()

    def reject(self):
        self.rejected.emit()

    def keyPressEvent(self, event):
        if event.modifiers() & QtCore.Qt.AltModifier:
            self._start_alt_f4_timer()
        super(Dialog, self).keyPressEvent(event)

    def closeEvent(self, event):
        if self._alt_f4_pressed:
            self._alt_f4_pressed = False
            event.ignore()
            self.hk_alt_f4.activated.emit()
            return
        event.accept()

    def hide(self):
        if not self.pinned:
            self.force_hide()

    def force_hide(self):
        self.commandlist.hide()
        super(Dialog, self).hide()

    def get_position(self):
        if self.position == 'top':
            pos = ActiveScreen.top()
            return pos[0] - self._width * 0.5, pos[1]

        pos = ActiveScreen.center()
        return pos[0] - self._width * 0.5, pos[1] - self._height * 0.5

    def slide_group(self, pos):
        start = (pos[0], pos[1], self._width, 0)
        end = (pos[0], pos[1], self._width, self._height)
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

        crect = self.commandlist._get_geometry()
        self.commandlist.setGeometry(crect)
        group.addAnimation(fade_in(self.commandlist, duration=50))
        if crect.height() <= 1:
            return group

        start = (crect.left(), start[1], crect.width(), 0)
        self.commandlist.setGeometry(*start)
        end = (crect.left(), end[1] + self._height, crect.width(), crect.height())
        group.addAnimation(
            resize(
                self.commandlist,
                start_value=start,
                end_value=end,
            )
        )
        return group

    def fade_in_group(self, pos):
        self.setGeometry(pos[0], pos[1], self._width, self._height)
        self.commandlist.setGeometry(self.commandlist._get_geometry())
        group = parallel_group(self, fade_in(self), fade_in(self.commandlist))
        return group

    def setStyleSheet(self, style):
        super(Dialog, self).setStyleSheet(style)
        self._set_sizes()
        self.mode_button.setFixedHeight(self._height)
        self.mode_button.setMinimumWidth(self._height)

    def exec_(self, anim_type=None, lefttop=None):
        self.show(anim_type, lefttop)
        with event_loop(timeout=120000, parent=self.parent) as loop:
            loop.result = None

            def on_accept():
                loop.quit()
                loop.result = QtWidgets.QDialog.Accepted

            def on_reject():
                if loop.result is not None:
                    return
                loop.quit()
                loop.result = QtWidgets.QDialog.Rejected

            self.accepted.connect(on_accept)
            self.rejected.connect(on_reject)
        self.force_hide()
        return loop.result

    def activate(self):
        self.raise_()
        self.activateWindow()
        self.input_field.setFocus()

    def _show(self):
        self.commandlist.show()
        super(Dialog, self).show()

    def show(self, anim_type=None, lefttop=None):
        self.setGeometry(self._default_rect)
        self._show()
        lefttop = lefttop or self.get_position()
        anim_type = anim_type or self.animation
        group = getattr(self, anim_type + '_group')(lefttop)
        group.finished.connect(self.activate)
        group.start(group.DeleteWhenStopped)
