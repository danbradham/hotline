'''
mayactx.py
--------------
An example of using hotline in Autodesk Maya.
'''

import re
import inspect
from functools import partial
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from maya.utils import executeInMainThreadWithResult as execInMain
import sys
import __main__
from .context import Context, add_mode
from ..messages import WriteOutput
from ..shout import shout


setattr(__main__, "execInMain", execInMain)
CMDS_CALLABLES = [name for name, data in inspect.getmembers(cmds, callable)]


class MayaOutputPipe(object):

    callback_id = None
    stream = sys.__stdout__
    redirect = False
    filters = (
        OpenMaya.MCommandMessage.kDisplay,
        OpenMaya.MCommandMessage.kError,
        OpenMaya.MCommandMessage.kResult,
        OpenMaya.MCommandMessage.kStackTrace,
        OpenMaya.MCommandMessage.kWarning,
        OpenMaya.MCommandMessage.kInfo,
    )
    filter_prefix = {
        OpenMaya.MCommandMessage.kDisplay: '',
        OpenMaya.MCommandMessage.kError: '[Error] ',
        OpenMaya.MCommandMessage.kResult: '',
        OpenMaya.MCommandMessage.kStackTrace: '',
        OpenMaya.MCommandMessage.kWarning: '[Warning] ',
        OpenMaya.MCommandMessage.kInfo: '[Info] ',
        OpenMaya.MCommandMessage.kHistory: '[History] '
    }

    @classmethod
    def set_stream(cls, stream):
        '''Defaults to sys.__stdout__. Stream must have a write and flush
        methods.
        '''

        cls.stream = stream

    @classmethod
    def set_filters(cls, *msg_types):
        '''MCommandMessage types to filter.

        OpenMaya.MCommandMessage.kDisplay
        OpenMaya.MCommandMessage.kError
        OpenMaya.MCommandMessage.kResult
        OpenMaya.MCommandMessage.kStackTrace
        OpenMaya.MCommandMessage.kWarning
        OpenMaya.MCommandMessage.kHistory
        OpenMaya.MCommandMessage.kInfo
        '''

        cls.filters = msg_types

    @classmethod
    def set_redirect(cls, value):
        '''True redirects all output away from the script editor.'''

        cls.redirect = value

    @classmethod
    def activate(cls):
        '''Setup the MCommandMessage callback.'''

        if not cls.callback_id:
            cid = OpenMaya.MCommandMessage.addCommandOutputFilterCallback(
                cls.callback)
            cls.callback_id = cid

    @classmethod
    def deactivate(cls):
        '''Remove the MCommandMessage callback'''

        if cls.callback_id:
            OpenMaya.MMessage.removeCallback(cls.callback_id)
        cls.callback_id = None

    @staticmethod
    def callback(msg, msg_type, filter_output, user_data):
        '''Write command output to MayaOutputPipe stream object.'''

        OpenMaya.MScriptUtil.setBool(filter_output, MayaOutputPipe.redirect)

        if msg_type in MayaOutputPipe.filters:
            prefix = MayaOutputPipe.filter_prefix[msg_type]
            MayaOutputPipe.stream.write(prefix + str(msg) + '\n')
            MayaOutputPipe.stream.flush()


class MayaOutStream(object):

    def write(self, message):
        shout(WriteOutput, message)

    def flush(self):
        pass


class MayaContext(Context):

    def __init__(self, app):
        super(MayaContext, self).__init__(app)
        MayaOutputPipe.set_stream(MayaOutStream())
        MayaOutputPipe.activate()

    @add_mode("PY", completer_list=CMDS_CALLABLES, syntax="Python")
    def py_handler(self, input_str):
        prev_chunk = cmds.undoInfo(q=True, chunkName=True)
        cmds.undoInfo(openChunk=True)
        try:
            execInMain(input_str)
            setattr(__main__, "last_py_cmd", input_str)
            cmds.repeatLast(addCommand='python("execInMain(last_py_cmd)")')
            cmds.undoInfo(closeChunk=True)
        except:
            cmds.undoInfo(closeChunk=True)
            if not cmds.undoInfo(q=True, chunkName=True) == prev_chunk:
                cmds.undo()
            raise

    @add_mode("MEL", completer_list=CMDS_CALLABLES)
    def mel_handler(self, input_str):
        prev_chunk = cmds.undoInfo(q=True, chunkName=True)
        cmds.undoInfo(openChunk=True)
        try:
            execInMain(partial(mel.eval, input_str))
            cmds.repeatLast(addCommand=input_str)
            cmds.undoInfo(closeChunk=True)
        except:
            cmds.undoInfo(closeChunk=True)
            if not cmds.undoInfo(q=True, chunkName=True) == prev_chunk:
                cmds.undo()
            raise

    @add_mode("SEL", completer_fn=cmds.ls)
    def sel_handler(self, input_str):
        cmds.select(input_str, replace=True)

    @add_mode("REN")
    def ren_handler(self, input_str):
        nodes = [(node, index)
                 for index, node in enumerate(cmds.ls(sl=True, long=True))]
        if not nodes:
            raise NameError("Select some nodes first!")

        prev_chunk = cmds.undoInfo(q=True, chunkName=True)
        cmds.undoInfo(openChunk=True)
        try:
            do_rename(nodes, input_str)
            cmds.undoInfo(closeChunk=True)
        except:
            cmds.undoInfo(closeChunk=True)
            if not cmds.undoInfo(q=True, chunkName=True) == prev_chunk:
                cmds.undo()
            raise

    @add_mode("CNCT")
    def cnct_handler(self, input_str):
        nodes = cmds.ls(sl=True, long=True)
        if len(nodes) < 2:
            raise NameError("Must have multiple nodes selected.")
        src_node = nodes[0]
        dest_nodes = nodes[1:]

        connections = input_str.split(",")
        for c in connections:
            c_ends = c.split()
            if len(c_ends) != 2:
                raise AttributeError("Must input a source and dest attr.")
            src, dest = c_ends
            for dest_node in dest_nodes:
                cmds.connectAttr(
                    "{}.{}".format(src_node, src),
                    "{}.{}".format(dest_node, dest),
                    force=True)

    @add_mode("NODE", completer_fn=cmds.allNodeTypes)
    def node_handler(self, input_str):
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
        prev_chunk = cmds.undoInfo(q=True, chunkName=True)
        cmds.undoInfo(openChunk=True)
        try:
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
        except:
            cmds.undoInfo(closeChunk=True)
            if not cmds.undoInfo(q=True, chunkName=True) == prev_chunk:
                cmds.undo()
            raise



def do_rename(nodes, input_str):
    sorted_nodes = sorted(
        nodes,
        key=lambda (node, index): len(node.split('|')),
        reverse=True)
    rename_strings = input_str.split()

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
