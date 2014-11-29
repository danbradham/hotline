from .highlighter import Highlighter
from ..utils import rel_path
from ..shout import has_ears, shout, hears
from ..messages import (ToggleMultiline, ToggleAutocomplete, TogglePin,
                       ToggleToolbar, Execute, NextHistory, NextMode,
                       PrevHistory, PrevMode, ShowDock, ShowHelp,
                       ClearOutput, AdjustSize, Store_Run, Store_Save,
                       Store_Load, Store_Delete, Store_Refresh)
from PySide import QtCore, QtGui
from functools import partial
import os
import logging

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

        self.buffer = []

        self.text_area = QtGui.QTextEdit(self)
        self.help_button = Button(
            message=ShowHelp,
            name="help",
            tooltip="Show Help.",
            parent=self)
        self.clear_button = Button(
            message=ClearOutput,
            name="clear",
            tooltip="Clear Output.",
            parent=self)

        grid.addWidget(self.text_area, 0, 0, 1, 3)
        grid.addWidget(self.help_button, 1, 1)
        grid.addWidget(self.clear_button, 1, 2)

    def write(self, text):
        self.text_area.clear()
        self.buffer.append(text)
        for line in self.buffer:
            self.text_area.append(line)

    def clear(self):
        self.buffer = []
        self.text_area.clear()


class Store(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Store, self).__init__(parent)

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(0, 1)
        self.setLayout(grid)

        self.filter = EditLine("Input Store Filter", self)
        self.refr_button = Button(
            message=Store_Refresh,
            name="refresh",
            tooltip="Refresh all stores",
            parent=self)
        self.store_list = QtGui.QListWidget(self)
        self.store_info = QtGui.QTextEdit(self)
        self.run_button = Button(
            message=Store_Run,
            name="run",
            tooltip="Run selected script",
            parent=self)
        self.save_button = Button(
            message=Store_Save,
            name="save",
            tooltip="Save current hotline command.",
            parent=self)
        self.load_button = Button(
            message=Store_Load,
            name="load",
            tooltip="Load current hotline command into editor.",
            parent=self)
        self.del_button = Button(
            message=Store_Delete,
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

        self.output = Output()
        self.store = Store()
        self.conf = Configurator()

        self.widget.addTab(self.output, "Output")
        self.widget.addTab(self.store, "Store")
        self.widget.addTab(self.conf, "Configuration")

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


class EditLine(QtGui.QLineEdit):

    text_emitted = QtCore.Signal(str)
    text_changed = QtCore.Signal(str)

    def __init__(self, default='', parent=None):
        super(EditLine, self).__init__(parent)
        self.default = default
        self.setText(self.default)
        self.returnPressed.connect(self.return_line)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding,)

    def mousePressEvent(self, event):
        super(EditLine, self).mousePressEvent(event)
        if self.default == self.text():
            self.setCursorPosition(0)

    def focusInEvent(self, event):
        super(EditLine, self).focusInEvent(event)
        if self.default == self.text():
            self.setCursorPosition(0)

    def focusOutEvent(self, event):
        super(EditLine, self).focusOutEvent(event)
        if not self.text():
            self.setText(self.default)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key.Key_Shift, QtCore.Qt.Key.Key_Control):
            event.accept()
        if self.default == self.text():
            self.clear()
        super(EditLine, self).keyPressEvent(event)
        self.text_changed.emit(self.text())

    def return_line(self):
        self.text_emitted.emit(self.text())
        self.setText(self.default)
        self.clearFocus()


