from .qt import QtCore, QtGui
from .utils import rel_path
from .events import *
from functools import partial
import os
import logging
import inspect

logger = logging.getLogger("hotline.views")


REL = os.path.dirname(__file__)
STYLE = None


def get_style():
    global STYLE
    if not STYLE:
        try:
            with open(rel_path('settings/user/style.css')) as f:
                STYLE = f.read() % ({"rel": REL})
        except:
            with open(rel_path('settings/defaults/style.css')) as f:
                STYLE = f.read() % ({"rel": REL})
    return STYLE


class View(object):

    def __init__(self, *args, **kwargs):
        logger.debug("In View __init__")

        bound_receivers = []
        for n, m in inspect.getmembers(self.__class__):
            if getattr(m, "is_receiver", False):
                bound_receivers.append(getattr(self, m.__name__))
        logger.debug("Event Receivers: {0}".format(bound_receivers))

        for receiver in bound_receivers:
            bound_receiver = getattr(self, receiver.__name__)
            receiver.event.calls(bound_receiver)
            logger.debug(
                "{0} ------> {1}".format(receiver.event, bound_receiver))

        super(View, self).__init__(*args, **kwargs)


class Configurator(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Configurator, self).__init__(parent)

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        self.rows = {}

    def add_row(self, name, value):
        pass

    def get(self, name, default=None):
        pass

    def set(self, name, value):
        pass


class Output(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Output, self).__init__(parent)

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(0, 1)
        self.setLayout(grid)

        self.text_area = QtGui.QTextEdit(self)
        self.help_button = Button(
            name="help",
            tooltip="Show Help.",
            parent=self)
        self.clear_button = Button(
            name="clear",
            tooltip="Clear Output.",
            parent=self)

        grid.addWidget(self.text_area, 0, 0, 1, 3)
        grid.addWidget(self.help_button, 1, 1)
        grid.addWidget(self.clear_button, 1, 2)

        self.help_button.pressed.calls(partial(Help, self.text_area))
        self.clear_button.pressed.calls(partial(ClearOutput, self.text_area))


class Store(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Store, self).__init__(parent)

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(0, 1)
        self.setLayout(grid)

        self.filter = QtGui.QLineEdit(self)
        self.refr_button = Button(
            name="refresh",
            tooltip="Refresh all stores",
            parent=self)
        self.store_list = QtGui.QListWidget(self)
        self.store_info = QtGui.QTextEdit(self)
        self.run_button = Button(
            name="run",
            tooltip="Run selected script",
            parent=self)
        self.save_button = Button(
            name="save",
            tooltip="Save current hotline command.",
            parent=self)
        self.load_button = Button(
            name="load",
            tooltip="Load current hotline command into editor.",
            parent=self)
        self.del_button = Button(
            name="delete",
            tooltip="Delete selected command.",
            parent=self)

        grid.addWidget(self.filter, 0, 0, 1, 4)
        grid.addWidget(self.refr_button, 0, 4)
        grid.addWidget(self.store_list, 1, 0, 1, 5)
        grid.addWidget(self.store_info, 2, 0, 1, 5)
        grid.addWidget(self.run_button, 3, 1)
        grid.addWidget(self.save_button, 3, 2)
        grid.addWidget(self.load_button, 3, 3)
        grid.addWidget(self.del_button, 3, 4)

        button_events = (
            (self.del_button, Delete),
            (self.save_button, Save),
            (self.load_button, Load),
            (self.run_button, Run))
        for button, event in button_events:
            def emit_ev(self):
                event(self.store_list.currentItem())
            button.pressed.calls(emit_ev)

        self.filter.textChanged.connect(partial(Filter, self.store_list))
        self.refr_button.pressed.calls(partial(Refresh, self.store_list))


class Save(QtGui.QDialog):

    def __init__(self, mode, options, parent=None):
        super(Save, self).__init__(parent)

        self.setWindowTitle("Save current command?")

        grid = QtGui.QGridLayout(self)
        grid.setColumnStretch(1, 1)

        name_label = QtGui.QLabel("Name:", self)
        self.name = QtGui.QLineEdit(self)

        mode_label = QtGui.QLabel("Mode:", self)
        self.mode = QtGui.QComboBox(self)
        self.mode.addItems(options)
        self.mode.setCurrentIndex(self.mode.findText(mode))

        desc_label = QtGui.QLabel("Description:", self)
        self.desc = QtGui.QTextEdit(self)

        self.autoload = QtGui.QCheckBox("Autoload Selected")

        self.ok = QtGui.QPushButton("Save", self)
        self.ok.clicked.connect(self.accept)
        self.notok = QtGui.QPushButton("Cancel", self)
        self.notok.clicked.connect(self.reject)
        buttons = QtGui.QHBoxLayout(self)
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.addWidget(self.ok)
        buttons.addWidget(self.notok)

        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self.name, 0, 1)
        grid.addWidget(mode_label, 1, 0)
        grid.addWidget(self.mode, 1, 1)
        grid.addWidget(desc_label, 2, 0)
        grid.addWidget(self.desc, 3, 0, 1, 2)
        grid.addWidget(self.autoload, 4, 1)
        grid.addLayout(buttons, 5, 1)

        self.setLayout(grid)

        try:
            with open(rel_path('settings/user/style.css')) as f:
                style = f.read() % ({"rel": REL})
        except:
            with open(rel_path('settings/defaults/style.css')) as f:
                style = f.read() % ({"rel": REL})
        self.setStyleSheet(style)

    def data(self):
        data = {
            "name": self.name.text(),
            "autoload": self.autoload.isChecked(),
            "mode": self.mode.currentText(),
            "description": self.desc.toPlainText()
        }
        return data


