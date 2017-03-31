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
    prompt = 'python command'

    def execute(self, command):
        main = sys.modules['__main__'].__dict__
        try:
            code = compile(command, '<string>', 'eval')
            return eval(code, main, main)
        except SyntaxError:
            code = compile(command, '<string>', 'exec')
            exec code in main



class BareContext(Context):

    name = 'BareContext'
    modes = [Python]
    style = styles.dark
    parent = None
    position = 'center'
    animation = 'slide'

    def initialize(self, app):
        keyboard.add_hotkey('ctrl + space', app.show)
