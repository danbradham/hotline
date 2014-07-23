from .views import Base, Dock, Editor
from .events import *
from contexts import CTX
import sys
import time
import logging
logger = logging.getLogger("hotline.hotline")


class HotLine(Base):

    def __init__(self, parent=None):
        super(HotLine, self).__init__(parent)

        self.multiline = False


        # Setup our event receivers
        # ToggleMultiline.calls(self.toggle_multiline)

    @receives(ToggleMultiline)
    def toggle_multiline(self):
        self.multiline = False if self.multiline else True
        return self.multiline

    @receives(ToggleMultiline.completed)
    def multiline_toggled(self, results):
        print results
        print type(results)

    @receives(TogglePin)
    def toggle_pin(self):
        logge.debug("")


def show(debug=False):
    '''Start up the QApplication if necessary'''
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    logger.debug("Starting HotLine with {0}. Available modes: {1}".format(
        CTX.__class__.__name__, CTX.modes))
    CTX.show(HotLine)
