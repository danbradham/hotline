'''
mayactx.py
--------------
An example of using hotline in Autodesk Maya.
Place in your maya scripts directory and bind a key to:
    import hotline
    from hotline.contexts import mayactx

    hotline.show()
'''

#Get wrapinstance from PyQt or PySide
try:
    import sip
    wrapinstance = sip.wrapinstance
    from PyQt4 import QtGui, QtCore
except ImportError:
    import shiboken
    wrapinstance = shiboken.wrapInstance
    from PySide import QtGui, QtCore
import re
import inspect
import hotline
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.mel as mel

CMDS_CALLABLES = [name for name, data in inspect.getmembers(cmds, callable)]


@hotline.add_mode("PY", completer_list=CMDS_CALLABLES, syntax="Python")
def py_handler(input_str):
    cmds.evalDeferred(input_str)
    cmds.repeatLast(addCommand='python("{0}")'.format(input_str))


@hotline.add_mode("MEL", completer_list=CMDS_CALLABLES)
def mel_handler(input_str):
    mel.eval(input_str)
    cmds.repeatLast(addCommand=input_str)


@hotline.add_mode("SEL", completer_fn=cmds.ls)
def sel_handler(input_str):
    cmds.select(input_str, replace=True)


@hotline.add_mode("REN")
def ren_handler(input_str):
        nodes = [(node, index)
                 for index, node in enumerate(cmds.ls(sl=True, long=True))]
        sorted_nodes = sorted(
            nodes,
            key=lambda (node, index): len(node.split('|')),
            reverse=True)
        rename_strings = input_str.split()

        cmds.undoInfo(openChunk=True)

        for rename_string in rename_strings:
            remMatch = re.search('\-', rename_string)
            addMatch = re.search('\+', rename_string)
            seq_length = rename_string.count('#')

            #Handle subtract tokens
            if remMatch:
                rename_string = rename_string.replace('-', '')
                for node, i in sorted_nodes:
                    node_shortname = node.split('|')[-1]
                    newName = node_shortname.replace(rename_string, '')
                    node = cmds.rename(node, newName)

            #Handle add tokens
            elif addMatch:
                for node, i in sorted_nodes:
                    name = rename_string
                    node_shortname = node.split('|')[-1]
                    if seq_length:
                        seq = str(i+1).zfill(seq_length)
                        name = name.replace('#' * seq_length, seq)
                    if name.endswith('+'):
                        node = cmds.rename(
                            node,
                            name.replace('+', '') + node_shortname)
                    elif name.startswith('+'):
                        node = cmds.rename(
                            node,
                            node_shortname + name.replace('+', ''))
                    else:
                        print "+ belongs at start or end of a string"
            else:

                #Handle Search Replace
                if len(rename_strings) == 2:
                    seq_length = rename_strings[-1].count('#')
                    for node, i in sorted_nodes:
                        node_shortname = node.split('|')[-1]
                        name = rename_strings[-1]
                        if seq_length:
                            seq = str(i+1).zfill(seq_length)
                            name = name.replace('#' * seq_length, seq)
                        node = cmds.rename(
                            node,
                            node_shortname.replace(rename_strings[0], name))
                    break

                #Handle Full Rename
                elif len(rename_strings) == 1:
                    for node, i in sorted_nodes:
                        name = rename_string
                        if seq_length:
                            seq = str(i+1).zfill(seq_length)
                            name = name.replace('#' * seq_length, seq)
                        cmds.rename(node, name)

        cmds.undoInfo(closeChunk=True)


@hotline.add_mode("NODE", completer_fn=cmds.allNodeTypes)
def node_handler(input_str):
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


def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapinstance(long(ptr), QtCore.QObject)


@hotline.set_show()
def show():
    '''Show HotLine ui.'''

    try:
        hl.enter()
    except NameError:
        #Instantiate HotLine as child of Maya Window
        hl = hotline.HotLine(getMayaWindow())
        hl.enter()
