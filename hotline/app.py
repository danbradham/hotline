from __future__ import division
import sys
import traceback
from .config import config_path
from .config import Config
from .store import Store
from .contexts import CTX
from .ui import UI
from .history import History
from .messages import (ToggleMultiline, ToggleAutocomplete, TogglePin,
                       ToggleToolbar, Execute, NextHistory, NextMode,
                       PrevHistory, PrevMode, ShowDock, ShowHelp,
                       ClearOutput, AdjustSize, Store_Run, Store_Save,
                       Store_Load, Store_Delete, Store_Refresh, Started,
                       Store_Evaluate, WriteOutput)
from .shout import shout
import logging
logger = logging.getLogger("hotline.hotline")


class HotLine(object):

    instance = None

    def __init__(self):

        self.config = Config(config_path("config.json"))

        if self.config.get('debug', None):
            logger.setLevel(logging.DEBUG)

        self.ui = None
        self.ctx = CTX(self)
        self._multiline = False
        self._autocomplete = False
        self._pinned = False
        self.history = History()
        self.store = Store(self, config_path("store.json"))
        shout(Started)

    @property
    def multiline(self):
        return self._multiline

    @multiline.setter
    def multiline(self, value):
        self._multiline = value
        shout(ToggleMultiline)

    def toggle_multiline(self):
        self.multiline = not self.multiline

    @property
    def autocomplete(self):
        return self._autocomplete

    @autocomplete.setter
    def autocomplete(self, value):
        self._autocomplete = value
        shout(ToggleAutocomplete)

    def toggle_autocomplete(self):
        self.autocomplete = not self.autocomplete

    @property
    def pinned(self):
        return self._pinned

    @pinned.setter
    def pinned(self, value):
        self._pinned = value
        shout(TogglePin)

    def toggle_pin(self):
        self.pinned = not self.pinned

    def toggle_toolbar(self):
        shout(ToggleToolbar)

    def run(self, input_str):
        output_str = "{}:\n{}\n\n".format(self.ctx.mode.name, input_str)
        shout(WriteOutput, output_str)

        try:
            self.ctx.run(input_str)
            self.history.add(self.ctx.mode, input_str)
            shout(Execute, True)
        except:
            exc = "".join(traceback.format_exception(*sys.exc_info()))
            shout(WriteOutput, exc)
            shout(Execute, False)

    def set_mode(self, name):
        self.ctx.set_mode(name)
        shout(NextMode, self.ctx.mode)

    def next_mode(self):
        self.ctx.next_mode()
        shout(NextMode, self.ctx.mode)

    def prev_mode(self):
        self.ctx.prev_mode()
        shout(PrevMode, self.ctx.mode)

    def next_hist(self):
        mode, text = self.history.next()
        shout(NextHistory, mode, text)

    def prev_hist(self):
        mode, text = self.history.prev()
        shout(PrevHistory, mode, text)

    def show(self):
        '''Shows a PySide UI to control the app. Parenting of the UI is handled
        by different subclasses of :class:`UI`. You can set the context using
        the "CONTEXT" key of your configuration.'''

        if not self.ui:
            self.ui = UI.create(self)
            self.store.evaluate(self.ctx.modes)
        self.ui.enter()
        shout(NextMode, self.ctx.mode)


def show(*args, **kwargs):
    '''Convenience method to show one instance of a HotLine ui.'''

    if not HotLine.instance:
        HotLine.instance = HotLine(*args, **kwargs)

    HotLine.instance.show()
