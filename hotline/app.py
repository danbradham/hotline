# -*- coding: utf-8 -*-
import signal
import sys
from Queue import Queue
from functools import partial
import traceback
from Qt import QtWidgets
from .command import Command
from .mode import Mode
from .contexts import best_context
from .widgets import Dialog, ModesDialog
from .utils import execute_in_main_thread, redirect_stream


class flags(object):
    class DontHide: pass
    class Hide: pass
    _list = [DontHide, Hide]


class HotlineMode(Mode):

    name = 'HotlineMode'
    short_name = 'HL'

    def show_console(self):
        self.app.ui.console.show()
        return flags.DontHide

    def toggle_pin(self):
        self.app.ui.pinned = not self.app.ui.pinned

    def stepped_command(self):
        result = self.app.get_user_input('Hello')
        print 'User input: ', result

    @property
    def commands(self):
        return [
            Command('Toggle Pin', self.toggle_pin),
            Command('Show Console', self.show_console),
            Command('Show Settings', self.show_console),
            Command('Stepped Command', self.stepped_command)
        ]

    def execute(self, command):
        print command


class HotlineStream(object):

    def __init__(self, app):
        self.app = app

    def write(self, message):
        sys.__stdout__.write(message)
        if self.app.ui:
            self.app.ui.console.write(message)


class Hotline(object):

    def __init__(self, context=None):
        context = context or best_context()
        self.context = context(self)
        self.stream = HotlineStream(self)
        self.ui = None

    def init_ui(self):
        '''Initialize the UI'''
        if self.ui:
            raise Exception('UI has already initialized')

        self.add_modes(HotlineMode)
        self.ui = ModesDialog(self.context.parent)
        self.ui.setStyleSheet(self.context.style)
        self.ui.mode_button.clicked.connect(self.on_next_mode)
        self.ui.hk_tab.activated.connect(self.on_next_mode)
        self.ui.hk_shift_tab.activated.connect(self.on_prev_mode)
        self.ui.hk_alt_f4.activated.connect(self.exit)
        self.ui.accepted.connect(self.on_accept)
        self.ui.rejected.connect(self.on_reject)
        self.refresh()

    def exit(self):
        if self._standalone:
            self._event_loop.setQuitOnLastWindowClosed(True)
            self._event_loop.quit()
            return

        self.ui._hide()

    def _show_args(self):
        try:
            position = self.context.get_position()
        except NotImplementedError:
            position = None

        if position is None:
            self.ui.position = self.context.position
            position = self.ui.get_position()

        return self.context.animation, position

    def show(self):
        '''Show the HotlineUI'''

        if self.ui:
            execute_in_main_thread(self.ui.show, *self._show_args())
            return

        self._standalone = QtWidgets.QApplication.instance() is None
        if self._standalone:
            self._event_loop = QtWidgets.QApplication([])
            self._event_loop.setQuitOnLastWindowClosed(False)
        else:
            self._event_loop = QtWidgets.QApplication.instance()

        self.init_ui()
        execute_in_main_thread(self.ui.show, *self._show_args())

        if self._standalone:
            sys.exit(self._event_loop.exec_())

    def refresh(self):
        '''Refresh the Hotline UI'''
        mode = self.get_mode()
        self.ui.input_field.placeholder = mode.prompt
        self.ui.input_field.clear()
        self.ui.mode_button.setText(mode.short_name)
        self.ui.commandlist.items = [c.name for c in mode.commands]

    def on_prev_mode(self):
        self.prev_mode()
        self.refresh()

    def on_next_mode(self):
        self.next_mode()
        self.refresh()

    def on_accept(self):
        result = self.execute(self.ui.text())
        self.ui.input_field.clear()

        if result:
            self.ui.console.show()

        if result is flags.DontHide:
            return

        if not isinstance(result, Exception):
            self.ui.hide()

    def on_reject(self):
        self.ui.hide()

    def get_user_input(self, prompt=None, options=None):
        '''Get input from user using a modeless Hotline Dialog'''

        self.ui._hide()
        pos = self.ui.pos()
        dialog = Dialog()
        dialog.setStyleSheet(self.context.style)
        if prompt:
            dialog.input_field.placeholder = prompt
            dialog.input_field.clear()
        if options:
            dialog.commandlist.items = options
        accepted = dialog.exec_(self.context.animation, (pos.x(), pos.y()))
        if accepted:
            return dialog.text()

    def execute(self, command):
        '''Execute a command using the current mode'''

        mode = self.get_mode()
        result = None
        with redirect_stream(stdout=self.stream, stderr=self.stream):
            try:
                result = mode(command)
                if result and result not in flags._list:
                    print(result)
            except Exception as e:
                result = e
                traceback.print_exc()
        return result

    def get_mode(self, name=None):
        '''Get active mode'''

        if not name:
            return self.context.modes[0]

        for mode in self.context.modes:
            if mode.name == name or mode.short_name == name:
                return mode

        raise NameError('Can not find mode named: '+ name)

    def set_mode(self, mode):
        '''Set active mode by name'''

        while True:
            if mode == self.context.modes[0]:
                signals.ModeChanged(self.context.modes[0])
                return
            self.context.modes.rotate(-1)


    def set_modes(self, *modes):
        '''Set available self.context.modes'''

        self.context.modes.clear()
        self.context.modes.extend(self.modes)

    def add_modes(self, *modes):
        '''Add mode'''

        self.context.modes.extend([m(self) for m in modes])

    def next_mode(self):
        '''Rotate to the next mode'''

        self.context.modes.rotate(-1)

    def prev_mode(self):
        '''Rotate to the previous mode'''

        self.context.modes.rotate()
