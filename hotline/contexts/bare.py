import sys

from hotline import styles
from hotline.context import Context
from hotline.mode import Mode


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


class BareContext(Context):
    name = "BareContext"
    modes = [Python]
    style = styles.dark
    parent = None
    position = "center"
    animation = "slide"

    def initialize(self, app):
        import keyboard

        keyboard.add_hotkey("ctrl + space", app.show)
