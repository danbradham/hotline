'''
hotline.py
----------

Contains HotLine object. A popup dialog that controls a HotField widget and
manages modes it's modes.
'''

import traceback
from collections import deque
import sys
from .highlighter import Highlighter
from .utils import rel_path, load_settings, save_settings
from .help import help_string, help_html
from .hotfield import HotField
from qt import QtGui, QtCore

REL = rel_path(".").replace('\\', '/')


class NonStdOut(object):

    handlers = []

    def write(self, msg):
        sys.__stdout__.write(msg)

        for handler in self.handlers:
            handler(msg)

    def add_handler(self, fn):
        self.handlers.append(fn)


class Button(QtGui.QPushButton):
    '''A button template'''

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
            tip="Open output window",
            checkable=False,
            parent=self)
        self.auto_button = Button(
            name="auto",
            tip="Autocomplete",
            checkable=True,
            parent=self)
        self.multiline_button = Button(
            name="multiline",
            tip="Toggle Multi-line Mode",
            checkable=True,
            parent=self)
        self.pin_button = Button(
            name="pin",
            tip="Pin HotLine (Keep on top)",
            checkable=True,
            parent=self)


        grid.setColumnStretch(0, 1)
        grid.addWidget(self.hotio_button, 0, 2)
        grid.addWidget(self.auto_button, 0, 3)
        grid.addWidget(self.multiline_button, 0, 4)
        grid.addWidget(self.pin_button, 0, 5)

    def mousePressEvent(self, event):
        '''Redirect to HotLine'''
        self.parent.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        '''Redirect to HotLine'''
        self.parent.mouseMoveEvent(event)


class SaveDialog(QtGui.QDialog):

    def __init__(self, mode, options, parent=None):
        super(SaveDialog, self).__init__(parent)

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


