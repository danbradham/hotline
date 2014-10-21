'''
qt.py
=====

Imports either PySide or PyQt with preference towards PySide.
usage:
    from qt import QtGui, QtCore, wrapinstance
'''

try:
    try:
        import shiboken
        wrapinstance = shiboken.wrapInstance
    except ImportError:
        wrapinstance = None
        pass
    from PySide import QtGui, QtCore
except ImportError:
    try:
        import sip
        for datatype in ['QString', 'QVariant', 'QUrl', 'QDate',
                         'QDateTime', 'QTextStream', 'QTime']:
            sip.setapi(datatype, 2)
        wrapinstance = sip.wrapinstance
    except ImportError:
        wrapinstance = None
        pass
    from PyQt4 import QtGui, QtCore
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
except ImportError:
    raise ImportError("Can not find PySide of PyQt.")
