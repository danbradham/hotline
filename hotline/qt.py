"""
Because the world has not yet decided which Python binding of Qt to use...

e.g.
from .qt import QtCore, QtGui, wrapinstance
"""


try:
    try:
        import shiboken
    except ImportError:
        from Shiboken import shiboken
    wrapinstance = shiboken.wrapInstance
    from PySide import QtGui, QtCore
except ImportError:
    import sip
    wrapinstance = sip.wrapinstance
    for datatype in ['QString', 'QVariant', 'QUrl', 'QDate',
                     'QDateTime', 'QTextStream', 'QTime']:
        sip.setapi(datatype, 2)
    from PyQt4 import QtGui, QtCore
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
except ImportError:
    raise ImportError("Can not find PySide or PyQt.")
