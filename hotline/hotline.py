'''
hotline.py
----------

Contains HotLine object. A popup dialog that controls a HotField widget and
manages modes it's modes.
'''

from collections import deque
from .highlighter import Highlighter
from .utils import rel_path
from .hotfield import HotField
from .mode import Mode
import os

#Try PyQt then PySide imports
try:
    from PyQt4 import QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore

REL = rel_path(".").replace('\\', '/')


class HotLine(QtGui.QDialog):
    '''A popup dialog with a HotField widget and several modes of input.'''

    _modes = deque()

    def __init__(self, parent=None):
        super(HotLine, self).__init__(parent)

        # Create and connect ui widgets
        self.hotfield = HotField()
        self.hotfield.setObjectName("input")
        self.hotfield.next_mode.connect(self.next_mode)
        self.hotfield.prev_mode.connect(self.prev_mode)
        self.hotfield.returnPressed.connect(self.handle_input)
        # Add python highlighter to hotfield
        self.highlighter = Highlighter(self.hotfield)
        # Add popup completer to hotfield
        self.mode_button = QtGui.QPushButton()
        self.mode_button.setObjectName("mode")
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
        self.multiline_button = QtGui.QPushButton()
        self.multiline_button.setObjectName("multiline")
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
        self.hotfield.multilineToggled.connect(
            self.multiline_button.setChecked)

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
            QtCore.Qt.Popup|
            QtCore.Qt.FramelessWindowHint|
            QtCore.Qt.WindowStaysOnTopHint)
        self.setObjectName('HotLine')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(28)
        if self._modes:
            self.mode.setup(self)

        try:
            with open(rel_path('settings/user/style.css')) as f:
                style = f.read() % ({"rel": REL})
        except:
            with open(rel_path('settings/defaults/style.css')) as f:
                style = f.read() % ({"rel": REL})
        self.setStyleSheet(style)

    @property
    def mode(self):
        '''Returns current mode.'''
        return self._modes[0]

    @classmethod
    def add_mode(cls, mode):
        '''Register modes with HotLine.'''
        cls._modes.append(mode)

    def prev_mode(self):
        self._modes.rotate(1)
        self.mode.setup(self)

    def next_mode(self):
        self._modes.rotate(-1)
        self.mode.setup(self)

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
