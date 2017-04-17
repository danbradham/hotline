# -*- coding: utf-8 -*-
from abc import abstractmethod, abstractproperty
from collections import deque


class Context(object):

    animation = 'slide'
    position = 'center'

    def __init__(self, app):
        self.app = app
        self.modes = deque([mode(self.app) for mode in self.modes])
        self.parent = None
        self.initialize(app)

    @abstractproperty
    def name(self):
        '''Name of context'''
        return

    @abstractproperty
    def modes(self):
        '''List of :class:`Mode` instances'''
        return

    @abstractproperty
    def style(self):
        '''CSS Stylesheet'''
        return

    def get_position(self):
        '''Override to provide a custom position for the UI.

        Must return a tuple containing top left corner position'''

        raise NotImplementedError

    @abstractmethod
    def initialize(self, app):
        '''This function must set self.parent to a QWidget or QMainWindow
        instance. If hotline is to be run within an existing QApplication then
        you can set self.parent to the QApplications top level QMainWindow
        instance. If hotline is to be the main application this method must
        instantiate a QApplication, create a top level widget and set it to
        self.parent, then start the QApplications event loop. You will also want
        to bind a hotkey to app.show.

        :param app: Hotline application instance'''
        return
