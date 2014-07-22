'''
Basic Context
-------------
'''

from ..context import Context, add_mode
import platform
import os
import subprocess


class BasicContext(Context):

    @add_mode("Run")
    def run_handler(self, input):
        plat = platform.system()
        if plat == "Windows":
            os.startfile(os.path.abspath(script))
        else:
            starter = {
                "Linux": "xdg-open",
                "Darwin": "open"
            }[plat]
            subprocess.call([starter, script])
