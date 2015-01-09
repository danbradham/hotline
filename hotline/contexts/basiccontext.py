'''
Basic Context
-------------
'''

from .context import Context, add_mode
import sys


class BasicContext(Context):

    @add_mode("PY", syntax="Python")
    def py_handler(self, input_str):
        exec(input_str)

    def show(self, hotline_cls):
        from PySide import QtGui

        app = QtGui.QApplication(sys.argv)
        if not self.hotline:
            self.hotline = hotline_cls(self)
        self.hotline.show()
        sys.exit(app.exec_())
