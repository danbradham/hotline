import sip
sip.setapi("QString", 2)
from PyQt4 import QtGui, QtCore

KEYS = {
    "Toggle Multiline": "Ctrl+M",
    "Toggle Something": "Ctrl+X",
    "Toggle Modes": "Tab",
    "Execute": "Enter",
    "Previous in History": "Up",
    "Next in History": "Down"
}

def print_keys(keys):
    for k, v in keys.iteritems():
        print k, v
        seq = QtGui.QKeySequence.fromString(v)[0]
        print seq

if __name__ == "__main__":
    print_keys(KEYS)