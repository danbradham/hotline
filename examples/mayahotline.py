'''
mayahotline.py
--------------
An example of using hotline in Autodesk Maya.
Place in your maya scripts directory and bind a key to:
    import mayahotline
    mayahotline.show()
'''

#Get wrapinstance from PyQt or PySide
try:
    import sip
    wrapinstance = sip.wrapinstance
except ImportError:
    import shiboken
    wrapinstance = shiboken.wrapInstance
import re

import hotline
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.mel as mel


def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapinstance(long(ptr), QtCore.QObject)


def py_handler(input_str):
    cmds.evalDeferred(input_str)
    cmds.repeatLast(addCommand='python("{0}")'.format(input_str))


def mel_handler(input_str):
    mel.eval(input_str)
    cmds.repeatLast(addCommand=input_str)


def sel_handler(input_str):
    cmds.select(input_str, replace=True)


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


def show():
    '''Show HotLine ui.'''

    try:
        hl.enter()
    except NameError:
        #Instantiate HotLine as child of Maya Window
        hl = hotline.HotLine(getMayaWindow())
        #Instantiate Modes
        PY = hotline.Mode("PY", py_handler, syntax="Python")
        MEL = hotline.Mode("MEL", mel_handler)
        SEL = hotline.Mode("SEL", sel_handler, completion_list_meth=cmds.ls)
        REN = hotline.Mode("REN", ren_handler)
        NODE = hotline.Mode("NODE", node_handler)
        #Add Modes to HotLine instance
        hl.add_mode(PY)
        hl.add_mode(MEL)
        hl.add_mode(SEL)
        hl.add_mode(REN)
        hl.add_mode(NODE)
        #Show Window
        hl.enter()
