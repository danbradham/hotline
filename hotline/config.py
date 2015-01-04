import os
from collections import defaultdict


def load_yaml(yml_filepath):
    '''Load yaml file

    :param yml_filepath: path to yaml file

    :return: dict
    '''

    import yaml

    with open(yml_filepath) as yml_file:
        data = yaml.load(yml_file)

    return data


def save_yaml(yml_filepath, data):
    '''Save yaml file

    :param yml_filepath: path to yaml file
    :param data: python dict to save
    '''

    import yaml

    with open(yml_filepath, 'w') as yml_file:
        yml_file.write(yaml.safe_dump(dict(data), default_flow_style=False))

    return True


def load_json(json_filepath):
    '''Load json file

    :param json_filepath: path to json file

    :return: dict
    '''

    import json

    with open(json_filepath) as json_file:
        data = json.loads(json_file.read())

    return data


def save_json(json_filepath, data):
    '''Save json file

    :param json_filepath: path to json file
    :param data: python dict to save
    '''

    import json

    with open(json_filepath, "w") as json_file:
        json_file.write(json.dumps(data, indent=4, sort_keys=True))

    return True


def load_py(py_filepath):
    '''Load py file

    :param py_filepath: path to json file

    :return: dict
    '''

    import imp

    cmod = imp.new_module('c')
    cmod.__file__ = py_filepath

    with open(py_filepath, 'r') as f:
        exec(compile(f.read(), py_filepath, 'exec'), cmod.__dict__)

    data = {}
    for k, v in dir(cmod):
        if k.isupper():
            data[k] = v

    return data


def save_py(py_filepath):
    '''Raises Exception'''
    raise IOError('Can not write configuration data directly to a python file')


LOADERS = {
    'yaml': load_yaml,
    'yml': load_yaml,
    'son': load_json,
    'json': load_json,
    'jsn': load_json,
    'py': load_py,
}
SAVERS = {
    'yaml': save_yaml,
    'yml': save_yaml,
    'son': save_json,
    'json': save_json,
    'jsn': save_json,
    'py': save_py,
}
SUPPORTED_TYPES = ['yaml', 'yml', 'son', 'json', 'py']


class ConfigBase(dict):

    def __init__(self, *args, **defaults):
        super(ConfigBase, self).__init__(*args, **defaults)
        self.env_var = None
        self.root = None
        self.path = None

    def from_env(self, env_var):
        self.env_var = env_var
        env_path = os.environ.get(env_var)

        if os.path.exists(env_path):
            if os.path.isfile(env_path):
                self.root = os.path.dirname(env_path)
                path = env_path
                self.from_file(path)
            else:
                self.root = env_path
                for typ in SUPPORTED_TYPES:
                    path = self.relative_path('config.{}'.format(typ))
                    if os.path.exists(path):
                        self.from_file(path)
        else:
            raise EnvironmentError(
                '{} points to invalid path: {}'.format(env_var, env_path))

    def from_file(self, path):
        ext = path.split(".")[-1]

        try:
            data = LOADERS[ext](path)
        except KeyError:
            raise OSError("Config files must be json, yaml, or py modules.")

        self.update(data)

        if hasattr(self, 'decode'):
            self.decode()

        self.path = path

    def relative_path(self, *path):
        '''Returns a path relative to config file or config root'''

        fullpath = os.path.abspath(os.path.join(self.root, *path))
        return fullpath.replace("\\", "/")

    def decode(self):
        '''Decode data after load.'''

        pass

    def encode(self):
        '''Encode and data prior to save.

        :return: dict'''

        return self

    def save(self, ext=None):
        '''Write config data to file.

        :param ext: Extension of file type'''

        if not ext:
            ext = self.path.split(".")[-1]
            path = self.path
        else:
            path = "{}.{}".format(os.path.splitext(self.path)[0], ext)

        if hasattr(self, 'encode'):
            data = self.encode()
        else:
            data = self

        SAVERS[ext](path, data)


class Config(ConfigBase):
    '''HotLine's Main Configuration Class. Converts keys between strings and
    QKeySequences on loading and saving.'''

    def decode(self):
        '''Convert any Key Strings to QKeySequences after loading config.'''

        from PySide import QtGui

        keys = self.get('KEYS', {})
        if keys:
            key_sequences = defaultdict(dict)
            for mode, key_shortcuts in keys.iteritems():
                for name, seq_str in key_shortcuts.iteritems():
                    seq = QtGui.QKeySequence.fromString(seq_str)
                    key_sequences[mode][name] = seq
            self['KEYS'] = key_sequences

    def encode(self):
        '''Convert any QtGui.QKeySequences to Strings before saving config.'''

        data = dict(self)
        keys = self.get('KEYS', {})
        if keys:
            key_strings = defaultdict(dict)
            for mode, key_shortcuts in keys.iteritems():
                for name, seq in key_shortcuts.iteritems():
                    key_strings[mode][name] = seq.toString()
            data['KEYS'] = key_strings
        return data
