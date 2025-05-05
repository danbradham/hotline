import os
import sys
from glob import glob

this_module = sys.modules[__name__]
this_package = os.path.dirname(__file__)

for file in glob(os.path.join(this_package, "*.css")):
    with open(file, "r") as f:
        data = f.read()
    style_name = os.path.basename(file).split(".")[0]
    setattr(this_module, style_name, data)
