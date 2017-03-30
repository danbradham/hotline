# -*- coding: utf-8 -*-
__all__ = [
    'Executor', 'execute_in_main_thread', 'new_process', 'redirect_stream',
    'wait_for', 'qt_sleep', 'sleep_until'
]

import sys
from contextlib import contextmanager
from Queue import Queue
from functools import partial
from Qt import QtCore, QtGui, QtWidgets
import subprocess
from timeit import default_timer


def keys_to_string(key, modifiers):
    key = QtGui.QKeySequence(key).toString()
    if key == 'Return':
        key = 'Enter'
    if key == 'Backtab':
        key = 'Tab'

    mods = []
    if modifiers & QtCore.Qt.ShiftModifier:
        mods.append('Shift+')
    if modifiers & QtCore.Qt.ControlModifier:
        mods.append('Ctrl+')
    if modifiers & QtCore.Qt.AltModifier:
        mods.append('Alt+')
    if modifiers & QtCore.Qt.MetaModifier:
        mods.append('Meta+')
    mods = ''.join(mods)
    return '+'.join([mods, key])


def new_process(*args, **kwargs):
    '''Wraps subprocess.Popen and polls until the process returns or the
    timeout is reached (2 seconds by default).

    :param args: subprocess.Popen args
    :param kwargs: subprocess.Popen kwargs
    :param timeout: Number of seconds to poll process before returning
    :returns: (stdout, stderr) or None if timeout reached
    '''

    timeout = kwargs.pop('timeout', 2)
    kwargs.setdefault('stdin', subprocess.PIPE)
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.PIPE)
    p = subprocess.Popen(args, **kwargs)
    s = default_timer()
    while default_timer() - s < timeout:
        p.poll()
        if p.returncode is not None:
            break

    if p.returncode is None:
        return

    return p.stdout.read(), p.stderr.read()


@contextmanager
def redirect_stream(stdout=None, stderr=None, stdin=None):
    '''Temporarily redirect output stream'''

    sys.stdout = stdout or sys.__stdout__
    sys.stderr = stderr or sys.__stderr__
    sys.stdin = stdin or sys.__stdin__

    try:
        yield
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.stdin = sys.__stdin__


class Executor(QtCore.QObject):
    '''Executes functions in the main QThread'''

    def __init__(self):
        super(Executor, self).__init__()
        self.queue = Queue()

    def execute(self, fn, *args, **kwargs):
        callback = partial(fn, *args, **kwargs)
        self.queue.put(callback)
        QtCore.QMetaObject.invokeMethod(
            self,
            '_execute',
            QtCore.Qt.QueuedConnection
        )

    @QtCore.Slot()
    def _execute(self):
        callback = self.queue.get()
        callback()


Executor = Executor()


def execute_in_main_thread(fn, *args, **kwargs):
    '''
    Convenience method for Executor.execute...Executes a function in the
    main QThread as soon as possible.
    '''

    Executor.execute(fn, *args, **kwargs)


@contextmanager
def event_loop(conditions=None, timeout=None):

    loop = QtCore.QEventLoop()

    if timeout:
        QtCore.QTimer.singleShot(timeout, loop.quit)

    if conditions:
        ctimer = QtCore.QTimer()
        def check_conditions():
            for condition in conditions:
                if condition():
                    ctimer.stop()
                    loop.quit()
        ctimer.timeout.connect(check_conditions)
        ctimer.start()

    try:
        yield loop
    finally:
        print 'waiting for event loop'
        loop.exec_()


def qt_sleep(secs=0):
    '''Non-blocking sleep for Qt'''

    start = default_timer()
    app = QtWidgets.QApplication.instance()

    while True:
        app.processEvents()
        if default_timer() - start > secs:
            return


def sleep_until(wake_condition, timeout=None, sleep=qt_sleep):
    '''
    Process QApplication events until the wake_condition returns True or
    the timeout is reached...

    :param wake_condition: callable returning True or False
    :param timeout: Number of seconds to wait before returning
    '''

    start = default_timer()

    while True:

        if timeout:
            if default_timer() - start > timeout:
                return

        if wake_condition():
            return

        sleep(0.1)
