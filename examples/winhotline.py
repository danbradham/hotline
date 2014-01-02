'''
An example of HotLine running with a global hotkey anywhere in windows.
'''
import sys
sys.path.append("C:/PROJECTS/HotLine")
import pyhk
import signal
import subprocess
from hotline import HotLine
from PyQt4 import QtGui, QtCore


app = QtGui.QApplication(sys.argv)

hl = HotLine()

@hl.add_mode("PY")
def py_handler(input_str):
    p = subprocess.Popen(
        ["python", "-c", input_str],
        stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)

@hl.add_mode("CMD")
def cmd_handler(input_str):
    subprocess.Popen(input_str.split(), stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout)

hl.enter()

#Setup a global hotkey using pyhk
key = pyhk.pyhk()
key.addHotkey(['Ctrl', 'Alt', 'H'], hl.enter)

#Handle sigint
def sigint_handler(*args):
    sys.exit(app.exec_())
signal.signal(signal.SIGINT, sigint_handler)
sys.exit(app.exec_())