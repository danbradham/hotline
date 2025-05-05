import re
import sys
from collections import namedtuple
from fnmatch import fnmatch

from hotline import styles
from hotline.command import Command
from hotline.context import Context
from hotline.mode import Mode
from hotline.renamer import Renamer
from hotline.vendor.qtpy import QtCore, QtGui, QtWidgets

# Py3 Compat
if sys.version_info > (0, 3):
    long = int


MayaWidget = namedtuple("MayaWidget", "path widget")


def get_maya_window():
    """Get Maya MainWindow as a QWidget."""

    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.objectName() == "MayaWindow":
            return widget
    raise RuntimeError("Could not locate MayaWindow...")


def maya_widget_under_cursor():
    """Get the MayaWidget under your mouse cursor"""

    cursor = QtGui.QCursor()
    return maya_widget_at(cursor.pos())


def maya_widget_at(pos):
    """Get a MayaWidget at QtCore.QPoint"""

    widget = QtWidgets.QApplication.widgetAt(pos)
    return maya_widget(widget)


def maya_widget(widget):
    """QWidget to MayaWidget"""

    from maya.OpenMayaUI import MQtUtil

    from hotline.vendor.qtpy.shiboken import getCppPointer

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

    from hotline.vendor.qtpy.shiboken import wrapInstance

    panel = cmds.getPanel(withFocus=True)
    widget = wrapInstance(long(MQtUtil.findControl(panel)), QtWidgets.QWidget)
    return MayaWidget(panel, widget)


def active_m3dview_widget():
    """Get active m3dview"""

    from maya.OpenMayaUI import M3dView

    from hotline.vendor.qtpy.shiboken import wrapInstance

    active3dview = M3dView.active3dView()
    pointer = long(active3dview.widget())
    widget = wrapInstance(pointer, QtWidgets.QWidget)
    return maya_widget(widget)


def top_center(widget):
    """Returns the top center screen coordinates of a widget"""

    rect = widget.rect()
    top = widget.mapToGlobal(rect.topLeft()).y()
    center = widget.mapToGlobal(rect.center()).x()
    return QtCore.QPoint(center, top)


class Python(Mode):
    name = "Python"
    label = "PY"
    commands = []
    prompt = "python command"

    def execute(self, command):
        main = sys.modules["__main__"].__dict__
        try:
            code = compile(command, "<string>", "eval")
            return eval(code, main, main)
        except SyntaxError:
            code = compile(command, "<string>", "exec")
            exec(code, main, main)


class Mel(Mode):
    name = "Mel"
    label = "MEL"
    commands = [
        Command("Attribute Editor", "AttributeEditor"),
        Command("ConnectionEditor", "ConnectionEditor"),
        Command("Node Editor", "NodeEditorWindow"),
        Command("Render View", "RenderViewWindow"),
        Command("Content Browser", "ContentBrowserWindow"),
        Command("Tool Settings", "ToolSettingsWindow"),
        Command("Hypergraph Hierarchy", "HypergraphHierarchyWindow"),
        Command("Hypergraph", "HypergraphDGWindow"),
        Command("Asset Editor", "AssetEditor"),
        Command("Attribute Spreadsheet", "SpreadSheetEditor"),
        Command("Component Editor", "ComponentEditor"),
        Command("Channel Control", "ChannelControlEditor"),
        Command("Display Layers", "DisplayLayerEditorWindow"),
        Command("File Path Editor", "FilePathEditor"),
        Command("Namespace Editor", "NamespaceEditor"),
        Command("Script Editor", "ScriptEditor"),
        Command("Command Shell", "CommandShell"),
        Command("Profiler", "ProfilerTool"),
        Command("Evaluation Toolkit", "EvaluationToolkit"),
        Command("Modeling Toolkit", "showModelingToolkit"),
        Command("Paint Effects Window", "PaintEffectsWindow"),
        Command("UV Editor", "TextureViewWindow"),
        Command(
            "Crease Sets",
            'python "from maya.app.general import creaseSetEditor; creaseSetEditor.showCreaseSetEditor();"',
        ),
        Command("Graph Editor", "GraphEditor"),
        Command("Time Editor", "TimeEditorWindow"),
        Command("Trax Editor", "CharacterAnimationEditor"),
        Command("Camera Sequencer", "SequenceEditor"),
        Command("Quick Rig", "QuickRigEditor"),
        Command("HIK Character Tools", "HIKCharacterControlsTool"),
        Command("Blend Shape Editor", "ShapeEditor"),
        Command("Pose Editor", "PoseEditor"),
        Command("Expression Editor", "ExpressionEditor"),
        Command("Render Settings/Globals", "RenderGlobalsWindow"),
        Command("Hypershade", "HypershadeWindow"),
        Command("Render Layer Editor", "RenderLayerEditorWindow"),
        Command(
            "Light Editor",
            'callPython "maya.app.renderSetup.views.lightEditor.editor" "openEditorUI" {};',
        ),
        Command("Render Flags", "RenderFlagsWindow"),
        Command("Shading Group Attributes", "ShadingGroupAttributeEditor"),
        Command("Animation Layer Relationships", "AnimationLayerRelationshipEditor"),
        Command("Camera Set Editor", "CameraSetEditor"),
        Command("Character Set Editor", "CharacterSetEditor"),
        Command("Deformer Set Editor", "DeformerSetEditor"),
        Command("Layer Relationship Editor", "LayerRelationshipEditor"),
        Command("Dynamic Relationship Editor", "DynamicRelationshipEditor"),
        Command("Light-Centric Light Linking Editor", "LightCentricLightLinkingEditor"),
        Command(
            "Object-Centric Light Linking Editor", "ObjectCentricLightLinkingEditor"
        ),
        Command("Set Editor", "SetEditor"),
        Command("Preferences", "PreferencesWindow"),
        Command("Performance Settings", "PerformanceSettingsWindow"),
        Command("Hotkey Preferences", "HotkeyPreferencesWindow"),
        Command("Color Preferences", "ColorPreferencesWindow"),
        Command("Marking Menu Preferences", "MarkingMenuPreferencesWindow"),
        Command("Shelf Preferences", "ShelfPreferencesWindow"),
        Command("Panel Preferences", "PanelPreferencesWindow"),
        Command("Plugin Manager", "PluginManager"),
        Command("Playblast Options", "PlayblastOptions"),
    ]
    prompt = "mel command"

    def execute(self, command):
        from maya import mel

        mel.eval(command)


