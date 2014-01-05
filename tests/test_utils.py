from hotline import utils
from nose.tools import *
import os


def test_rel_path():
    path = utils.rel_path("../hotline/__init__.py")
    eq_ path == os.sep.join(["C:", "PROJECTS", "HotLine", "hotline", "__init__.py"])


def test_load_settings():
    KEYS = utils.load_settings('key.settings')
    eq_ isinstance(KEYS, dict)


def test_load_keys():
    KEYS = utils.load_keys()
    for mode, hotkeys in KEYS.iteritems():
        for key_name, seq in hotkeys.iteritems():
            eq_ isinstance(seq, QtGui.QKeySequence)


def setup_PatternFactory():
    pf = utils.PatternFactory()


@with_setup(setup_PatternFactory)
def test_PatternFactory_init():
    eq_ isinstance(pf.colors, dict)


@with_setup(setup_PatternFactory)
def test_PatternFactory_format_text():
    fmt = pf.format_text(255, 255, 255, 255, "bold")
    eq_ isinstance(fmt, QtGui.QTextCharFormat)
