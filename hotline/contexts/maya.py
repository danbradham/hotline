# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import namedtuple
import re
from Qt import QtWidgets, QtCore, QtGui
from functools import partial
from ..mode import Mode
from ..command import Command
from ..context import Context
from .. import styles
from ..helpers import new_process
from ..renamer import Renamer

MayaWidget = namedtuple('MayaWidget', 'path widget')


def get_maya_window():
    '''Get Maya MainWindow as a QWidget.'''

    for widget in QtWidgets.QApplication.instance().topLevelWidgets():
        if widget.objectName() == 'MayaWindow':
            return widget
    raise RuntimeError('Could not locate MayaWindow...')


def maya_widget_under_cursor():
    '''Get the MayaWidget under your mouse cursor'''

    app = QtWidgets.QApplication.instance()
    cursor = QtGui.QCursor()
    return maya_widget_at(cursor.pos())


def maya_widget_at(pos):
    '''Get a MayaWidget at QtCore.QPoint'''

    app = QtWidgets.QApplication.instance()
    widget = app.widgetAt(pos)
    return maya_widget(widget)


def maya_widget(widget):
    '''QWidget to MayaWidget'''

    from maya.OpenMayaUI import MQtUtil
    try:
        from shiboken import getCppPointer
    except ImportError:
        from shiboken2 import getCppPointer

    pointer = long(getCppPointer(widget)[0])
    path = MQtUtil.fullName(pointer)
    return MayaWidget(path, widget)


def find_child(widget, pattern):

    children = widget.findChildren(QtWidgets.QWidget, QtCore.QRegExp(pattern))
    if children:
        return [maya_widget(child) for child in children]


def active_panel_widget():
    from maya import cmds
    from maya.OpenMayaUI import MQtUtil
    try:
        from shiboken import wrapInstance
    except ImportError:
        from shiboken2 import wrapInstance

    panel = cmds.getPanel(withFocus=True)
    widget = wrapInstance(long(MQtUtil.findControl(panel)), QtWidgets.QWidget)
    return MayaWidget(panel, widget)


def active_m3dview_widget():
    '''Get active m3dview'''

    from maya.OpenMayaUI import M3dView
    try:
        from shiboken import wrapInstance
    except ImportError:
        from shiboken2 import wrapInstance

    active3dview = M3dView.active3dView()
    pointer = long(active3dview.widget())
    widget = wrapInstance(pointer, QtWidgets.QWidget)
    return maya_widget(widget)


def top_center(widget):
    '''Returns the top center screen coordinates of a widget'''

    rect = widget.rect()
    top = widget.mapToGlobal(rect.topLeft()).y()
    center = widget.mapToGlobal(rect.center()).x()
    return QtCore.QPoint(center, top)


class Python(Mode):

    name = 'Python'
    short_name = 'PY'
    commands = []
    prompt = 'python command'

    def execute(self, command):
        main = sys.modules['__main__'].__dict__
        try:
            code = compile(command, '<string>', 'eval')
            return eval(code, main, main)
        except SyntaxError:
            code = compile(command, '<string>', 'exec')
            exec code in main


