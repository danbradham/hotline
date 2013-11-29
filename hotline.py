'''
HotLine
Dan Bradham
danielbradham@gmail.com
http://danbradham.com

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
import inspect
import pymel as pm

def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)


class HotField(QtGui.QLineEdit):
    '''QLineEdit with history and dropdown completion.'''

    def __init__(self, parent=None):
        super(HotField, self).__init__(parent)
        self.history = []
        self.history_index = 0
        self.node_types = cmds.allNodeTypes()
        self.mel_callables = [name for name, data in inspect.getmembers(cmds, callable)]
        self.py_callables = ['cmds.' + name for name in self.mel_callables]

        #Dropdown Completer
        self.completer_list = QtGui.QStringListModel(self.py_callables)
        self.completer = QtGui.QCompleter(self.completer_list, self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(self.completer)

    def setup_completer(self, mode):
        '''Change completer word list.'''

        completion_list = {
        "PY": self.py_callables,
        "MEL": self.mel_callables,
        "SEL": cmds.ls(),
        "REN": [],
        "NODE": self.node_types}[mode]
        self.completer_list.setStringList(completion_list)

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

    modes = ['PY', 'MEL', 'SEL', 'REN', 'NODE']

    def __init__(self, parent=getMayaWindow()):
        super(HotLine, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Popup|QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
        self.resize(400, 24)
        self.setObjectName('HotLine')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.mode = 0

        self.hotfield = HotField()
        self.hotfield.returnPressed.connect(self.eval_hotfield)
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
        if self.mode == len(self.modes) - 1:
            self.mode = 0
        else:
            self.mode += 1

        #set hotfield completer
        self.hotfield.setup_completer(self.modes[self.mode])
        self.mode_button.setText(self.modes[self.mode])
        self.hotfield.setFocus()

    def eval_hotfield(self):
        input_str = self.hotfield.text()
        self.hotfield.history.append(input_str)
        self.hotfield.history_index = len(self.hotfield.history)
        if self.mode == 0:
            cmds.evalDeferred(input_str)
            cmds.repeatLast(addCommand='python("{0}")'.format(input_str))
        elif self.mode == 1:
            mel.eval(input_str)
            cmds.repeatLast(addCommand=input_str)
        elif self.mode == 2:
            cmds.select(input_str, replace=True)
        elif self.mode == 3:
            self.rename(str(input_str))
        elif self.mode == 4:
            self.create_node(input_str)
        self.exit()

    def create_node(self, input_str):
        input_buffer = input_str.split()
        if len(input_buffer) > 1:
            node_type, node_name = input_buffer
        else:
            node_type = input_buffer[0]
            node_name = None

        node_class = cmds.getClassification(node_type)

        #Wrap node creation and naming in a single chunk
        cmds.undoInfo(openChunk=True)

        if node_class:
            if "utility" in node_class[0].lower():
                node = cmds.shadingNode(node_type, asUtility=True)
            elif "shader" in node_class[0].lower():
                node = cmds.shadingNode(node_type, asShader=True)
            elif "texture" in node_class[0].lower():
                node = cmds.shadingNode(node_type, asTexture=True)
            elif "rendering" in node_class[0].lower():
                node = cmds.shadingNode(node_type, asRendering=True)
            elif "postprocess" in node_class[0].lower():
                node = cmds.shadingNode(node_type, asPostProcess=True)
            elif "light" in node_class[0].lower():
                node = cmds.shadingNode(node_type, asLight=True)
            else:
                node = cmds.createNode(node_type)
        else:
            node = cmds.createNode(node_type)

        if node_name:
            cmds.rename(node, node_name.replace('\"', ''))

        cmds.undoInfo(closeChunk=True)

    def rename(self, r_string):
            '''string processing'''
            nodes = cmds.ls(sl=True, long=True)
            rename_strings = r_string.split()

            cmds.undoInfo(openChunk=True)

            for rename_string in rename_strings:
                remMatch = re.search('\-', rename_string)
                addMatch = re.search('\+', rename_string)
                seq_length = rename_string.count('#')

                #Handle subtract tokens
                if remMatch:
                    rename_string = rename_string.replace('-', '')
                    for node in nodes:
                        node_shortname = node.split('|')[-1]
                        newName = node_shortname.replace(rename_string, '')
                        node = cmds.rename(node, newName)

                #Handle add tokens
                elif addMatch:
                    for i, node in enumerate(nodes):
                        name = rename_string
                        node_shortname = node.split('|')[-1]
                        if seq_length:
                            seq = str(i+1).zfill(seq_length)
                            name = name.replace('#' * seq_length, seq)
                        if name.endswith('+'):
                            node = cmds.rename(node, name.replace('+', '') + node_shortname)
                        elif name.startswith('+'):
                            node = cmds.rename(node, node_shortname + name.replace('+', ''))
                        else:
                            print "+ symbols belong at the front or the end of a string"
                else:

                    #Handle Search Replace
                    if len(rename_strings) == 2:
                        seq_length = rename_strings[-1].count('#')
                        for i, node in enumerate(nodes):
                            node_shortname = node.split('|')[-1]
                            name = rename_strings[-1]
                            if seq_length:
                                seq = str(i+1).zfill(seq_length)
                                name = name.replace('#' * seq_length, seq)
                            node = cmds.rename(node, node_shortname.replace(rename_strings[0], name))
                        break

                    #Handle Full Rename
                    elif len(rename_strings) == 1:
                        for i, node in enumerate(nodes):
                            name = rename_string
                            if seq_length:
                                seq = str(i+1).zfill(seq_length)
                                name = name.replace('#' * seq_length, seq)
                            cmds.rename(node, name)

            cmds.undoInfo(closeChunk=True)

    def enter(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x(), pos.y())
        self.show()
        self.hotfield.setFocus()

    def exit(self):
        self.hotfield.clear()
        self.close()

if __name__ == '__main__':
    hl = HotLine()
    hl.enter()
