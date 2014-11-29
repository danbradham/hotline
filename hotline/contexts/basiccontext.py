'''
Basic Context
-------------
'''

from .context import Context, add_mode
from PySide import QtGui
import sys


class BasicContext(Context):

    @add_mode("PY", syntax="Python")
    def py_handler(self, input_str):
        exec(input_str)

    def show(self, hotline_cls):
        app = QtGui.QApplication(sys.argv)
        if not self.hotline:
            self.hotline = hotline_cls(self)
        self.hotline.show()
        sys.exit(app.exec_())
