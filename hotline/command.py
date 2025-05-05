from inspect import isgeneratorfunction


class Command(object):
    def __init__(self, name, command, icon=None):
        self.name = name
        self.command = command
        self.icon = icon

    def __call__(self):
        return self.command()

    def __hash__(self):
        return hash(self.name)

    @property
    def callable(self):
        return callable(self.command)

    @property
    def generator(self):
        return isgeneratorfunction(self.command)
