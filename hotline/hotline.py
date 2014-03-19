'''
hotline.py
----------

Contains HotLine object. A popup dialog that controls a HotField widget and
manages modes it's modes.
'''

import traceback
from collections import deque
from functools import partial
from .highlighter import Highlighter
from .utils import rel_path
from .help import help_string
from .hotfield import HotField
try:
    from PyQt4 import QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore

REL = rel_path(".").replace('\\', '/')


def load_script(name):
    script_path = rel_path("settings/user/scripts/{0}.py".format(name))
    with open(script_path, r) as f:
        script = f.read()
    return script


def save_script(name, script):
    script_path = rel_path("settings/user/scripts/{0}.py".format(name))
    with open(script_path, w) as f:
        f.write(script)


def delete_script(name):
    script_path = rel_path("settings/user/scripts/{0}.py".format(name))
    try:
        os.remove(script_path)
    except OSError:
        return


class Button(QtGui.QPushButton):
    '''A button template...because I'm getting tired of QPushButtons.'''

    def __init__(self, name, tip, checkable, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)

        self.setObjectName(name)
        self.setSizePolicy(
            QtGui.QSizePolicy.Fixed,
            QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(24)
        self.setFixedWidth(24)
        self.setCheckable(checkable)
        self.setToolTip(tip)


class Toolbar(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Toolbar, self).__init__(parent)

        self.parent = parent

        grid = QtGui.QGridLayout()
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)


        self.hotio_button = Button(
            name="output",
            tip="Open output window.",
            checkable=False,
            parent=self)
        self.help_button = Button(
            name="help",
            tip="Get some help.",
            checkable=False,
            parent=self)
        self.pin_button = Button(
            name="pin",
            tip="Pin HotLine (Keep on top)",
            checkable=True,
            parent=self)
        self.multiline_button = Button(
            name="multiline",
            tip="Toggle Multi-line Mode",
            checkable=True,
            parent=self)


        grid.setColumnStretch(0, 1)
        grid.addWidget(self.help_button, 0, 1)
        grid.addWidget(self.hotio_button, 0, 2)
        grid.addWidget(self.multiline_button, 0, 4)
        grid.addWidget(self.pin_button, 0, 5)

    def mousePressEvent(self, event):
        '''Redirect to HotLine'''
        self.parent.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        '''Redirect to HotLine'''
        self.parent.mouseMoveEvent(event)


class HotIO(QtGui.QDialog):
    '''Input Output window for HotLine.

    Handles script/command storage and logging output.'''

    save_current = QtCore.Signal()
    load_current = QtCore.Signal()
    del_current = QtCore.Signal()

    def __init__(self, parent=None):
        super(HotIO, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowStaysOnTopHint)

        layout = QtGui.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        tabs = QtGui.QTabWidget()

        #Store Tab
        store_widget = QtGui.QWidget()
        store_grid = QtGui.QGridLayout()
        store_widget.setLayout(store_grid)
        self.store_list = QtGui.QListWidget()
        self.store_load = Button(
            name="clear",
            tip="Load selectd.",
            checkable=False,
            parent=self)
        self.store_save = Button(
            name="save",
            tip="Save current script.",
            checkable=False,
            parent=self)
        self.store_del = Button(
            name="clear",
            tip="Delete selected",
            checkable=False,
            parent=self)

        self.store_save.clicked.connect(self.save_current.emit)
        self.store_load.clicked.connect(self.load_current.emit)
        self.store_del.clicked.connect(self.del_current.emit)

        store_grid.setColumnStretch(0, 1)
        store_grid.setRowStretch(0, 1)
        store_grid.addWidget(self.store_list, 0, 0, 1, 4)
        store_grid.addWidget(self.store_save, 1, 1)
        store_grid.addWidget(self.store_load, 1, 2)
        store_grid.addWidget(self.store_del, 1, 3)

        tabs.addTab(store_widget, "Store")

        #Output Tab
        self._buffer = []
        out_widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        out_widget.setLayout(grid)

        self.textfield = QtGui.QTextBrowser(self)
        self.textfield.setReadOnly(True)
        self.textfield.setOpenExternalLinks(True)
        self.help_button = Button(
            name="help",
            tip="Print some help!",
            checkable=False,
            parent=self)
        self.dump_button = Button(
            name="save",
            tip="Save log to file.",
            checkable=False,
            parent=self)
        self.clear_button = Button(
            name="clear",
            tip="Clear Log.",
            checkable=False,
            parent=self)

        self.dump_button.clicked.connect(self.dump_output)
        self.clear_button.clicked.connect(self.clear_output)
        self.help_button.clicked.connect(partial(self.append, help_string))

        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 1)
        grid.addWidget(self.textfield, 0, 0, 1, 4)
        grid.addWidget(self.clear_button, 1, 1)
        grid.addWidget(self.dump_button, 1, 2)
        grid.addWidget(self.help_button, 1, 3)

        tabs.addTab(out_widget, "Output")
        layout.addWidget(tabs, 0, 0)

    def append(self, txt):
        self._buffer.append(txt)
        self.textfield.append(txt)

    def clear_output(self):
        self.textfield.clear()
        self._buffer = []

    def dump_output(self):
        pass

    def show(self):
        super(HotIO, self).show()
        self.textfield.clear()
        self.textfield.append(''.join(self._buffer))


