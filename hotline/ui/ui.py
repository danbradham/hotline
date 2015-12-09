from .highlighter import Highlighter
from ..shout import has_ears, shout, hears
from .. import __version__
from ..messages import (ToggleMultiline, ToggleAutocomplete, TogglePin,
                       ToggleToolbar, Execute, NextHistory, NextMode,
                       PrevHistory, PrevMode, ShowDock, ShowHelp,
                       ClearOutput, AdjustSize, Store_Run, Store_Save,
                       Store_Load, Store_Delete, Store_Refresh, WriteOutput,
                       Store_Evaluate)
from PySide import QtCore, QtGui
from functools import partial
import os
import logging
import resource

logger = logging.getLogger("hotline.ui")
STYLE = None


def get_style():
    global STYLE
    if not STYLE:
        with open(os.path.join(os.path.dirname(__file__), 'style.css')) as f:
            STYLE = f.read()
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


@has_ears
class OutputWidget(QtGui.QWidget):

    def __init__(self, app, parent=None):
        super(OutputWidget, self).__init__(parent)
        self.app = app
        self.parent = parent

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(0, 1)
        self.setLayout(grid)

        self.text_area = QtGui.QTextEdit(self)
        self.help_button = Button(
            connect=partial(shout, ShowHelp),
            name="help",
            tooltip="Show Help.",
            parent=self)
        self.clear_button = Button(
            connect=partial(shout, ClearOutput),
            name="clear",
            tooltip="Clear Output.",
            parent=self)

        grid.addWidget(self.text_area, 0, 0, 1, 3)
        grid.addWidget(self.help_button, 1, 1)
        grid.addWidget(self.clear_button, 1, 2)

    @hears(WriteOutput)
    def write(self, text):
        self.text_area.append(text)

    @hears(ClearOutput)
    def clear(self):
        self.text_area.clear()


class RightLabel(QtGui.QLabel):

    def __init__(self, *args, **kwargs):
        super(RightLabel, self).__init__(*args, **kwargs)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.setFixedHeight(12)
        self.setWordWrap(True)