class Dock(QtGui.QDockWidget):

    def __init__(self, out=Output, store=Store, conf=Configurator, **kwargs):
        super(Dock, self).__init__(**kwargs)

        self.widget = QtGui.QTabWidget()
        self.setWidget(self.widget)

        self.output_tab = Output()
        self.store_tab = Store()
        self.conf_tab = Configurator()

        self.widget.addTab(self.output_tab, "Output")
        self.widget.addTab(self.store_tab, "Store")
        self.widget.addTab(self.conf_tab, "Configuration")

        self.setFeatures(
            QtGui.QDockWidget.DockWidgetClosable|
            QtGui.QDockWidget.DockWidgetFloatable|
            QtGui.QDockWidget.DockWidgetMovable)
        self.setFloating(True)
        self.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea|
            QtCore.Qt.RightDockWidgetArea)
        self.widget.setDocumentMode(True)
        tb = self.widget.tabBar()
        tb.setDrawBase(False)
        tb.setExpanding(True)
        tb.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setStyleSheet(get_style())


class Tools(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Tools, self).__init__(parent)
        self.parent = parent

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)
        self.addWidget = grid.addWidget

    def mousePressEvent(self, event):
        '''Redirect to Parent'''
        self.parent.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        '''Redirect to Parent'''
        self.parent.mouseMoveEvent(event)


class Editor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)


class Button(QtGui.QPushButton):

    def __init__(self, name, tooltip, size=(24, 24),
                 checkable=False, parent=None):
        super(Button, self).__init__(parent)
        self.setObjectName(name)
        self.setToolTip(tooltip)
        self.setFixedSize(*size)

        self.pressed = Event.create("{0} Button Pressed".format(name.title()))

        self.clicked.connect(self.pressed)
        self.setCheckable(checkable)


class Base(View, QtGui.QWidget):

    def __init__(self, editor=Editor, parent=None):
        super(Base, self).__init__(parent)

        grid = QtGui.QGridLayout()
        grid.setContentsMargins(0, 0, 2, 2)
        grid.setSpacing(0)
        grid.setColumnStretch(1, 1)
        self.setLayout(grid)

        self.tools = Tools(self)
        self.pin_button = Button(
            name="pin",
            tooltip="Pin HotLine.",
            checkable=True,
            parent=self.tools)
        self.multi_button = Button(
            name="multiline",
            tooltip="Toggle Multiline.",
            checkable=True,
            parent=self.tools)
        self.auto_button = Button(
            name="auto",
            tooltip="Toggle Autocomplete.",
            checkable=True,
            parent=self.tools)
        self.dock_button = Button(
            name="output",
            tooltip="Show HotLine's Dock.",
            parent=self.tools)
        self.mode_button = Button(
            name="mode",
            tooltip="Change HotLine mode",
            size=(40, 24),
            parent=self)
        self.editor = Editor(self)

        self.tools.addWidget(self.dock_button, 0, 1)
        self.tools.addWidget(self.auto_button, 0, 2)
        self.tools.addWidget(self.multi_button, 0, 3)
        self.tools.addWidget(self.pin_button, 0, 4)
        grid.addWidget(self.tools, 0, 0, 1, 2)
        grid.addWidget(self.mode_button, 1, 0)
        grid.addWidget(self.editor, 1, 1)

        self.dock = Dock(parent)
        self.dock.hide()

        self.dock_button.pressed.calls(self.dock.show)
        self.auto_button.pressed.calls(ToggleAutocomplete)
        self.multi_button.pressed.calls(ToggleMultiline)
        self.pin_button.pressed.calls(TogglePin)

        self.setWindowFlags(
            QtCore.Qt.Window|
            QtCore.Qt.FramelessWindowHint|
            QtCore.Qt.WindowStaysOnTopHint)
        self.setObjectName('HotLine')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(50)
        self.setStyleSheet(get_style())


    def mousePressEvent(self, event):
        self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        vect = event.globalPos() - self.start_pos
        self.move(vect.x(), vect.y())