class HotLine(QtGui.QWidget):
    '''A popup dialog with a HotField widget and several modes of input.'''

    _modes = deque()
    instance = None

    def __init__(self, parent=None):
        super(HotLine, self).__init__(parent)

        HotLine.instance = self
        self._multiline = False
        self.pinned = False

        self.hotio = HotIO(self)
        self.hotio.hide()

        # Create and connect ui widgets
        self.hotfield = HotField(self)
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
        self.mode_button.setToolTip("Switch HotLine Mode\n")

        self.toolbar = Toolbar(self)
        self.toolbar.hide()
        self.toolbar.multiline_button.clicked.connect(self.toggle_multiline)
        self.toolbar.pin_button.clicked.connect(self.toggle_pin)
        self.toolbar.hotio_button.clicked.connect(self.hotio.show)
        self.toolbar.help_button.clicked.connect(self.help)

        self.hotfield.multiline_toggled.connect(self.toggle_multiline)
        self.hotfield.toolbar_toggled.connect(self.toggle_toolbar)
        self.hotfield.pin_toggled.connect(self.toggle_pin)

        # Layout widgets and set stretch policies
        self.layout = QtGui.QGridLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 0)
        self.layout.setRowStretch(2, 1)
        self.layout.addWidget(self.toolbar, 0, 0, 1, 2)
        self.layout.addWidget(self.mode_button, 1, 0)
        self.layout.addWidget(self.hotfield, 1, 1, 2, 1)
        self.setLayout(self.layout)

        # Set dialog flags and size policy
        self.setWindowFlags(
            QtCore.Qt.Window|
            QtCore.Qt.FramelessWindowHint|
            QtCore.Qt.WindowStaysOnTopHint)
        self.setObjectName('HotLine')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(28)

        if self._modes:
            self.mode.setup(self)

        # Setup keyboard shortcut
        esc_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence.fromString("Escape"),
            self,
            self.exit)

        try:
            with open(rel_path('settings/user/style.css')) as f:
                style = f.read() % ({"rel": REL})
        except:
            with open(rel_path('settings/defaults/style.css')) as f:
                style = f.read() % ({"rel": REL})
        self.setStyleSheet(style)

    @property
    def multiline(self):
        return self._multiline

    @multiline.setter
    def multiline(self, value):
        self._multiline = value
        self.adjust_size()

    @property
    def mode(self):
        '''Returns current mode.'''
        return self._modes[0]

    @classmethod
    def add_mode(cls, mode):
        '''Register modes with HotLine.'''
        cls._modes.append(mode)

    def mousePressEvent(self, event):
        self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        vect = event.globalPos() - self.start_pos
        self.move(vect.x(), vect.y())

    def adjust_size(self):
        doc_height = self.hotfield.document().size().height()
        doc_width = self.hotfield.document().idealWidth()
        if doc_width > 346 and self.multiline:
            self.hotfield.setFixedWidth(doc_width)
            self.setFixedWidth(doc_width + 54)
        else:
            self.hotfield.setFixedWidth(346)
            self.setFixedWidth(400)
        if self.multiline:
            self.hotfield.setFixedHeight(doc_height + 1)
            height = (doc_height + 29 if self.toolbar.isVisible()
                      else doc_height + 5)
            self.setFixedHeight(height)
        else:
            self.hotfield.setFixedHeight(24)
            self.setFixedHeight(28 if not self.toolbar.isVisible() else 52)

    def prev_mode(self):
        self._modes.rotate(1)
        self.mode.setup(self)

    def next_mode(self):
        self._modes.rotate(-1)
        self.mode.setup(self)

    def handle_input(self, input_str):
        self.hotio.append(
            "{0} Command: \n\n {1}\n\n".format(self.mode.name, str(input_str)))
        try:
            self.mode.handler(str(input_str))
        except:
            self.hotio.show()
            self.hotio.append(traceback.format_exc())
        if not self.pinned:
            self.exit()

    def toggle_multiline(self):
        self.multiline = False if self.multiline else True
        self.toolbar.multiline_button.setChecked(self.multiline)
        self.hotfield.setFocus()

    def toggle_toolbar(self):
        tb = self.toolbar.isVisible()
        pos = self.pos()
        if tb:
            self.toolbar.hide()
            self.move(pos.x(), pos.y() + 24)
        else:
            self.toolbar.show()
            self.move(pos.x(), pos.y() - 24)
        self.adjust_size()

    def toggle_pin(self):
        self.pinned = False if self.pinned else True
        self.toolbar.pin_button.setChecked(self.pinned)

    def focusOutEvent(self, event):
        if self.pinned:
            super(HotLine, self).focusOutEvent(event)
            return
        if not self.hotfield.hasFocus():
            self.close()

    def help(self):
        self.hotio.show()
        self.hotio.append(help_string)

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.hotfield.setFocus()

    def exit(self):
        if not self.pinned:
            self.close()
