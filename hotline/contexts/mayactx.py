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
from functools import partial
import hotline
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
from maya.utils import executeInMainThreadWithResult as execInMain
import maya.mel as mel
import __main__

CMDS_CALLABLES = [name for name, data in inspect.getmembers(cmds, callable)]


@hotline.add_mode("PY", completer_list=CMDS_CALLABLES, syntax="Python")
def py_handler(input_str):
    main = __main__.__dict__
    exec(input_str, main, main)
    cmds.repeatLast(
        addCommand='python("exec({0}, {1}, {1})")'.format(input_str, main))


@hotline.add_mode("MEL", completer_list=CMDS_CALLABLES)
def mel_handler(input_str):
    execInMain(partial(mel.eval, input_str))
    cmds.repeatLast(addCommand=input_str)


@hotline.add_mode("SEL", completer_fn=cmds.ls)
def sel_handler(input_str):
    cmds.select(input_str, replace=True)


@hotline.add_mode("REN")
def ren_handler(input_str):
        nodes = [(node, index)
                 for index, node in enumerate(cmds.ls(sl=True, long=True))]
        if not nodes:
            raise NameError("Select some nodes first!")
        sorted_nodes = sorted(
            nodes,
            key=lambda (node, index): len(node.split('|')),
            reverse=True)
        rename_strings = input_str.split()

        cmds.undoInfo(openChunk=True)

        for rename_string in rename_strings:
            remMatch = re.search('\-', rename_string)
            addMatch = re.search('\+', rename_string)
            seqMatch = re.search(r"(#+)(\((\d+)\))?", rename_string)
            start_index = 1
            seq_length = 0
            if seqMatch:
                seq_length = len(seqMatch.group(1))
                if seqMatch.group(3):
                    start_index = int(seqMatch.group(3))
                    rename_string = rename_string.replace(seqMatch.group(2),"")

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
                        seq = str(i+start_index).zfill(seq_length)
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
                    for node, i in sorted_nodes:
                        node_shortname = node.split('|')[-1]
                        name = rename_strings[-1]
                        if seq_length:
                            seq = str(i+start_index).zfill(seq_length)
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
                            seq = str(i+start_index).zfill(seq_length)
                            name = name.replace('#' * seq_length, seq)
                        cmds.rename(node, name)

        cmds.undoInfo(closeChunk=True)


@hotline.add_mode("NODE", completer_fn=cmds.allNodeTypes)
def node_handler(input_str):
    input_buffer = input_str.split()
    if len(input_buffer) > 1:
        node_type, node_name = input_buffer
        if "#" in node_name:
            raise NameError(
                "# symbol found in node name. "
                "This will completely fuck your maya scene. \n"
                "Try again without the #.")
    else:
        node_type = input_buffer[0]
        node_name = None

    #Wrap node creation and naming in a single chunk
    cmds.undoInfo(openChunk=True)

    if cmds.getClassification(node_type, satisfies="utility"):
        node = cmds.shadingNode(node_type, asUtility=True)
    elif cmds.getClassification(node_type, satisfies="shader"):
        node = cmds.shadingNode(node_type, asShader=True)
    elif cmds.getClassification(node_type, satisfies="texture"):
        node = cmds.shadingNode(node_type, asTexture=True)
    elif cmds.getClassification(node_type, satisfies="rendering"):
        node = cmds.shadingNode(node_type, asRendering=True)
    elif cmds.getClassification(node_type, satisfies="postprocess"):
        node = cmds.shadingNode(node_type, asPostProcess=True)
    elif cmds.getClassification(node_type, satisfies="light"):
        node = cmds.shadingNode(node_type, asLight=True)
    else:
        node = cmds.createNode(node_type)

    if node_name:
        cmds.rename(node, node_name.replace('\"', ''))

    cmds.undoInfo(closeChunk=True)


def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = long(OpenMayaUI.MQtUtil.mainWindow())
    if "shiboken" in globals():
        return wrapinstance(ptr, QtGui.QWidget)
    return wrapinstance(ptr, QtCore.QObject)


@hotline.set_show()
def show():
    '''Show HotLine ui.'''

    try:
        hotline.HotLine.instance.enter()
    except:
        #Instantiate HotLine as child of Maya Window
        hl = hotline.HotLine(getMayaWindow())
        hl.enter()
