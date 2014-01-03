import os
import json
#Try PyQt then PySide imports
try:
    from PyQt4 import QtGui
except ImportError:
    from PySide import QtGui


def rel_path(path):
    '''Returns paths relative to the modules directory.'''
    fullpath = os.path.join(os.path.dirname(__file__), os.path.abspath(path))
    if os.path.exists(fullpath):
        return fullpath
    return None


def load_settings(which, combine_user_defaults=True):
    '''Load and concatentate user and default settings.

    :param which: which setting file to load (str, filename.ext)
    :param combine_user_defaults: How to load settings (bool)
        if True -- concatenate user and default settings
        elif False -- user settings if they exist, else default settings
    '''

    defaults_path = rel_path("settings/defaults/" + which)
    user_path = rel_path("settings/user/" + which)

    try:
        with open(defaults_path) as f:
            defaults = json.load(f)
    except OSError:
        defaults = {}
    try:
        with open(user_path) as f:
            user = json.load(f)
    except OSError:
        user = {}

    if combine_user_defaults:
        settings = defaults.update(user)
    else:
        settings = user if user else defaults
    return settings


def load_keys():
    keys = load_settings('key.settings')
    for mode, key_shortcuts in keys.iteritems():
        for name, seq_str in keys['standard'].iteritems():
            seq = QtGui.QKeySequence.fromString(seq_str)[0]
            keys[mode][name] = seq
    return keys


def format_text(r, g, b, a=255, style=''):
    '''Create a QTextCharFormat for Highlighter.'''
    color = QtGui.QColor(r, g, b, a)
    fmt = QtGui.QTextCharFormat()
    fmt.setForeground(color)
    if "bold" in style:
        fmt.setFontWeight(QtGui.QFont.Bold)
    if "italic" in style:
        fmt.setFontItalic(True)
    return fmt


class PatternFactory(object):

    def __init__(self, color_settings="color.settings"):
        self.colors = load_settings(color_settings)

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

        fmt = format_text(*color)

        if 'multiline' in name:
            start = QtGui.QRegexp(pattern['start'])
            end = QtGui.QRegexp(pattern['end'])
            return start, end, fmt
        else:
            match = QtGui.QRegexp(pattern['match'])
            captures = pattern['captures']
            return match, captures, fmt
