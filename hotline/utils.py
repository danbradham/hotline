import os
import json


def rel_path(path, check=True):
    '''Returns paths relative to the modules directory.'''

    fullpath = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    if check and not os.path.exists(fullpath):
        raise OSError("Path {0} does not exist.".format(fullpath))
    return fullpath.replace("\\", "/")


def json_load(path):
    if path:
        with open(path) as f:
            try:
                return json.load(f)
            except ValueError:
                print "JSON ERROR: " + path
    return {}


def json_encode(data):
    return json.dumps(data, indent=4)