class Mel(Mode):

    name = 'Mel'
    short_name = 'MEL'
    commands = [
        Command('Attribute Editor', 'AttributeEditor'),
        Command('ConnectionEditor', 'ConnectionEditor'),
        Command('Node Editor', 'NodeEditorWindow'),
        Command('Render View', 'RenderViewWindow'),
        Command('Content Browser', 'ContentBrowserWindow'),
        Command('Tool Settings', 'ToolSettingsWindow'),
        Command('Hypergraph Hierarchy', 'HypergraphHierarchyWindow'),
        Command('Hypergraph', 'HypergraphDGWindow'),
        Command('Asset Editor', 'AssetEditor'),
        Command('Attribute Spreadsheet', 'SpreadSheetEditor'),
        Command('Component Editor', 'ComponentEditor'),
        Command('Channel Control', 'ChannelControlEditor'),
        Command('Display Layers', 'DisplayLayerEditorWindow'),
        Command('File Path Editor', 'FilePathEditor'),
        Command('Namespace Editor', 'NamespaceEditor'),
        Command('Script Editor', 'ScriptEditor'),
        Command('Command Shell', 'CommandShell'),
        Command('Profiler', 'ProfilerTool'),
        Command('Evaluation Toolkit', 'EvaluationToolkit'),
        Command('Modeling Toolkit', 'showModelingToolkit'),
        Command('Paint Effects Window', 'PaintEffectsWindow'),
        Command('UV Editor', 'TextureViewWindow'),
        Command('Crease Sets', 'python "from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor();"'),
        Command('Graph Editor', 'GraphEditor'),
        Command('Time Editor', 'TimeEditorWindow'),
        Command('Trax Editor', 'CharacterAnimationEditor'),
        Command('Camera Sequencer', 'SequenceEditor'),
        Command('Quick Rig', 'QuickRigEditor'),
        Command('HIK Character Tools', 'HIKCharacterControlsTool'),
        Command('Blend Shape Editor', 'ShapeEditor'),
        Command('Pose Editor', 'PoseEditor'),
        Command('Expression Editor', 'ExpressionEditor'),
        Command('Render Settings/Globals', 'RenderGlobalsWindow'),
        Command('Hypershade', 'HypershadeWindow'),
        Command('Render Layer Editor', 'RenderLayerEditorWindow'),
        Command('Light Editor', 'callPython "maya.app.renderSetup.views.lightEditor.editor" "openEditorUI" {};'),
        Command('Render Flags', 'RenderFlagsWindow'),
        Command('Shading Group Attributes', 'ShadingGroupAttributeEditor'),
        Command('Animation Layer Relationships', 'AnimationLayerRelationshipEditor'),
        Command('Camera Set Editor', 'CameraSetEditor'),
        Command('Character Set Editor', 'CharacterSetEditor'),
        Command('Deformer Set Editor', 'DeformerSetEditor'),
        Command('Layer Relationship Editor', 'LayerRelationshipEditor'),
        Command('Dynamic Relationship Editor', 'DynamicRelationshipEditor'),
        Command('Light-Centric Light Linking Editor', 'LightCentricLightLinkingEditor'),
        Command('Object-Centric Light Linking Editor', 'ObjectCentricLightLinkingEditor'),
        Command('Set Editor', 'SetEditor'),
        Command('Preferences', 'PreferencesWindow'),
        Command('Performance Settings', 'PerformanceSettingsWindow'),
        Command('Hotkey Preferences', 'HotkeyPreferencesWindow'),
        Command('Color Preferences', 'ColorPreferencesWindow'),
        Command('Marking Menu Preferences', 'MarkingMenuPreferencesWindow'),
        Command('Shelf Preferences', 'ShelfPreferencesWindow'),
        Command('Panel Preferences', 'PanelPreferencesWindow'),
        Command('Plugin Manager', 'PluginManager'),
        Command('Playblast Options', 'PlayblastOptions')
    ]
    prompt = 'mel command'

    def execute(self, command):
        from maya import mel
        mel.eval(command)


class Rename(Mode):

    name = 'Rename'
    short_name = 'REN'
    commands = []
    prompt = 'rename tokens'

    def execute(self, command):
        from maya import cmds
        from maya.api import OpenMaya

        renamer = Renamer(command)

        nodes = OpenMaya.MGlobal.getActiveSelectionList()
        for i in range(nodes.length()):
            full_path = nodes.getSelectionStrings(i)[0]
            short_name = full_path.split('|')[-1]
            new_name = renamer.rename(short_name, i)
            cmds.rename(full_path, new_name)


