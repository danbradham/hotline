# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os
import shlex
import sys
from hotline.mode import Mode
from hotline.command import Command
from hotline.context import Context
from hotline import styles
from hotline.utils import new_process


def elevated():
    new_process(
        'powershell.exe',
        '-Command',
        "Start-Process powershell.exe -Verb runAs"
    )


class PowerShell(Mode):

    name = 'PowerShell'
    label = 'PS'
    prompt = 'Powershell command'

    @property
    def commands(self):
        return [
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

        print(new_process(*cmd))


class Cmd(Mode):

    name = 'Cmd'
    label = 'CMD'
    commands = []
    prompt = 'batch command'

    def execute(self, command):
        cmd = ['cmd', '/C', command]
        print(new_process(cmd, shell=True))


class Python(Mode):

    name = 'Python'
    label = 'PY'
    commands = []
    prompt = 'python command'

    def execute(self, command):
        main = sys.modules['__main__'].__dict__
        try:
            code = compile(command, '<string>', 'eval')
            return eval(code, main, main)
        except SyntaxError:
            code = compile(command, '<string>', 'exec')
            eval(code, main, main)


class Run(Mode):

    name = 'Run'
    label = 'RUN'

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
    parent = None

    def initialize(self, app):
        import keyboard
        keyboard.add_hotkey('ctrl + space', app.show)
