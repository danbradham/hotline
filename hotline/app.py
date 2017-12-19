# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import traceback
from hotline.Qt import QtWidgets
from hotline.command import Command
from hotline.mode import Mode
from hotline.contexts import best_context
from hotline.widgets import Dialog
from hotline.utils import execute_in_main_thread, redirect_stream
from hotline.history import History, ModeCommand


class flags(object):
    class DontHide: pass
    class Hide: pass
    _list = [DontHide, Hide]


class HotlineMode(Mode):

    name = 'HotlineMode'
    label = 'HL'

    def show_console(self):
        self.app.ui.console.show()
        return flags.DontHide

    def toggle_pin(self):
        self.app.ui.pinned = not self.app.ui.pinned

    def gen_command(self):
        result = self.app.get_user_input('User Input')
        print result

    @property
    def commands(self):
        return [
            Command('Toggle Pin', self.toggle_pin),
            Command('Show Console', self.show_console),
            Command('Show Settings', self.show_console),
            Command('Multi-Command', self.gen_command)
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
        self.history = History()
        self.ui = None

    def init_ui(self):
        if self.ui:
            raise Exception('UI has already initialized')

        self.add_modes(HotlineMode)
        self.ui = Dialog(self.context.parent)
        self.ui.mode_button.show()
        self.ui.setStyleSheet(self.context.style)
        self.ui.mode_button.clicked.connect(self.on_next_mode)
        self.ui.hk_tab.activated.connect(self.on_next_mode)
        self.ui.hk_shift_tab.activated.connect(self.on_prev_mode)
        self.ui.hk_alt_f4.activated.connect(self.exit)
        self.ui.hk_ctrl_up.activated.connect(self.on_history_prev)
        self.ui.hk_ctrl_dn.activated.connect(self.on_history_next)
        self.ui.accepted.connect(self.on_accept)
        self.ui.rejected.connect(self.on_reject)
        self.refresh()

    def exit(self):
        if self._standalone:
            self._event_loop.setQuitOnLastWindowClosed(True)
            self._event_loop.quit()
            return

        self.ui.force_hide()

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
        mode = self.get_mode()
        self.ui.input_field.placeholder = mode.prompt
        self.ui.input_field.clear()
        self.ui.mode_button.setText(mode.label)
        self.ui.commandlist.items = [c.name for c in mode.commands]

    def on_history_prev(self):
        text = self.ui.text()
        is_partial_command = self.history.index == 0 and text
        if is_partial_command:
            self.history.insert(1, ModeCommand(self.get_mode(), text))

        item = self.history.prev()
        if item is None:
            return
        self.set_mode(item.mode)
        self.refresh()
        self.ui.input_field.setText(item.command)

    def on_history_next(self):
        item = self.history.next()
        if item is None:
            self.ui.input_field.setText('')
            return
        self.set_mode(item.mode)
        self.refresh()
        self.ui.input_field.setText(item.command)

    def on_prev_mode(self):

        self.prev_mode()
        self.refresh()

    def on_next_mode(self):

        self.next_mode()
        self.refresh()

    def on_accept(self):

        result = self.execute(self.ui.text())
        success = not isinstance(result, Exception)
        hide = success and result is not flags.DontHide

        if not success:
            self.ui.console.show()

        if success:
            self.history.add(ModeCommand(self.get_mode(), self.ui.text()))
            self.ui.input_field.clear()
            self.ui.commandlist.filter('')

        if hide:
            self.ui.hide()

    def on_reject(self):

        self.ui.hide()

    def get_user_input(self, prompt=None, options=None):
        '''Get input from user using a modeless Hotline Dialog'''

        self.ui.force_hide()
        pos = self.ui.pos()
        dialog = Dialog(self.context.parent)
        dialog.setStyleSheet(self.context.style)
        if prompt:
            dialog.input_field.placeholder = prompt
            dialog.input_field.clear()
        if options:
            dialog.commandlist.items = options
        accepted = dialog.exec_(self.context.animation, (pos.x(), pos.y()))
        user_input = dialog.text()
        if accepted:
            return user_input

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
            if mode.name == name or mode.label == name:
                return mode

        raise NameError('Can not find mode named: '+ name)

    def set_mode(self, mode):
        '''Set active mode by name or Mode object'''

        start = self.context.modes[0]
        if mode == start:
            return

        self.context.modes.rotate(-1)
        while not self.context.modes[0] == start:
            if mode == self.context.modes[0]:
                self.refresh()
                return
            self.context.modes.rotate(-1)

        raise Exception('Could not find: {}'.format(mode))

    def set_modes(self, *modes):
        '''Set available self.context.modes'''

        self.context.modes.clear()
        self.add_modes(*modes)

    def add_modes(self, *modes):
        '''Add mode'''

        self.context.modes.extend([m(self) for m in modes])

    def next_mode(self):
        '''Rotate to the next mode'''

        self.context.modes.rotate(-1)

    def prev_mode(self):
        '''Rotate to the previous mode'''

        self.context.modes.rotate()
