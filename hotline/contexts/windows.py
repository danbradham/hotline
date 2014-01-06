'''
An example of HotLine running with a global hotkey anywhere in windows.
'''

import pyhk
import signal
import subprocess
import hotline
from PyQt4 import QtGui, QtCore


def py_handler(input_str):
    p = subprocess.Popen(["python", "-c", input_str],
                         stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)

def cmd_handler(input_str):
    subprocess.Popen(input_str.split(), stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)


def main():

    PY = hotline.Mode("PY", py_handler, syntax='PYTHON')
    CMD = hotline.Mode("CMD", cmd_handler)
    app = QtGui.QApplication(sys.argv)
    hl = hotline.HotLine()
    hl.add_mode(PY)
    hl.add_mode(CMD)
    hl.enter()

    #Setup a global hotkey using pyhk
    key = pyhk.pyhk()
    key.addHotkey(['Ctrl', 'Alt', 'H'], hl.enter)

    #Handle sigint
    def sigint_handler(*args):
        sys.exit(app.exec_())
    signal.signal(signal.SIGINT, sigint_handler)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
