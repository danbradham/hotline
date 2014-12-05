from PySide import QtGui
from .ui import UI


def get_maya_window():
    '''Grabs Maya's MainWindow QWidget instance. I feel enough software
    has sufficiently switched over to PySide to simplify this function and
    stop supporting both PyQt and PySide. Little lazy with the maya import,
    allowing this module to be imported to a standard python interpreter.'''

    import shiboken
    import maya.OpenMayaUI as mui

    ptr = long(mui.MQtUtil.mainWindow())
    return shiboken.wrapInstance(ptr, QtGui.QWidget)


class MayaUI(UI):
    '''Context overriding :func:`create` parenting the UI to Autodesk Maya.'''

    @classmethod
    def create(cls, app):
        maya_window = get_maya_window()
        return cls(app, parent=maya_window)
