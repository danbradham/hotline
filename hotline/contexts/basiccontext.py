'''
Basic Context
-------------
'''

from ..context import Context, add_mode
from ..qt import QtGui
import sys
import platform
import os
import subprocess


class BasicContext(Context):

    @add_mode("PY", syntax="Python")
    def py_handler(self, input_str):
        exec(input_str)

    @add_mode("SH")
    def shell_handler(self, input_str):
        # plat = platform.system()
        # if plat == "Windows":
        #     os.startfile(os.path.abspath(script))
        # else:
        #     starter = {
        #         "Linux": "xdg-open",
        #         "Darwin": "open"
        #     }[plat]
        #     subprocess.call([starter, script])
        pass

    def show(self, hotline_cls):
        app = QtGui.QApplication(sys.argv)
        if not self.hotline:
            self.hotline = hotline_cls()
        self.hotline.show()
        sys.exit(app.exec_())
