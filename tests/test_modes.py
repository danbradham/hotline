import hotline
from nose.tools import *


class TestContext:

    def test_init(self):
        def null_handler(input_str):
            return input_str
        A = hotline.Mode("A", null_handler)
        assert(A.name == "A")
        assert(A.completer_fn is None)
        assert(A.completion_list is not None)
        assert(getattr(A, "patterns", None) is None)
        assert(getattr(A, "multiline_patterns", None) is None)

    def test_decorators(self):
        @hotline.create_mode(completion_list=["a", "b"], syntax="Python")
        def A(input_str):
            return "<strong>" + input_str + "<\\strong>"

        eq_(A("hello"), "<strong>hello<\\strong>")
        eq_(A.completion_list, ["a", "b"])
        assert(A.patterns is not None)
        assert(A.multiline_patterns is not None)

        @A.completer
        def A_completer():
            return ["a", "b", "c"]
        eq_(A.completer_fn(), ["a", "b", "c"])