class HotIO(QtGui.QDockWidget):
    '''Input Output window for HotLine.

    Handles script/command storage and logging output.'''

    def __init__(self, hotline, parent=None):
        super(HotIO, self).__init__(parent)

        self.setFeatures(
            QtGui.QDockWidget.DockWidgetClosable|
            QtGui.QDockWidget.DockWidgetFloatable|
            QtGui.QDockWidget.DockWidgetMovable)
        self.setFloating(True)
        self.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea|
            QtCore.Qt.RightDockWidgetArea)

        self.setWindowTitle("HotLine IO")
        self.hotline = hotline

        wrap_widget = QtGui.QWidget(self)
        layout = QtGui.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        wrap_widget.setLayout(layout)

        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setDocumentMode(True)
        tb = self.tabs.tabBar()
        tb.setDrawBase(False)
        tb.setExpanding(True)
        tb.setFocusPolicy(QtCore.Qt.NoFocus)

        #Output Tab
        self._buffer = []
        out_widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        out_widget.setLayout(grid)

        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(8)

        self.textfield = QtGui.QTextBrowser(self)
        self.textfield.setFont(font)
        self.textfield.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.textfield.setReadOnly(True)
        self.textfield.setOpenExternalLinks(True)
        self.help_button = Button(
            name="help",
            tip="Print some help!",
            checkable=False,
            parent=self)
        self.clear_button = Button(
            name="clear",
            tip="Clear Log.",
            checkable=False,
            parent=self)

        self.clear_button.clicked.connect(self.clear_output)
        self.help_button.clicked.connect(self.print_help)

        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 1)
        grid.addWidget(self.textfield, 0, 0, 1, 4)
        grid.addWidget(self.clear_button, 1, 2)
        grid.addWidget(self.help_button, 1, 3)

        self.tabs.addTab(out_widget, "Output")

        #Store Tab
        store_widget = QtGui.QWidget(self)
        store_grid = QtGui.QGridLayout(store_widget)
        store_widget.setLayout(store_grid)
        self.store_line = EditLine("Insert Filter", store_widget)
        self.store_line.setObjectName("filter")
        self.store_refr = Button(
            name="refresh",
            tip="Refresh Store",
            checkable=False,
            parent=store_widget)
        self.store_list = QtGui.QListWidget(store_widget)
        self.store_list.setFocusPolicy(QtCore.Qt.NoFocus)
        self.store_list.setSortingEnabled(True)
        self.store_mode = QtGui.QLabel(store_widget)
        self.store_mode.hide()
        self.store_desc = QtGui.QLabel(store_widget)
        self.store_desc.setWordWrap(True)
        self.store_desc.hide()
        self.store_run = Button(
            name="run",
            tip="Run Selected.",
            checkable=False,
            parent=store_widget)
        self.store_load = Button(
            name="load",
            tip="Load selected.",
            checkable=False,
            parent=store_widget)
        self.store_save = Button(
            name="save",
            tip="Save current script.",
            checkable=False,
            parent=store_widget)
        self.store_del = Button(
            name="delete",
            tip="Delete selected",
            checkable=False,
            parent=store_widget)
        self.store_autoload = QtGui.QCheckBox("Autoload Selected")
        self.store_autoload.setEnabled(False)

        self.store_refresh()

        self.store_line.text_changed.connect(self.store_filter)
        self.store_refr.clicked.connect(self.store_refresh)
        self.store_list.currentTextChanged.connect(self.store_changed)
        self.store_list.itemChanged.connect(self.store_item_changed)
        self.store_autoload.stateChanged.connect(self.autoload_changed)
        self.store_run.clicked.connect(self.run)
        self.store_save.clicked.connect(self.save)
        self.store_load.clicked.connect(self.load)
        self.store_del.clicked.connect(self.delete)

        store_grid.setColumnStretch(0, 1)
        store_grid.setRowStretch(1, 1)
        store_grid.addWidget(self.store_line, 0, 0, 1, 4)
        store_grid.addWidget(self.store_refr, 0, 4)
        store_grid.addWidget(self.store_list, 1, 0, 1, 5)
        store_grid.addWidget(self.store_mode, 2, 0)
        store_grid.addWidget(self.store_desc, 3, 0, 1, 5)
        store_grid.addWidget(self.store_autoload, 4, 0)
        store_grid.addWidget(self.store_run, 4,1)
        store_grid.addWidget(self.store_save, 4, 2)
        store_grid.addWidget(self.store_load, 4, 3)
        store_grid.addWidget(self.store_del, 4, 4)

        self.tabs.addTab(store_widget, "Store")
        layout.addWidget(self.tabs, 0, 0)

        self.setWidget(wrap_widget)

        try:
            with open(rel_path('settings/user/style.css')) as f:
                style = f.read() % ({"rel": REL})
        except:
            with open(rel_path('settings/defaults/style.css')) as f:
                style = f.read() % ({"rel": REL})
        self.setStyleSheet(style)

    def print_help(self):
        self.textfield.append(help_string)
        cursor = self.textfield.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.textfield.insertHtml(help_html)

    def write(self, txt):
        self._buffer.append(txt)
        self.textfield.append(txt)

    def clear_output(self):
        self.textfield.clear()
        self._buffer = []

    def store_add_item(self, name):
        list_item = QtGui.QListWidgetItem(name)
        list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsEditable)
        list_item.setData(QtCore.Qt.UserRole, name)
        self.store_list.addItem(list_item)

    def store_item_changed(self, list_item):
        new_name = list_item.text()
        old_name = list_item.data(QtCore.Qt.UserRole)
        self.store[new_name] = self.store.pop(old_name)
        save_settings("store.settings", self.store)
        list_item.setData(QtCore.Qt.UserRole, new_name)

    def store_filter(self, text_filter):
        self.store_list.clear()
        for name, value in self.store.iteritems():
            if not text_filter.lower() in name.lower():
                continue
            self.store_add_item(name)

    def store_refresh(self):
        self.store = load_settings("store.settings")
        self.store_list.clear()
        self.store_line.clear()
        try:
            self.evaluate_store()
        except:
            print "Failed to autoload items from store."

    def evaluate_store(self, autoload=True):
        print "Evaluating store..."
        for mode in self.hotline._modes:
            for name, value in self.store.iteritems():
                if value["mode"] == mode.name:
                    self.store_add_item(name)
                    if autoload and value["autoload"]:
                        mode.handler(value["command"])

    def store_changed(self, name):
        command_values = self.store.get(name, None)
        if not command_values:
            self.store_autoload.setChecked(False)
            self.store_autoload.setEnabled(False)
            return
        self.store_autoload.setEnabled(True)
        self.store_autoload.setChecked(command_values["autoload"])
        self.store_mode.show()
        self.store_mode.setText(command_values["mode"])
        desc = command_values.get("description", None)
        if desc:
            self.store_desc.show()
            self.store_desc.setText(desc)
        else:
            self.store_desc.hide()

    def autoload_changed(self, value):
        list_item = self.store_list.currentItem()
        self.store_autoload.setEnabled(True)
        self.store[list_item.text()]["autoload"] = True if value else False
        save_settings("store.settings", self.store)

    def run(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        command_values = self.store.get(list_item.text(), None)
        if command_values:
            self.hotline.hotfield.clear()
            text = command_values["command"]
            mode = command_values["mode"]
            if mode == self.hotline.mode.name:
                self.hotline.handle_input(text)
                return
            for x in xrange(len(self.hotline._modes)):
                self.hotline.next_mode()
                if mode == self.hotline.mode.name:
                    self.hotline.handle_input(text)
                    return

    def save(self):

        options = [m.name for m in self.hotline._modes]
        save_diag = SaveDialog(self.hotline.mode.name, options, self)

        if save_diag.exec_():
            data = save_diag.data()
            name = data["name"]
            if not name in self.store:
                self.store_add_item(name)
            else:
                overwrite_it = QtGui.QMessageBox.question(
                    self,
                    name,
                    "Overwrite {0}?".format(name),
                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)
                if overwrite_it == QtGui.QMessageBox.No:
                    return
            data["command"] = self.hotline.hotfield.toPlainText()
            self.store[name] = data
            save_settings("store.settings", self.store)
        self.store_list.sortItems()

    def load(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        command_values = self.store.get(list_item.text(), None)
        if command_values:
            self.hotline.hotfield.clear()
            text = command_values["command"]
            if "\n" in text:
                self.hotline.multiline = True
                self.hotline.toolbar.multiline_button.setChecked(True)
                self.hotline.hotfield.setFocus()
            if not self.hotline.mode.name == command_values["mode"]:
                for x in xrange(len(self.hotline._modes)):
                    self.hotline.next_mode()
                    if command_values["mode"] == self.hotline.mode.name:
                        break
            self.hotline.hotfield.setText(command_values["command"])
        self.store_list.sortItems()
        self.hotline.hotfield.setFocus()

    def delete(self):
        list_item = self.store_list.currentItem()
        if not list_item:
            return
        delete_it = QtGui.QMessageBox.question(
            self,
            list_item.text(),
            "Delete {0}?".format(list_item.text()),
            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
            QtGui.QMessageBox.No)

        if delete_it == QtGui.QMessageBox.Yes:
            self.store.pop(list_item.text())
            self.store_list.takeItem(self.store_list.currentRow())
            save_settings("store.settings", self.store)
        self.store_list.sortItems()

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
        self.auto = False

        self.hotio = HotIO(self, parent if parent else self)
        self.hotio.hide()

        self.output = NonStdOut()
        sys.stdout = self.output
        self.output.add_handler(self.hotio.write)

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
        #self.toolbar.help_button.clicked.connect(self.help)
        self.toolbar.auto_button.clicked.connect(self.toggle_auto)

        self.hotfield.multiline_toggled.connect(self.toggle_multiline)
        self.hotfield.toolbar_toggled.connect(self.toggle_toolbar)
        self.hotfield.pin_toggled.connect(self.toggle_pin)
        self.hotfield.autocomplete_toggled.connect(self.toggle_auto)
        self.hotfield.show_output.connect(self.hotio.show)

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
        if self.multiline and doc_height > 30:
            self.hotfield.setFixedHeight(doc_height)
            height = (doc_height + 28 if self.toolbar.isVisible()
                      else doc_height + 4)
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
        self.output.write(
            "\n{0} Command: \n {1}\n\n".format(self.mode.name, str(input_str)))
        try:
            self.mode.handler(str(input_str))
        except:
            self.output.write(
                "".join(traceback.format_exception(*sys.exc_info())))
            self.hotio.show()
            self.hotio.tabs.setCurrentIndex(0)
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

    def toggle_auto(self):
        self.auto = False if self.auto else True
        self.toolbar.auto_button.setChecked(self.auto)

    def focusOutEvent(self, event):
        if self.pinned:
            super(HotLine, self).focusOutEvent(event)
            return
        if not self.hotfield.hasFocus():
            self.close()

    def help(self):
        self.hotio.show()
        self.hotio.write(help_string)

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.adjust_size()
        self.hotfield.setFocus()

    def exit(self):
        if not self.pinned:
            self.close()
