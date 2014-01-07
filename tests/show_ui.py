'''
A quick test of HotLine running with a global hotkey anywhere in windows.
'''
import sip
for datatype in ['QString', 'QVariant', 'QUrl', 'QDate',
                 'QDateTime', 'QTextStream', 'QTime']:
    sip.setapi(datatype, 2)

import sys
import signal
import hotline
from PyQt4 import QtGui


@hotline.add_mode("PY", syntax="Python")
def py_handler(input_str):
    print input_str


def main():

    app = QtGui.QApplication(sys.argv)
    hl = hotline.HotLine()
    hl.enter()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
