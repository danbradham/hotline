'''
An example of HotLine running with a global hotkey anywhere in windows.
'''

import sys
import os
import pyhk
import subprocess
import hotline
from PyQt4 import QtGui


def py_handler(input_str):
    p = subprocess.Popen(["python", "-c", input_str],
                         stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)


def cmd_handler(input_str):
    p = subprocess.Popen(input_str.split(), stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)


def exit(app):
    pid = os.getpid()
    os.kill(pid, 1)


def show():
    try:
        hl.enter()
    except NameError:
        PY = hotline.Mode("PY", py_handler, syntax='PYTHON')
        CMD = hotline.Mode("CMD", cmd_handler)
        app = QtGui.QApplication(sys.argv)
        hl = hotline.HotLine()
        hl.add_mode(PY)
        hl.add_mode(CMD)
        hl.enter()

        #Setup a global hotkey using pyhk
        key = pyhk.pyhk()
        key.addHotkey(['Ctrl', 'Alt', 'H'], show)
        key.addHotkey(['Ctrl', 'Alt', 'Q'], exit)

        app.exec_()
