from .qt import QtCore, QtGui
from .utils import rel_path
from .core import Event
from functools import partial
from settings import KeySettings
import os

REL = os.path.dirname(__file__)
STYLE = None


# Define all of our UI Events
# Make sure we're emitting these from the correct ui elements.
# Handlers added in controller.
store_filter = Event("Filter")
store_refresh = Event("Refresh")
store_run = Event("Run")
store_save = Event("Save")
store_load = Event("Load")
store_delete = Event("Delete")
show_help = Event("Help")
hotkey = Event("Hotkey Pressed")
tgl_tools = Event("Show Tools")
show_dock = Event("Show Dock")
tgl_auto = Event("Toggle Autocomplete")
tgl_pin = Event("Toggle Pin")
next_mode = Event("Next Mode")
prev_mode = Event("Previous Mode")
run = Event("Run")
next_hist = Event("Next History")
prev_hist = Event("Previous History")
clear_out = Event("Clear Output")


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


class Configurator(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Configurator, self).__init__(parent)

        grid = QtGui.QGridLayout()
        self.setLayout(grid)


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

        self.help_button.pressed += partial(show_help, self.text_area)
        self.clear_button.pressed += partial(clear_out, self.text_area)


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
            (self.del_button, store_delete),
            (self.save_button, store_save),
            (self.load_button, store_load),
            (self.run_button, store_run))
        for button, event in button_events:
            def emit_ev(self):
                event(self.store_list.currentItem())
            button.pressed += emit_ev

        self.filter.textChanged.connect(partial(store_filter, self.store_list))
        self.refr_button.pressed += partial(store_refresh, self.store_list)


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
        self.pressed = Event("{0} pressed".format(name))
        self.clicked.connect(self.pressed)
        self.setCheckable(checkable)


class Base(QtGui.QWidget):

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
        self.out_button = Button(
            name="output",
            tooltip="Show HotLine's Dock.",
            parent=self.tools)
        self.mode_button = Button(
            name="mode",
            tooltip="Change HotLine mode",
            size=(40, 24),
            parent=self)
        self.editor = editor(self)

        self.tools.addWidget(self.out_button, 0, 1)
        self.tools.addWidget(self.auto_button, 0, 2)
        self.tools.addWidget(self.multi_button, 0, 3)
        self.tools.addWidget(self.pin_button, 0, 4)
        grid.addWidget(self.tools, 0, 0, 1, 2)
        grid.addWidget(self.mode_button, 1, 0)
        grid.addWidget(self.editor, 1, 1)

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
