from __future__ import division
import os
import shutil
import sys
import traceback
from .utils import rel_path, config_path
from .config import Config, Store
from .contexts import CTX
from .ui import UI
from .history import History
from .messages import (ToggleMultiline, ToggleAutocomplete, TogglePin,
                       ToggleToolbar, Execute, NextHistory, NextMode,
                       PrevHistory, PrevMode, ShowDock, ShowHelp,
                       ClearOutput, AdjustSize, Store_Run, Store_Save,
                       Store_Load, Store_Delete, Store_Refresh, Started,
                       WriteOutput)
from .shout import shout
import logging
logger = logging.getLogger("hotline.hotline")

HL_HOME = os.environ.get(
    "HOTLINE_CFG",
    os.path.join(os.path.expanduser("~"), "hotline")
)


class HotLine(object):

    instance = None

    def __init__(self):

        if not os.path.exists(HL_HOME):
            shutil.copytree(rel_path("conf"), HL_HOME)

        self.config = Config(config_path("config.json"))

        if self.config.get('debug', None):
            logger.setLevel(logging.DEBUG)

        self.ui = None
        self.ctx = CTX(self)
        self.multiline = False
        self.autocomplete = False
        self.pinned = False
        self.history = History()
        self.store = Store(config_path("store.json"))
        shout(Started)

    def toggle_multiline(self):
        self.multiline = False if self.multiline else True
        shout(ToggleMultiline)

    def toggle_autocomplete(self):
        self.autocomplete = False if self.autocomplete else True
        shout(ToggleAutocomplete)

    def toggle_pin(self):
        self.pinned = False if self.pinned else True
        shout(TogglePin)

    def toggle_toolbar(self):
        shout(ToggleToolbar)

    def run(self, input_str):
        output_str = "{}:\n{}\n\n".format(self.ctx.mode.name, input_str)
        shout(WriteOutput, output_str)

        try:
            self.ctx.run(input_str)
            shout(Execute, True)
        except:
            exc = "".join(traceback.format_exception(*sys.exc_info()))
            shout(WriteOutput, exc)
            shout(Execute, False)

    def next_mode(self):
        self.ctx.next_mode()
        shout(NextMode, self.ctx.mode)

    def prev_mode(self):
        self.ctx.prev_mode()
        shout(PrevMode, self.ctx.mode)

    def next_hist(self):
        text = self.history.next()
        shout(NextHistory, text)

    def prev_hist(self):
        text = self.history.prev()
        shout(PrevHistory, text)

    def store_evaluate(self):
        for mode in self.ctx.modes:
            for name, data in self.store.iteritems():
                if data["mode"] == mode.name:
                    self.store_add_item(name)
                    if data["autoload"]:
                        mode.handler(data["command"])

    def show(self):
        '''Shows a PySide UI to control the app. Parenting of the UI is handled
        by different subclasses of :class:`UI`. You can set the context using
        the "CONTEXT" key of your configuration.'''

        if not self.ui:
            self.ui = UI.create(self)
        self.ui.enter()
        shout(NextMode, self.ctx.mode)


def show(*args, **kwargs):
    '''Convenience method to show one instance of a HotLine ui.'''

    if not HotLine.instance:
        HotLine.instance = HotLine(*args, **kwargs)

    HotLine.instance.show()
