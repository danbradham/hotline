import hotline
from nose.tools import *
#Try PyQt then PySide imports
try:
    from PyQt4 import QtGui, QtCore
except ImportError:
    from PySide import QtGui, QtCore
import sys


class TestContext:

    @classmethod
    def setup_class(cls):
        cls.app = QtGui.QApplication(sys.argv)
        cls.hl = hotline.HotLine()

    def test_mode_init(self):

        def null_handler(input_str):
            return input_str

        def null_completer():
            return list("abc")

        A = hotline.Mode("A", null_handler)
        assert(A.name == "A")
        assert(A.completer_fn is None)
        assert(A.completer_list is not None)
        assert(A.patterns is not None)
        assert(A.multiline_patterns is not None)

        B = hotline.Mode("B", null_handler, completer_fn=null_completer,
                         syntax="Python")
        assert(B.name == "B")
        assert(B.completer_fn() == ["a", "b", "c"])
        assert(B.completer_list is not None)
        assert(B.patterns is not None)
        assert(B.multiline_patterns is not None)

    def test_add_mode(self):
        a_list = ["a", "b"]

        @hotline.add_mode("A", completer_list=a_list, syntax="Python")
        def a_handler(input_str):
            return "<strong>" + input_str + "<\\strong>"

        eq_(self.hl.mode.handler("hello"), "<strong>hello<\\strong>")
        eq_(self.hl.mode.completer_list, ["a", "b"])
        assert(self.hl.mode.patterns is not None)
        assert(self.hl.mode.multiline_patterns is not None)

    def test_show(self):

        @hotline.set_show()
        def show():
            return "SHOWING HOTLINE"

        eq_(hotline.show(), "SHOWING HOTLINE")
