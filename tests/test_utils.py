from hotline import utils
from nose.tools import *
import os
import sys
from PyQt4 import QtGui, QtCore


REL = os.path.dirname(__file__)


def test_rel_path_exist():
    test_pth = os.path.abspath(os.path.join(REL, "../hotline/__init__.py"))
    eq_(utils.rel_path("__init__.py"), test_pth)


def test_rel_path_doesnt_exist():
    eq_(utils.rel_path("NONEXISTANT/PATH"), None)


def test_load_settings():
    KEYS = utils.load_settings("key.settings")
    assert(isinstance(KEYS, dict))


def test_load_keys():
    KEYS = utils.load_keys()
    for mode, hotkeys in KEYS.iteritems():
        for key_name, seq in hotkeys.iteritems():
            assert(isinstance(seq, QtGui.QKeySequence))


class TestPatternFactory:

    @classmethod
    def setup_class(cls):
        cls.factory = utils.PatternFactory()

    def test_init(self):
        assert(isinstance(self.factory.colors, dict))

    def test_format_text(self):
        fmt = self.factory.format_text(255, 255, 255, 255, "bold")
        assert(isinstance(fmt, QtGui.QTextCharFormat))

    def test_create_standard(self):
        name = "Python"
        pattern_name = "keywords"
        pattern = {
            "match": (
                "\\b(and|assert|break|continue|del|elif|else|except|exec|"
                "finally|for|from|global|if|import|in|is|lambda|not|or|"
                "pass|print|raise|return|try|while|yield)\\b"),
            "captures": 0}
        syntax_pattern = self.factory.create(name, pattern_name, pattern)
        assert isinstance(syntax_pattern[0], QtCore.QRegExp)
        assert isinstance(syntax_pattern[1], int)
        assert isinstance(syntax_pattern[2], QtGui.QTextCharFormat)

    def test_create_multiline(self):
        name = "Python"
        pattern_name = "multiline.single"
        pattern = {
            "start": "'''",
            "end": "'''"}
        syntax_pattern = self.factory.create(name, pattern_name, pattern)
        assert isinstance(syntax_pattern[0], QtCore.QRegExp)
        assert isinstance(syntax_pattern[1], QtCore.QRegExp)
        assert isinstance(syntax_pattern[2], QtGui.QTextCharFormat)
