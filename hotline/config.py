import os
import shutil
from PySide import QtGui
from collections import defaultdict
from .utils import rel_path


HL_HOME = os.environ.get(
    "HOTLINE_CFG",
    os.path.join(os.path.expanduser("~"), "hotline")
)


def config_path(path, check=True):
    fullpath = os.path.abspath(os.path.join(HL_HOME, path))
    if check and not os.path.exists(fullpath):
        raise OSError("Path {0} does not exist.".format(fullpath))
    return fullpath.replace("\\", "/")


class ConfigBase(dict):

    def __init__(self, cfg_file=None, defaults=None):
        super(ConfigBase, self).__init__(defaults or {})

        if not os.path.exists(HL_HOME):
            shutil.copytree(rel_path("conf"), HL_HOME)

        self.cfg_file = cfg_file
        if self.cfg_file:
            self.from_file(self.cfg_file)

    def from_file(self, f):

        ext = f.split(".")[-1]

        cfg_loaders = {
            "yaml": load_yaml,
            "yml": load_yaml,
            "son": load_json,
            "json": load_json,
            "jsn": load_json,
        }

        try:
            data = cfg_loaders[ext](f)
        except KeyError:
            raise OSError("Config files can be json, yaml, cfg, or ini.")

        self.update(data)
        self.post_load()
        self.cfg_file = f

    def post_load(self):
        pass

    def pre_save(self):
        pass

    def save(self, ext=None):
        if not ext:
            ext = self.cfg_file.split(".")[-1]
            f = self.cfg_file
        else:
            f = "{}.{}".format(os.path.splitext(self.cfg_file)[0], ext)

        cfg_savers = {
            "yaml": save_yaml,
            "yml": save_yaml,
            "son": save_json,
            "json": save_json,
            "jsn": save_json,
        }

        data = self.pre_save()
        cfg_savers[ext](f, data)
        self.cfg_file = f


class Config(ConfigBase):
    '''HotLine's Main Configuration Class. Converts keys between strings and
    QKeySequences on loading and saving.'''

    def post_load(self):
        '''Convert any Key Strings to QKeySequences after loading config.'''

        keys = self.get('KEYS', {})
        if keys:
            key_sequences = defaultdict(dict)
            for mode, key_shortcuts in keys.iteritems():
                for name, seq_str in key_shortcuts.iteritems():
                    seq = QtGui.QKeySequence.fromString(seq_str)
                    key_sequences[mode][name] = seq
            self['KEYS'] = key_sequences

    def pre_save(self):
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


def load_yaml(yml_filepath):
    import yaml

    with open(yml_filepath) as yml_file:
        data = yaml.load(yml_file)

    return data


def save_yaml(yml_filepath, data):
    import yaml

    with open(yml_filepath, 'w') as yml_file:
        yml_file.write(yaml.safe_dump(dict(data), default_flow_style=False))


def load_json(json_filepath):
    import json

    with open(json_filepath) as json_file:
        data = json.loads(json_file.read())

    return data


def save_json(json_filepath, data):
    import json

    with open(json_filepath, "w") as json_file:
        json_file.write(json.dumps(data, indent=4, sort_keys=True))
