# -*- coding: utf-8 -*-
from abc import abstractmethod, abstractproperty
from .command import Command
import threading


class Mode(object):

    prompt = None

    def __init__(self, app):
        self.app = app

    def __str__(self):
        return self.short_name

    def __hash__(self):
        return hash(self.name)

    def __call__(self, command):
        cmd = self.get_command(command)
        if not cmd:
            return self.execute(command)

        if cmd.generator:
            cmd_steps = cmd.command()
            selection = None
            result = None
            try:
                while result is None:

                    if selection:
                        step = cmd_steps.send(selection)
                        selection = None
                    else:
                        step = cmd_steps.next()

                    if isinstance(step, Command):
                        result = step
                    elif isinstance(step, (list, tuple)) or step is None:
                        selection = self.app.get_user_input(step)
                    else:
                        raise Exception(
                            'Generator yielded invalid type...'
                            'must be Sequence, None or Command not {}'.format(type(step))
                        )
            finally:
                cmd_steps.close()
                cmd = result

        if cmd.callable:
            return cmd()

        return self.execute(cmd.command)

    @abstractproperty
    def name(self):
        '''return name of mode'''
        return

    @abstractproperty
    def short_name(self):
        '''return a short name up to 4 characters'''
        return

    @property
    def icon(self):
        '''[optional] return path to an icon'''
        return

    def get_command(self, name):
        for command in self.commands:
            if command.name == name:
                return command
        return

    @abstractproperty
    def commands(self):
        '''return a list of Command objects'''
        return

    @abstractmethod
    def execute(self, command):
        '''Execute the user input command from hotline'''
        return
