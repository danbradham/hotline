import sys
import keyboard
from ..mode import Mode
from ..command import Command
from ..context import Context
from .. import styles


class Python(Mode):

    name = 'Python'
    short_name = 'PY'
    commands = []

    def execute(self, command):
        code = compile(command, '<string>', 'exec')
        exec code in sys.modules['__main__'].__dict__


class BareContext(Context):

    name = 'BareContext'
    modes = [Python]
    style = styles.dark
    parent = None
    position = 'center'
    animation = 'slide'

    def initialize(self, app):
        keyboard.add_hotkey('ctrl + space', app.show)
