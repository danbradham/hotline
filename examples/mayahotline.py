#Get wrapinstance from PyQt or PySide
try:
    import sip
    wrapinstance = sip.wrapinstance
except ImportError:
    import shiboken
    wrapinstance = shiboken.wrapInstance

from hotline import HotLine
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.mel as mel

def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapinstance(long(ptr), QtCore.QObject)

@HotLine.add_mode("PY")
def python_handler(input_str):
    cmds.evalDeferred(input_str)
    cmds.repeatLast(addCommand='python("{0}")'.format(input_str))

@HotLine.add_mode("MEL")
def mel_handler(input_str):
    mel.eval(input_str)
    cmds.repeatLast(addCommand=input_str)

@HotLine.add_mode("SEL")
def sel_handler(input_str):
    cmds.select(input_str, replace=True)

@HotLine.add_mode("REN")
def ren_handler(input_str):
        nodes = [(node, index) 
            for index, node in enumerate(cmds.ls(sl=True, long=True))]
        sorted_nodes = sorted(nodes, 
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
                        node = cmds.rename(node,
                            name.replace('+', '') + node_shortname)
                    elif name.startswith('+'):
                        node = cmds.rename(node,
                            node_shortname + name.replace('+', ''))
                    else:
                        print "+ symbols belong at the front or the end of a string"
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
                        node = cmds.rename(node,
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

@HotLine.add_mode("NODE")
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

try:
    hl.enter()
except NameError:
    hl = HotLine(getMayaWindow())
    hl.enter()

