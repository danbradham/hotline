'''
Selectively import and set CTX based on the python executable path.
'''
import sys

PY_EXE = sys.executable.lower()
CTX = None

if "maya" in PY_EXE:
    from .mayacontext import MayaContext
    CTX = MayaContext
elif "nuke" in PY_EXE:
    from .nukecontext import NukeContext
    CTX = NukeContext
else:
    from .basiccontext import BasicContext
    CTX = BasicContext
