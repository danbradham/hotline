from .config import ConfigBase
from .shout import shout
from .messages import (Store_Delete, Store_Evaluate, Store_Load,
                       Store_Refresh, Store_Save, Store_Run, WriteOutput)
import sys
import traceback


class Store(ConfigBase):
    '''No encode or decode. Just reads and writes config files.'''

    def __init__(self, app, *args, **kwargs):
        self.app = app
        super(Store, self).__init__(*args, **kwargs)

    def evaluate(self, modes):
        for name, data in self.iteritems():
            shout(Store_Evaluate, name)
            if data["autoload"]:
                self.run(data)

    def encode(self):
        shout(Store_Save, self.path)
        return self

    def decode(self):
        shout(Store_Load, self.path)

    def delete(self, name):
        self.pop(name, None)
        shout(Store_Delete, name)
        self.save()

    def refresh(self):
        shout(Store_Refresh)
        self.from_file(self.path)

    def run(self, data):

        mode = self.app.ctx.get_mode(data['mode'])
        cmd = data['command']
        output_str = "{}:\n{}\n\n".format(mode.name, cmd)
        shout(WriteOutput, output_str)

        try:
            mode.handler(cmd)
        except:
            exc = "".join(traceback.format_exception(*sys.exc_info()))
            shout(WriteOutput, exc)
