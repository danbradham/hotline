from PySide import QtCore, QtGui
import shiboken
import maya.OpenMayaUI as OpenMayaUI
from .ui import UI


def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = long(OpenMayaUI.MQtUtil.mainWindow())
    if "shiboken" in globals():
        return shiboken.wrapInstance(ptr, QtGui.QWidget)
    return shiboken.wrapInstance(ptr, QtCore.QObject)


class MayaUI(UI):

    @classmethod
    def show(cls):
        '''Show HotLine ui.'''

        if not cls.instance:
            #Instantiate HotLine as child of Maya Window
            cls.instance = cls(parent=getMayaWindow())
        cls.instance.enter()