class Editor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)
        self.parent = parent

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(24)
        self.setFixedWidth(346)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.setFont(font)
        self.completer = QtGui.QCompleter(self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer_model = QtGui.QStringListModel([], self)
        self.completer.setModel(self.completer_model)
        self.completer.activated.connect(self.insertCompletion)
        self.document().contentsChanged.connect(partial(shout, AdjustSize))

        #Setup Hotkeys
        self.key_methods = {
            "Toggle Multiline": partial(shout, ToggleMultiline),
            "Next Mode": partial(shout, NextMode),
            "Prev Mode": partial(shout, PrevMode),
            "Execute": partial(shout, Execute),
            "Previous in History": partial(shout, PrevHistory),
            "Next in History": partial(shout, NextHistory),
            "Pin": partial(shout, TogglePin),
            "Toggle Toolbar": partial(shout, ToggleToolbar),
            "Toggle Autocomplete": partial(shout, ToggleAutocomplete),
            "Show Output": partial(shout, ShowDock)}

    def set_completer_model(self, completer_list):
        self.completer_model.setStringList(completer_list)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        tc.insertText(completion)
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QtGui.QTextEdit.focusInEvent(self, event)

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

    def focusOutEvent(self, event):
        super(Editor, self).focusOutEvent(event)
        if not self.parent.hasFocus():
            self.parent.focusOutEvent(event)

    def keyPressEvent(self, event):
        keysettings = self.parent.ctx.keysettings
        completer_popup = self.completer.popup()
        is_completing = completer_popup.isVisible()
        is_multiline = self.parent.ctx.multiline
        is_auto = self.parent.ctx.autocomplete
        key = event.key()
        mod = event.modifiers()
        key_seq = self.to_key_sequence(key, mod)

        #Singleline Hotkeys
        if not is_multiline and not is_completing:
            for name, seq in keysettings['standard'].iteritems():
                if key_seq.matches(seq):
                    self.key_methods[name]()
                    return
        #Multiline Hotkeys
        if is_multiline and not is_completing:
            for name, seq in keysettings['multiline'].iteritems():
                if key_seq.matches(seq):
                    self.key_methods[name]()
                    return

        #Tab Insertion as spaces
        if (
            not is_completing
            and key in (QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab)
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

        if not hasattr(QtCore, "pyqtSignal"): # Check if we're using PyQt
            if key in (QtCore.Qt.Key.Key_Shift, QtCore.Qt.Key.Key_Control):
                event.accept()
                return
            else:
                super(Editor, self).keyPressEvent(event)

        if is_auto:
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


class Button(QtGui.QPushButton):

    def __init__(self, message, name, tooltip, size=(24, 24),
                 checkable=False, parent=None):
        super(Button, self).__init__(parent)
        self.setObjectName(name)
        self.setToolTip(tooltip)
        self.setFixedSize(*size)
        self.setCheckable(checkable)
        self.clicked.connect(partial(shout, message))


class UI(QtGui.QWidget):

    instance = None

    def __init__(self, ctx, parent=None):
        super(UI, self).__init__(parent)
        self.ctx = ctx

        grid = QtGui.QGridLayout()
        grid.setContentsMargins(0, 0, 2, 2)
        grid.setSpacing(0)
        grid.setColumnStretch(1, 1)
        self.setLayout(grid)

        self.tools = Tools(self)
        self.pin_button = Button(
            message=TogglePin,
            name="pin",
            tooltip="Pin HotLine.",
            checkable=True,
            parent=self.tools)
        self.multi_button = Button(
            message=ToggleMultiline,
            name="multiline",
            tooltip="Toggle Multiline.",
            checkable=True,
            parent=self.tools)
        self.auto_button = Button(
            message=ToggleAutocomplete,
            name="auto",
            tooltip="Toggle Autocomplete.",
            checkable=True,
            parent=self.tools)
        self.dock_button = Button(
            message=ShowDock,
            name="output",
            tooltip="Show HotLine's Dock.",
            parent=self.tools)
        self.mode_button = Button(
            message=NextMode,
            name="mode",
            tooltip="Change HotLine mode",
            size=(40, 24),
            parent=self)

        self.tools.addWidget(self.dock_button, 0, 1)
        self.tools.addWidget(self.auto_button, 0, 2)
        self.tools.addWidget(self.multi_button, 0, 3)
        self.tools.addWidget(self.pin_button, 0, 4)

        self.editor = Editor(self)
        self.highlighter = Highlighter(self.editor)
        grid.addWidget(self.tools, 0, 0, 1, 2)
        grid.addWidget(self.mode_button, 1, 0)
        grid.addWidget(self.editor, 1, 1)

        self.dock = Dock(parent=parent)
        self.dock.hide()

        self.output = self.dock.output
        self.store = self.dock.store
        self.conf = self.dock.conf

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

    @hears(AdjustSize)
    def adjust_size(self):
        doc_height = self.editor.document().size().height()
        doc_width = self.editor.document().idealWidth()
        if doc_width > 346 and self.ctx.multiline:
            self.editor.setFixedWidth(doc_width)
            self.setFixedWidth(doc_width + 54)
        else:
            self.editor.setFixedWidth(346)
            self.setFixedWidth(400)
        if self.ctx.multiline and doc_height > 30:
            self.editor.setFixedHeight(doc_height)
            height = (doc_height + 28 if self.tools.isVisible()
                      else doc_height + 4)
            self.setFixedHeight(height)
        else:
            self.editor.setFixedHeight(24)
            self.setFixedHeight(28 if not self.tools.isVisible() else 52)

    def focusOutEvent(self, event):
        if self.ctx.pinned:
            super(UI, self).focusOutEvent(event)
            return
        if not self.editor.hasFocus():
            self.close()

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        super(UI, self).show()
        self.adjust_size()
        self.editor.setFocus()

    def exit(self):
        if not self.ctx.pinned:
            self.close()
