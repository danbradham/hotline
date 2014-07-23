'''
settings.py
===========
'''

from .utils import json_load, json_encode, rel_path
try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui


class Settings(object):
    '''An object linked to a json file. Allowing loading and saving.

    :meth post_load: If included pre_load will be run on the json loaded
        from disk prior to setting self._settings.
    :meth pre_save: If included pre_save will be run prior to saving
        self._settings to disc.
    '''

    def __init__(self, settings, combine_user_defaults=True):
        self.name = settings
        self.combine_user_defaults = combine_user_defaults
        self._settings = self.load()

    def __getitem__(self, name):
        return self._settings.__getitem__(name)

    def __setitem__(self, name, value):
        self._settings.__setitem__(name, value)

    def load(self):
        data = load_settings(self.name, self.combine_user_defaults)
        if hasattr(self, "post_load"):
            return self.post_load(data)
        return data

    def refresh(self):
        self._settings = self.load()

    def save(self):
        if hasattr(self, "pre_save"):
            save_settings(self.pre_save(self._settings))
            return
        save_settings(self._settings)


class KeySettings(Settings):
    '''Settings object that encodes key strings to QKeySequences'''

    def __init__(self, combine_user_defaults=True):
        super(KeySettings, self).__init__("key.settings",combine_user_defaults)

    def post_load(self, keys):
        for mode, key_shortcuts in keys.iteritems():
            for name, seq_str in key_shortcuts.iteritems():
                seq = QtGui.QKeySequence.fromString(seq_str)
                keys[mode][name] = seq
        return keys


def save_settings(which, data):
    '''Save settings.

    :param which: which settings file to save (str, filename.ext)
    :param data: data to save (json encodable dict).
    '''
    with open(rel_path("settings/user/" + which, check=False), "w") as f:
        f.write(json_encode(data))


def load_settings(which, combine_user_defaults=True):
    '''Load and concatentate user and default settings.

    :param which: which setting file to load (str, filename.ext)
    :param combine_user_defaults: How to load settings (bool)
        if True -- concatenate user and default settings
        elif False -- user settings if they exist, else default settings
    '''

    defaults = json_load(rel_path("settings/defaults/" + which, check=False))
    user = json_load(rel_path("settings/user/" + which, check=False))

    if combine_user_defaults:
        settings = defaults
        defaults.update(user)
    else:
        settings = user if user else defaults
    return settings
