import os


def rel_path(path, check=True):
    '''Returns paths relative to the modules directory.'''

    fullpath = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    if check and not os.path.exists(fullpath):
        raise OSError("Path {0} does not exist.".format(fullpath))
    return fullpath.replace("\\", "/")