class Rename(Mode):
    name = "Rename"
    label = "REN"
    commands = []
    prompt = "rename tokens"

    def execute(self, command):
        from maya import cmds
        from maya.api import OpenMaya

        renamer = Renamer(command)

        nodes = OpenMaya.MGlobal.getActiveSelectionList()
        for i in range(nodes.length()):
            full_path = nodes.getSelectionStrings(i)[0]
            short_name = full_path.split("|")[-1]
            new_name = renamer.rename(short_name, i)
            cmds.rename(full_path, new_name)


class Connect(Mode):
    name = "Connect"
    label = "CNCT"
    prompt = "source destination"

    def get_next_attr_index(self, attr):
        from maya import cmds

        for i in range(10000):
            attr_ = "{}[{}]".format(attr, i)
            if not cmds.connectionInfo(attr_, sfd=True):
                return i
        return 0

    def connect_pairs(self):
        command = self.app.get_user_input(self.prompt)
        if not command:
            return

        self.validate_command(command)

        from maya import cmds

        attrs = command.split()
        sel = cmds.ls(sl=True, long=True)
        assert len(sel) % 2 == 0, "Must have an even number of items selected."

        for src, dest in zip(sel[::2], sel[1::2]):
            src_attr = src + "." + attrs[0]
            dest_attr = dest + "." + attrs[1]
            try:
                cmds.connectAttr(src_attr, dest_attr, force=True)
            except Exception:
                pass

    def connect_one_to_many(self):
        command = self.app.get_user_input(self.prompt)
        if not command:
            return

        self.validate_command(command)

        from maya import cmds

        attrs = command.split()
        sel = cmds.ls(sl=True, long=True)

        src_attr = sel[0] + "." + attrs[0]
        for dest in sel[1:]:
            dest_attr = dest + "." + attrs[1]
            try:
                cmds.connectAttr(src_attr, dest_attr, force=True)
            except Exception:
                pass

    def connect_many_to_one(self):
        command = self.app.get_user_input(self.prompt)
        if not command:
            return

        self.validate_command(command)

        from maya import cmds

        attrs = command.split()
        sel = cmds.ls(sl=True, long=True)

        dest_attr = sel[-1] + "." + attrs[1]
        inputs = cmds.listConnections(dest_attr) or []
        idx = self.get_next_attr_index(dest_attr)
        for i, src in enumerate(sel[:-1]):
            src_attr = src + "." + attrs[0]
            if src in inputs:
                continue
            dest_attr_idx = "{}[{}]".format(dest_attr, idx + i)
            cmds.connectAttr(src_attr, dest_attr_idx)

    @property
    def commands(self):
        return [
            Command("Pairs", self.connect_pairs),
            Command("One To Many", self.connect_one_to_many),
            Command("Many To One", self.connect_many_to_one),
        ]

    def validate_command(self, command):
        from maya import cmds

        if len(command.split()) != 2:
            raise Exception(
                "Input must be a source and destination attribute:\n\n"
                "   translateX translateY\n"
                "   scale scale\n"
            )

        if len(cmds.ls(sl=True, long=True)) < 2:
            raise Exception("Must have at least 2 objects selected...")

    def execute(self, command):
        self.validate_command(command)

        from maya import cmds

        attrs = command.split()
        sel = cmds.ls(sl=True, long=True)

        src_attr = sel[0] + "." + attrs[0]
        for dest in sel[1:]:
            dest_attr = dest + "." + attrs[1]
            try:
                cmds.connectAttr(src_attr, dest_attr, force=True)
            except Exception:
                pass


