from PySide import QtGui
from .ui import UI
from .help import help_string
from .contexts import CTX
from .shout import has_ears, shout, hears
from .messages import (ToggleMultiline, ToggleAutocomplete, TogglePin,
                       ToggleToolbar, Execute, NextHistory, NextMode,
                       PrevHistory, PrevMode, ShowDock, ShowHelp,
                       ClearOutput, AdjustSize, Store_Run, Store_Save,
                       Store_Load, Store_Delete, Store_Refresh)
import traceback
import sys
import logging
logger = logging.getLogger("hotline.hotline")


@has_ears
class HotLine(UI):

    def __init__(self, ctx=CTX, parent=None):
        super(HotLine, self).__init__(ctx, parent)
        CTX.mode.setup(self)

    @hears(ShowDock)
    def show_dock(self):
        self.dock.show()

    @hears(ToggleAutocomplete)
    def toggle_autocomplete(self):
        CTX.autocomplete = False if CTX.autocomplete else True
        self.auto_button.setChecked(CTX.autocomplete)

    @hears(ToggleMultiline)
    def toggle_multiline(self):
        CTX.multiline = False if CTX.multiline else True
        self.multi_button.setChecked(CTX.multiline)
        self.adjust_size()

    @hears(TogglePin)
    def toggle_pinned(self):
        CTX.pinned = False if CTX.pinned else True
        self.pin_button.setChecked(CTX.pinned)

    @hears(NextMode)
    def next_mode(self):
        CTX.next_mode()

    @hears(PrevMode)
    def prev_mode(self):
        CTX.prev_mode()

    @hears(Execute)
    def key_execute(self):
        input_str = self.editor.toPlainText()
        CTX.history.add(input_str)
        output_str = "{}:\n{}\n\n".format(CTX.mode.name, input_str)
        self.output.write(output_str)

        try:
            CTX.run(input_str)
            self.editor.clear()
        except:
            self.output.write(
                "".join(traceback.format_exception(*sys.exc_info())))
            self.output.show()
            self.dock.widget.setCurrentIndex(0)

        self.exit()

    @hears(ShowHelp)
    def show_help(self):
        self.output.write(help_string)

    @hears(ClearOutput)
    def clear_output(self):
        self.output.clear()

    @hears(PrevHistory)
    def key_prev(self):
        self.editor.setText(CTX.history.prev())

    @hears(NextHistory)
    def key_next(self):
        self.editor.setText(CTX.history.next())


def show(debug=False):
    '''Start up the QApplication if necessary'''
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug("Starting HotLine with {0}. Available modes: {1}".format(
        CTX.__class__.__name__, CTX.modes))
    HotLine.show()