@has_ears
class StoreWidget(QtGui.QWidget):

    def __init__(self, app, parent=None):
        super(StoreWidget, self).__init__(parent)
        self.app = app
        self.parent = parent

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(1, 1)
        self.setLayout(grid)

        self.filter = EditLine("Input Store Filter", self)
        self.filter.text_changed.connect(self.filter_list)
        self.refr_button = Button(
            connect=self.refresh,
            name="refresh",
            tooltip="Refresh all stores",
            parent=self)
        self.store_list = QtGui.QListWidget(self)
        self.store_list.currentTextChanged.connect(self.item_changed)
        self.store_list.itemChanged.connect(self.item_name_changed)
        mode_label = RightLabel("Mode")
        self.item_mode = QtGui.QLabel()
        self.item_mode.setWordWrap(True)
        name_label = RightLabel("Name")
        self.item_name = QtGui.QLabel()
        self.item_name.setWordWrap(True)
        desc_label = RightLabel("Description")
        desc_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.item_desc = QtGui.QLabel()
        self.item_desc.setWordWrap(True)
        auto_label = RightLabel("Autoload")
        self.item_auto = QtGui.QCheckBox()
        self.item_auto.stateChanged.connect(self.auto_load_changed)
        self.run_button = Button(
            connect=self.run,
            name="run",
            tooltip="Run selected script",
            parent=self)
        self.save_button = Button(
            connect=self.save,
            name="save",
            tooltip="Save current hotline command.",
            parent=self)
        self.load_button = Button(
            connect=self.load,
            name="load",
            tooltip="Load current hotline command into editor.",
            parent=self)
        self.del_button = Button(
            connect=self.delete,
            name="delete",
            tooltip="Delete selected command.",
            parent=self)

        grid.addWidget(self.filter, 0, 0, 1, 5)
        grid.addWidget(self.refr_button, 0, 5)
        grid.addWidget(self.store_list, 1, 0, 1, 6)
        grid.addWidget(mode_label, 2, 0)
        grid.addWidget(self.item_mode, 2, 1, 5)
        grid.addWidget(name_label, 3, 0)
        grid.addWidget(self.item_name, 3, 1, 5)
        grid.addWidget(desc_label, 4, 0)
        grid.addWidget(self.item_desc, 4, 1, 5)
        grid.addWidget(auto_label, 5, 0)
        grid.addWidget(self.item_auto, 5, 1, 5)
        grid.addWidget(self.run_button, 6, 2)
        grid.addWidget(self.save_button, 6, 3)
        grid.addWidget(self.load_button, 6, 4)
        grid.addWidget(self.del_button, 6, 5)

    def auto_load_changed(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        data = self.app.store[list_item.text()]
        data.update({'autoload': self.item_auto.isChecked()})
        self.app.store.save()

    def item_name_changed(self, list_item):
        new_name = list_item.text()
        old_name = list_item.data(QtCore.Qt.UserRole)
        self.app.store[new_name] = self.app.store.pop(old_name)

    def filter_list(self, text):
        num_items = self.store_list.count()
        for i in xrange(num_items):
            item = self.store_list.item(i)
            if not text or text in item.text():
                item.show()
                continue
            item.hide()

    def item_changed(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        name = list_item.text()
        data = self.app.store[name]
        self.item_mode.setText(data['mode'])
        self.item_name.setText(name)
        self.item_desc.setText(data['description'])
        self.item_auto.setChecked(data['autoload'])

    def refresh(self):
        self.store_list.clear()
        self.app.store.refresh()
        self.app.store.evaluate(self.app.ctx.modes)

    def save(self):

        options = [m.name for m in self.app.ctx.modes]
        save_diag = StoreDialog(self.app.ctx.mode.name, options, self)

        list_item = self.store_list.currentItem()
        if list_item:
            name = list_item.text()
            data = self.app.store[name]
            save_diag.name.setText(name)
            save_diag.autoload.setChecked(data['autoload'])
            save_diag.desc.append(data['description'])

        if save_diag.exec_():
            data = save_diag.data()
            name = data["name"]
            if not name in self.app.store:
                self.new_store_item(name)
            else:
                overwrite_it = QtGui.QMessageBox.question(
                    self,
                    name,
                    "Overwrite {0}?".format(name),
                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)
                if overwrite_it == QtGui.QMessageBox.No:
                    return
            data["command"] = self.parent.editor.toPlainText()
            self.app.store[name] = data
            self.app.store.save()
        self.store_list.sortItems()

    def run(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        name = list_item.text()
        data = self.app.store[name]
        self.app.store.run(data)

    def delete(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        self.app.store.delete(list_item.text())
        self.store_list.takeItem(self.store_list.currentRow())

    def load(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        data = self.app.store[list_item.text()]
        self.app.set_mode(data['mode'])
        self.parent.editor.setText(data['command'])
        self.app.multiline = '\n' in data['command']

    @hears(Store_Evaluate)
    def new_store_item(self, name):
        list_item = QtGui.QListWidgetItem(name)
        list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsEditable)
        self.store_list.addItem(list_item)


class StoreDialog(QtGui.QDialog):

    def __init__(self, mode, options, parent=None):
        super(StoreDialog, self).__init__(parent)

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

        self.setStyleSheet(get_style())

    def data(self):
        data = {
            "name": self.name.text(),
            "autoload": self.autoload.isChecked(),
            "mode": self.mode.currentText(),
            "description": self.desc.toPlainText()
        }
        return data


class Dock(QtGui.QDockWidget):

    def __init__(self, **kwargs):
        super(Dock, self).__init__(**kwargs)

        self.widget = QtGui.QTabWidget()
        self.setWidget(self.widget)
        self.setWindowTitle("HotLine " + __version__)

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
        self.setObjectName('Tools')
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

    def __init__(self, app, parent=None):
        super(Editor, self).__init__(parent)
        self.app = app
        self.parent = parent

        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFixedHeight(24)
        self.setFixedWidth(354)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
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
            "Toggle Multiline": self.app.toggle_multiline,
            "Next Mode": self.app.next_mode,
            "Prev Mode": self.app.prev_mode,
            "Execute": self.key_execute,
            "Previous in History": self.key_prev_hist,
            "Next in History": self.app.next_hist,
            "Pin": self.app.toggle_pin,
            "Toggle Toolbar": partial(shout, ToggleToolbar),
            "Toggle Autocomplete": self.app.toggle_autocomplete,
            "Show Output": partial(shout, ShowDock)}

    def key_prev_hist(self):
        self.app.prev_hist(self.toPlainText())

    def key_execute(self):
        input_str = self.toPlainText()
        self.app.run(input_str)

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
        keysettings = self.app.config['KEYS']
        completer_popup = self.completer.popup()
        is_completing = completer_popup.isVisible()
        is_multiline = self.app.multiline
        is_auto = self.app.autocomplete
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

    def __init__(self, connect, name, tooltip, size=(24, 24),
                 checkable=False, parent=None):
        super(Button, self).__init__(parent)
        self.setObjectName(name)
        self.setToolTip(tooltip)
        self.setFixedSize(*size)
        self.setCheckable(checkable)
        self.clicked.connect(connect)


@has_ears
class UI(QtGui.QWidget):

    def __init__(self, app, parent=None):
        super(UI, self).__init__(parent)
        self.app = app

        grid = QtGui.QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setVerticalSpacing(2)
        grid.setHorizontalSpacing(0)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(1, 1)
        self.setLayout(grid)

        self.tools = Tools(self)
        self.tools.setFixedHeight(24)
        self.pin_button = Button(
            connect=self.app.toggle_pin,
            name="pin",
            tooltip="Pin HotLine.",
            checkable=True,
            parent=self.tools)
        self.multi_button = Button(
            connect=self.app.toggle_multiline,
            name="multiline",
            tooltip="Toggle Multiline.",
            checkable=True,
            parent=self.tools)
        self.auto_button = Button(
            connect=self.app.toggle_autocomplete,
            name="auto",
            tooltip="Toggle Autocomplete.",
            checkable=True,
            parent=self.tools)
        self.dock_button = Button(
            connect=partial(shout, ShowDock),
            name="output",
            tooltip="Show HotLine's Dock.",
            parent=self.tools)
        self.mode_button = Button(
            connect=self.app.next_mode,
            name="mode",
            tooltip="Change HotLine mode",
            size=(40, 24),
            parent=self)

        self.tools.addWidget(self.dock_button, 0, 1)
        self.tools.addWidget(self.auto_button, 0, 2)
        self.tools.addWidget(self.multi_button, 0, 3)
        self.tools.addWidget(self.pin_button, 0, 4)

        self.editor = Editor(self.app, self)
        self.highlighter = Highlighter(self.editor)
        grid.addWidget(self.tools, 0, 0, 1, 2)
        grid.addWidget(self.mode_button, 1, 0)
        grid.addWidget(self.editor, 1, 1)
        grid.setAlignment(self.mode_button, QtCore.Qt.AlignVCenter)
        grid.setAlignment(self.editor, QtCore.Qt.AlignVCenter)

        self.dock = Dock(parent=parent)
        self.dock.hide()

        self.output_tab = OutputWidget(self.app, self)
        self.store_tab = StoreWidget(self.app, self)
        self.dock.widget.addTab(self.output_tab, "Output")
        self.dock.widget.addTab(self.store_tab, "Store")

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
        '''Adjusts size based on multiline attribute and toolbar visibility'''

        doc_height = self.editor.document().size().height()
        doc_width = self.editor.document().idealWidth()

        if doc_width > 354 and self.app.multiline:
            self.editor.setFixedWidth(doc_width)
            self.setFixedWidth(doc_width + 46)
        else:
            self.editor.setFixedWidth(354)
            self.setFixedWidth(400)

        if doc_height > 28 and self.app.multiline:
            self.editor.setFixedHeight(min(doc_height, 570))
            height = (doc_height + 30 if self.tools.isVisible()
                      else doc_height + 2)
            self.setFixedHeight(min(height, 600))
        else:
            self.editor.setFixedHeight(24)
            self.setFixedHeight(54 if self.tools.isVisible() else 28)


    @hears(ShowDock)
    def show_dock(self):
        self.dock.show()

    @hears(ToggleAutocomplete)
    def toggle_autocomplete(self):
        self.auto_button.setChecked(self.app.autocomplete)

    @hears(ToggleMultiline)
    def toggle_multiline(self):
        self.multi_button.setChecked(self.app.multiline)
        self.adjust_size()

    @hears(TogglePin)
    def toggle_pinned(self):
        self.pin_button.setChecked(self.app.pinned)

    @hears(NextMode, PrevMode)
    def setup_mode(self, mode):
        self.mode_button.setText(mode.name)
        self.highlighter.set_rules(mode.patterns, mode.multiline_patterns)
        self.editor.set_completer_model(mode.completer_list)

    @hears(Execute)
    def key_execute(self, result):
        if result:
            self.editor.clear()
        else:
            self.dock.show()
            self.dock.widget.setCurrentIndex(0)
        self.exit()

    @hears(ShowHelp)
    def show_help(self):
        self.output_tab.write(self.format_help())

    @hears(ClearOutput)
    def clear_output(self):
        self.output_tab.clear()

    @hears(NextHistory, PrevHistory)
    def history_changed(self, mode, text):
        if mode:
            self.app.set_mode(mode.name)
        self.editor.clear()
        self.editor.insertPlainText(text)

    @hears(ToggleToolbar)
    def key_toggletoolbar(self):
        pos = self.pos()
        if self.tools.isVisible():
            self.tools.hide()
            self.adjust_size()
            self.move(pos.x(), pos.y() + 26)
        else:
            self.tools.show()
            self.adjust_size()
            self.move(pos.x(), pos.y() - 26)

    def format_help(self):
        keys = self.app.config['KEYS']
        #Generate hotkey table
        col1_max = max([len(key) for key in keys["standard"].keys()]) + 1
        col2_max = max([len(value) for value in keys["standard"].values()]) + 2
        col3_max = max([len(value) for value in keys["multiline"].values()]) + 1
        row_template = "| {0:<{col1_max}}| {1:<{col2_max}}| {2:<{col3_max}}|"
        hotkey_table = []
        for command, hotkey in keys["standard"].iteritems():
            row = row_template.format(
                command,
                hotkey,
                keys["multiline"][command],
                col1_max=col1_max,
                col2_max=col2_max,
                col3_max=col3_max)
            hotkey_table.append(row)

        help_string = (
            "|        Hotkey       | singleline |   multiline    |"
            "| ------------------- | ---------- | -------------- |"
            "{hotkeys}"
        ).format(hotkeys="\n".join(hotkey_table))
        return help_string


    def focusOutEvent(self, event):
        if self.app.pinned:
            super(UI, self).focusOutEvent(event)
            return
        if not self.editor.hasFocus():
            self.close()

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.adjust_size()
        self.editor.setFocus()

    def exit(self):
        if not self.app.pinned:
            self.close()
