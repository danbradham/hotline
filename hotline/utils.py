import sys
import os


HL_HOME = os.environ.get(
    "HOTLINE_CFG",
    os.path.join(os.path.expanduser("~"), "hotline")
)


def rel_path(path, check=True):
    '''Returns paths relative to the modules directory.'''

    fullpath = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    if check and not os.path.exists(fullpath):
        raise OSError("Path {0} does not exist.".format(fullpath))
    return fullpath.replace("\\", "/")


def config_path(path, check=True):
    fullpath = os.path.abspath(os.path.join(HL_HOME, path))
    if check and not os.path.exists(fullpath):
        raise OSError("Path {0} does not exist.".format(fullpath))
    return fullpath.replace("\\", "/")


def import_module(name):
    '''Like importlib.import_module, but without support for relative imports
    from packages.'''
    __import__(name)
    return sys.modules[name]
