import traceback
from abc import abstractmethod
from collections import deque

from hotline import styles
from hotline.constant import flags


class Context(object):
    animation = "slide"
    position = "center"

    def __init__(self, app):
        self.app = app
        self.modes = deque([mode(self.app) for mode in self.modes])
        self.parent = None
        self.initialize(app)

    def before_execute(self, mode, command):
        """Called before every command is executed in this context."""
        return NotImplemented

    def execute(self, command, mode=None):
        mode = mode or self.modes[0]

        self.before_execute(mode, command)

        try:
            result = mode(command)
            if result and result not in flags._list:
                print(result)
        except Exception as e:
            result = e
            traceback.print_exc()

        self.after_execute(mode, command, result)

    def after_execute(self, mode, command, result):
        """Called before every command is executed in this context."""
        return NotImplemented

    @property
    @abstractmethod
    def name(self):
        """Name of context"""
        return

    @property
    @abstractmethod
    def modes(self):
        """List of :class:`Mode` instances"""
        return

    @property
    @abstractmethod
    def style(self):
        """CSS Stylesheet"""
        return styles.light

    def get_position(self):
        """Override to provide a custom position for the UI.

        Must return a tuple containing top left corner position"""

        raise NotImplementedError

    @abstractmethod
    def initialize(self, app):
        """This function must set self.parent to a QWidget or QMainWindow
        instance. If hotline is to be run within an existing QApplication then
        you can set self.parent to the QApplications top level QMainWindow
        instance. If hotline is to be the main application this method must
        instantiate a QApplication, create a top level widget and set it to
        self.parent, then start the QApplications event loop. You will also
        want to bind a hotkey to app.show.

        :param app: Hotline application instance"""
        return NotImplemented