class Connect(Mode):

    name = 'Connect'
    short_name = 'CNCT'
    commands = []
    prompt = 'source destination'

    def execute(self, command):
        from maya import cmds

        attrs = command.split()
        if len(attrs) != 2:
            raise Exception(
                'Input must be a source and destination attribute:\n\n'
                '   translateX translateY\n'
                '   scale scale\n'
            )

        sel = cmds.ls(sl=True, long=True)
        if len(sel) < 2:
            raise Exception(
                'Must have at least 2 objects selected...'
            )

        src_attr = sel[0] + '.' + attrs[0]
        nodes = sel[1:]
        for node in nodes:
            dest_attr = node + '.' + attrs[1]
            try:
                cmds.connectAttr(src_attr, dest_attr, force=True)
            except:
                pass


class Node(Mode):

    name = 'Node'
    short_name = 'NODE'
    prompt = 'node type'

    @property
    def commands(self):
        from maya import cmds
        commands = [Command(c, c) for c in sorted(cmds.allNodeTypes())]
        return commands

    def execute(self, command):
        from maya import cmds

        parts = command.split()
        if len(parts) > 2:
            raise Exception(
                'Input must be a node type and optional name:\n\n'
                '    multiplyDivide\n'
                '    multiplyDivide myMultiplyDivide\n'
            )

        node_type = parts[0]
        node = None
        name = None
        if len(parts) == 2:
            name = parts[1]

        # Handle dg nodes
        shading_classifications = (
            'Utility', 'Shader', 'Texture', 'Rendering', 'PostProcess', 'Light'
        )
        for cls in shading_classifications:
            if cmds.getClassification(node_type, satisfies=cls.lower()):
                node = cmds.shadingNode(node_type, **{'as' + cls: True})

        # Handle dag nodes
        if not node:
            node = cmds.createNode(node_type)

        if name:
            cmds.rename(node, name)


def ls_regex(reg):
    from maya import cmds
    p = re.compile(reg)
    nodes = []
    for node in cmds.ls(long=True):
        name = node.split('|')[-1]
        if p.match(name):
            nodes.append(node)
    return nodes


def ls(pattern):
    from maya import cmds
    return cmds.ls(pattern, long=True)


def select(nodes, add=False):
    from maya import cmds
    return cmds.select(nodes, add=add)


class Select(Mode):

    name = 'Select'
    short_name = 'SEL'
    prompt = 'glob pattern'

    def regex_select(self):
        pattern = self.app.get_user_input('regex pattern')
        if pattern is None:
            return
        return select(ls_regex(pattern))

    def regex_add(self):
        pattern = self.app.get_user_input('regex pattern')
        if pattern is None:
            return
        return select(ls_regex(pattern), add=True)

    def add(self):
        pattern = self.app.get_user_input('glob pattern')
        if pattern is None:
            return
        return select(ls(pattern), add=True)

    @property
    def commands(self):
        return [
            Command('Add', self.add),
            Command('Regex Select', self.regex_select),
            Command('Regex Add', self.regex_add)
        ]

    def execute(self, command):
        return select(command)


class MayaContext(Context):

    name = 'MayaContext'
    modes = [Rename, Select, Node, Connect, Python, Mel]
    style = styles.light
    parent = None

    def get_position(self):
        ok_names = [
            'nodeEditorPanel\dNodeEditorEd',
            'modelPanel\d',
            'hyperShadePrimaryNodeEditor',
            'polyTexturePlacementPanel\d',
            'hyperGraphPanel\dHyperGraphEdImpl',
            'graphEditor\dGraphEdImpl',
        ]

        try:
            widget = maya_widget_under_cursor()
        except TypeError as e:
            print type(e), e
            if not 'shiboken-based type' in str(e):
                raise
        else:
            for name in ok_names:
                match = re.search(widget.path, name)
                if match:
                    pos = top_center(widget.widget)
                    return pos.x() - 480, pos.y()

        panel = active_panel_widget()
        if 'modelPanel' in panel.path:
            widget = active_m3dview_widget()
            pos = top_center(widget.widget)
            return pos.x() - 480, pos.y()

        for name in ok_names:
            widgets = find_child(panel.widget, name)
            if widgets:
                pos = top_center(widgets[0].widget)
                return pos.x() - 480, pos.y()

    def initialize(self, app):
        self.parent = get_maya_window()
