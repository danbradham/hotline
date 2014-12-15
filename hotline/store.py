from .config import ConfigBase
from .shout import shout
from .messages import (Store_Delete, Store_Evaluate, Store_Load,
                       Store_Refresh, Store_Save, Store_Run, WriteOutput)
import sys
import traceback

class Store(ConfigBase):
    '''No pre save or post load. Just reads and writes config files.'''

    def __init__(self, app, *args, **kwargs):
        self.app = app
        super(Store, self).__init__(*args, **kwargs)

    def evaluate(self, modes):
        for name, data in self.iteritems():
            shout(Store_Evaluate, name)
            if data["autoload"]:
                self.run(data)

    def pre_save(self):
        shout(Store_Save, self.cfg_file)
        return self

    def post_load(self):
        shout(Store_Load, self.cfg_file)

    def delete(self, name):
        self.pop(name, None)
        shout(Store_Delete, name)
        self.save()

    def refresh(self):
        shout(Store_Refresh)
        self.from_file(self.cfg_file)

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