class Node(Mode):
    name = "Node"
    label = "NODE"
    prompt = "node type"

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
                "Input must be a node type and optional name:\n\n"
                "    multiplyDivide\n"
                "    multiplyDivide myMultiplyDivide\n"
            )

        node_type = parts[0]
        node = None
        name = None
        if len(parts) == 2:
            name = parts[1]

        # Handle dg nodes
        shading_classifications = (
            "Utility",
            "Shader",
            "Texture",
            "Rendering",
            "PostProcess",
            "Light",
        )
        for cls in shading_classifications:
            if cmds.getClassification(node_type, satisfies=cls.lower()):
                node = cmds.shadingNode(node_type, **{"as" + cls: True})

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
        name = node.split("|")[-1]
        if p.match(name):
            nodes.append(node)
    return nodes


def ls_regex_filter(reg):
    from maya import cmds

    p = re.compile(reg)
    nodes = []
    for node in cmds.ls(sl=True, long=True):
        name = node.split("|")[-1]
        if p.match(name):
            nodes.append(node)
    return nodes


def ls(pattern):
    from maya import cmds

    return cmds.ls(pattern, long=True)


def ls_filter(pattern):
    from maya import cmds

    return cmds.ls(pattern, sl=True, long=True)


def select(nodes, add=False):
    from maya import cmds

    return cmds.select(nodes, add=add)


class Select(Mode):
    name = "Select"
    label = "SEL"
    prompt = "glob pattern"

    def add(self):
        pattern = self.app.get_user_input("glob pattern")
        if pattern is None:
            return
        return select(ls(pattern), add=True)

    def filter(self):
        pattern = self.app.get_user_input("glob pattern")
        if pattern is None:
            return
        return select(ls_filter(pattern))

    def regex_select(self):
        pattern = self.app.get_user_input("regex pattern")
        if pattern is None:
            return
        return select(ls_regex(pattern))

    def regex_add(self):
        pattern = self.app.get_user_input("regex pattern")
        if pattern is None:
            return
        return select(ls_regex(pattern), add=True)

    def regex_filter(self):
        pattern = self.app.get_user_input("regex pattern")
        if pattern is None:
            return
        return select(ls_regex_filter(pattern))

    def type_select(self):
        from maya import cmds

        pattern = self.app.get_user_input("node type")
        if pattern is None:
            return
        return select(
            [n for n in cmds.ls() if fnmatch(cmds.nodeType(n), pattern)],
        )

    def type_add(self):
        from maya import cmds

        pattern = self.app.get_user_input("node type")
        if pattern is None:
            return
        return select(
            [n for n in cmds.ls() if fnmatch(cmds.nodeType(n), pattern)],
            add=True,
        )

    def type_filter(self):
        from maya import cmds

        pattern = self.app.get_user_input("node type")
        if pattern is None:
            return
        return select(
            [n for n in cmds.ls(sl=True) if fnmatch(cmds.nodeType(n), pattern)],
        )

    @property
    def commands(self):
        return [
            Command("Add", self.add),
            Command("Filter", self.filter),
            Command("Regex Select", self.regex_select),
            Command("Regex Add", self.regex_add),
            Command("Regex Filter", self.regex_filter),
            Command("Type Select", self.type_select),
            Command("Type Add", self.type_add),
            Command("Type Filter", self.type_filter),
        ]

    def execute(self, command):
        return select(command)


class MayaContext(Context):
    name = "MayaContext"
    modes = [Rename, Select, Node, Connect, Python, Mel]
    style = styles.maya
    parent = None

    def before_execute(self, mode, command):
        from maya import cmds

        cmds.undoInfo(openChunk=True)

    def after_execute(self, mode, command, result):
        from maya import cmds

        cmds.undoInfo(closeChunk=True)

    def get_position(self):
        ok_names = [
            "nodeEditorPanel\dNodeEditorEd",
            "modelPanel\d",
            "hyperShadePrimaryNodeEditor",
            "polyTexturePlacementPanel\d",
            "hyperGraphPanel\dHyperGraphEdImpl",
            "graphEditor\dGraphEdImpl",
        ]

        try:
            widget = maya_widget_under_cursor()
        except TypeError as e:
            print(type(e), e)
            if "shiboken-based type" not in str(e):
                raise
        else:
            for name in ok_names:
                match = re.search(widget.path, name)
                if match:
                    pos = top_center(widget.widget)
                    return pos.x() - self.app.ui._width * 0.5, pos.y()

        panel = active_panel_widget()
        if "modelPanel" in panel.path:
            widget = active_m3dview_widget()
            pos = top_center(widget.widget)
            return pos.x() - self.app.ui._width * 0.5, pos.y()

        for name in ok_names:
            widgets = find_child(panel.widget, name)
            if widgets:
                pos = top_center(widgets[0].widget)
                return pos.x() - self.app.ui._width * 0.5, pos.y()

    def initialize(self, app):
        self.parent = get_maya_window()
