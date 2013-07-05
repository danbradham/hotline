'''
HotLine
Dan Bradham 2013

A convenient popup script editor.
Up and down keys shuffle through HotLine History.
Tab key changes mode.

Set a hotkey to the following python script:

import maya.cmds as cmds
try:
    hl.enter()
except:
    from hotline import HotLine
    hl = HotLine()
    hl.enter()
'''
import re

import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
from PyQt4 import QtGui, QtCore
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import maya.mel as mel


def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)


class HotField(QtGui.QLineEdit):

    def __init__(self, parent=None):
        super(HotField, self).__init__(parent)
        self.history = []
        self.history_index = 0

    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress\
        and event.key() == QtCore.Qt.Key_Tab:
            self.parent().setMode()
            return True
        return QtGui.QLineEdit.event(self, event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            if self.history_index:
                self.history_index -= 1
                if self.text() and not self.text() in self.history:
                    self.history.append(self.text())
                self.setText(self.history[self.history_index])
        elif event.key() == QtCore.Qt.Key_Down:
            self.history_index += 1
            if self.history_index < len(self.history):
                self.setText(self.history[self.history_index])
            elif self.history_index == len(self.history):
                self.clear()
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)


class HotLine(QtGui.QDialog):
    '''HotLine, a hotbox script editor'''

    style = '''QPushButton {
                    border:0;
                    background: none;}
                QPushButton:pressed {
                    border:0;
                    color: rgb(0, 35, 55)}
                QLineEdit {
                    background-color: none;
                    border: 0;
                    border-bottom: 1px solid rgb(42, 42, 42);
                    padding-left: 10px;
                    padding-right: 10px;
                    height: 20;}
                QLineEdit:focus {
                    outline: none;
                    background: none;
                    border: 0;
                    height: 20;}'''

    def __init__(self, parent=getMayaWindow()):
        #Init my main window, and pass in the maya main window as it's parent
        super(HotLine, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Popup|QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
        self.resize(400, 24)
        self.setObjectName('HotLine')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.mode = 0

        self.hotfield = HotField()
        self.hotfield.returnPressed.connect(self.evalScript)
        self.mode_button = QtGui.QPushButton('PY')
        self.mode_button.clicked.connect(self.setMode)
        self.mode_button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.mode_button.setFixedWidth(50)
        self.layout = QtGui.QGridLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.hotfield, 0, 1)
        self.layout.addWidget(self.mode_button, 0, 0)
        self.setLayout(self.layout)

        self.setStyleSheet(self.style)

    def setMode(self):
        if self.mode == 3:
            self.mode = 0
            self.mode_button.setText('PY')
        elif self.mode == 0:
            self.mode = 1
            self.mode_button.setText('MEL')
        elif self.mode == 1:
            self.mode = 2
            self.mode_button.setText('SEL')
        elif self.mode == 2:
            self.mode = 3
            self.mode_button.setText('REN')
        self.hotfield.setFocus()

    def evalScript(self):
        input_str = self.hotfield.text()
        self.hotfield.history.append(input_str)
        self.hotfield.history_index = len(self.hotfield.history)
        if self.mode == 0:
            cmds.evalDeferred(input_str)
        elif self.mode == 1:
            mel.eval(input_str)
        elif self.mode == 2:
            cmds.select(input_str, replace=True)
        elif self.mode == 3:
            self.rename(str(input_str))
        self.exit()

    def rename(self, r_string):
            '''string processing'''
            nodes = cmds.ls(sl=True, long=True)
            rename_strings = r_string.split()

            for rename_string in rename_strings:
                remMatch = re.search('\-', rename_string)
                addMatch = re.search('\+', rename_string)
                seq_length = rename_string.count('#')

                #Handle subtract tokens
                if remMatch:
                    rename_string = rename_string.replace(r'-', '')
                    for node in nodes:
                        newName = node.replace(rename_string, '')
                        node = cmds.rename(node, newName)

                #Handle add tokens
                elif addMatch:
                    for i, node in enumerate(nodes):
                        if seq_length:
                            seq = str(i+1).zfill(seq_length)
                            rename_string = rename_string.replace('#' * seq_length, seq)
                        if rename_string.endswith(r'+'):
                            node = cmds.rename(node, rename_string.replace(r'+', '') + node)
                        elif rename_string.startswith(r'+'):
                            node = cmds.rename(node, node + rename_string.replace(r'+', ''))
                        else:
                            print "+ symbols belong at the front or the end of a string"
                else:

                    #Handle Search Replace
                    if len(rename_strings) == 2:
                        seq_length = rename_strings[-1].count('#')
                        for i, node in enumerate(nodes):
                            if seq_length:
                                seq = str(i+1).zfill(seq_length)
                                rename_strings[-1] = rename_strings[-1].replace('#' * seq_length, seq)
                            node = cmds.rename(node, node.replace(rename_strings[0], rename_strings[1]))
                        break

                    #Handle Full Rename
                    elif len(rename_strings) == 1:
                        for i, node in enumerate(nodes):
                            if seq_length:
                                seq = str(i+1).zfill(seq_length)
                                rename_string = rename_string.replace('#' * seq_length, seq)
                            cmds.rename(node, rename_string)

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.hotfield.setFocus()

    def exit(self):
        self.hotfield.clear()
        self.close()

if __name__ == '__main__':
    try:
        hl.enter()
    except:
        hl = HotLine()
        hl.enter()
