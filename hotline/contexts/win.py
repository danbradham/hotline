# -*- coding: utf-8 -*-
import os
import shlex
from functools import partial
import sys
import keyboard
from ..mode import Mode
from ..command import Command
from ..context import Context
from .. import styles
from ..utils import new_process


def elevated():
    return new_process(
        'powershell.exe',
        '-Command',
        "Start-Process powershell.exe -Verb runAs"
    )


class PowerShell(Mode):

    name = 'PowerShell'
    short_name = 'PS'

    @property
    def commands(self):
        return [
            Command('Use Python 27', 'sudo usepython 27'),
            Command('Use Python 35', 'sudo usepython 35'),
            Command('Use Python 36', 'sudo usepython 36'),
            Command('Launch Elevated PowerShell', elevated),
        ]

    def execute(self, command):
        cmd = ['powershell']
        if '-file' in command.lower() or '-command' in command.lower():
            cmd.extend(shlex.split(command))
        elif command.endswith('.ps1'):
            cmd.append(cmd)
        else:
            cmd.append('-Command')
            cmd.append(command)

        print new_process(*cmd)


class Cmd(Mode):

    name = 'Cmd'
    short_name = 'CMD'
    commands = []

    def execute(self, command):
        cmd = ['cmd', '/C', command]
        print new_process(cmd, shell=True)


class Python(Mode):

    name = 'Python'
    short_name = 'PY'
    commands = []

    def execute(self, command):
        code = compile(command, '<string>', 'exec')
        exec code in sys.modules['__main__'].__dict__


class Run(Mode):

    name = 'Run'
    short_name = 'RUN'

    @property
    def commands(self):
        commands = {}
        user_start_menu = os.path.join(
            os.path.expanduser('~'),
            'AppData',
            'Roaming',
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs'
        )
        start_menu = os.path.join(
            'C:\\',
            'ProgramData',
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs')

        for path in (user_start_menu, start_menu):
            for root, subdirs, files in os.walk(path):
                for file in files:
                    if not file.endswith('.lnk'):
                        continue
                    name = os.path.basename(file).replace('.lnk', '')
                    if name in commands or 'uninstall' in name.lower():
                        continue
                    pth = os.path.join(root, file)
                    commands[name] = Command(name, pth)

        paths = os.environ['PATH'].split(os.pathsep)
        for path in paths:
            if not os.path.exists(path):
                continue
            for file in os.listdir(path):
                name, ext = os.path.splitext(file)
                if ext not in ['.exe', '.bat', '.sh', '.py', '.lnk', '.ps1']:
                    continue
                if name in commands or 'uninstall' in name.lower():
                    continue
                pth = os.path.join(path, file)
                commands[name] = Command(name, pth)

        return [v for k, v in sorted(commands.items())]

    def execute(self, command):
        os.startfile(command)


class WindowsContext(Context):

    name = 'WindowsContext'
    modes = [Run, Python, PowerShell, Cmd]
    style = styles.light
    parent = None

    def initialize(self, app):
        keyboard.add_hotkey('ctrl + space', app.show)
