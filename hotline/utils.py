import os
import glob
import sys
import json
#Try PyQt then PySide imports
try:
    from PyQt4 import QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore


def rel_path(path, check=True):
    '''Returns paths relative to the modules directory.'''

    fullpath = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    if check and not os.path.exists(fullpath):
        return None
    return fullpath


def json_load(path):
    if path:
        with open(path) as f:
            try:
                return json.load(f)
            except ValueError, e:
                print "JSON ERROR: " + path
    return {}


def save_settings(which, data):
    encode = json.dumps(data, indent=4)
    with open(rel_path("settings/user/" + which, check=False), "w") as f:
        f.write(json.dumps(data, indent=4))

def load_settings(which, combine_user_defaults=True):
    '''Load and concatentate user and default settings.

    :param which: which setting file to load (str, filename.ext)
    :param combine_user_defaults: How to load settings (bool)
        if True -- concatenate user and default settings
        elif False -- user settings if they exist, else default settings
    '''

    defaults = json_load(rel_path("settings/defaults/" + which))
    user = json_load(rel_path("settings/user/" + which))

    if combine_user_defaults:
        settings = defaults
        defaults.update(user)
    else:
        settings = user if user else defaults
    return settings


def load_keys():
    keys = load_settings('key.settings')
    for mode, key_shortcuts in keys.iteritems():
        for name, seq_str in key_shortcuts.iteritems():
            seq = QtGui.QKeySequence.fromString(seq_str)
            keys[mode][name] = seq
    return keys


class PatternFactory(object):
    '''Create patterns for Highlighter.'''

    def __init__(self, color_settings="color.settings"):
        self.colors = load_settings(color_settings)

    def format_text(self, r, g, b, a=255, style=''):
        '''Create a QTextCharFormat for Highlighter.'''
        color = QtGui.QColor(r, g, b, a)
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(color)
        if "bold" in style:
            fmt.setFontWeight(QtGui.QFont.Bold)
        if "italic" in style:
            fmt.setFontItalic(True)
        return fmt

    def create(self, name, pattern_name, pattern):
        '''Generates a pattern for use with a QSyntaxHighlighter
        Returns a tuple containing a regex pattern and text formatter
        '''

        try:
            color = self.colors[name][pattern_name]
        except KeyError:
            color = self.colors[name][pattern_name.split('.')[0]]
        except KeyError:
            color = self.colors['defaults']['input_color']

        fmt = self.format_text(*color)

        if 'multiline' in pattern_name:
            start = QtCore.QRegExp(pattern['start'])
            end = QtCore.QRegExp(pattern['end'])
            return start, end, fmt
        else:
            match = QtCore.QRegExp(pattern['match'])
            captures = pattern['captures']
            return match, captures, fmt
