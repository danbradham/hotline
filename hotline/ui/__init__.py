'''
Selectively import and set UI based on the python executable path.
'''
import sys

PY_EXE = sys.executable.lower()

if "maya" in PY_EXE:
    from .mayaui import MayaUI
    UI = MayaUI
else:
    from .ui import UI
