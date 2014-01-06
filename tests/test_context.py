import hotline
from nose.tools import *


class TestContext:

    @classmethod
    def setup_class(cls):
        cls.ctx = hotline.Context()

    def test_init(self):
        #Check shared state
        assert(self.ctx.instance() is hotline.Context.instance())

    def test_decorators(self):
        @self.ctx.add_mode("A", completion_list=["a", "b"], syntax="Python")
        def a_handler(input_str):
            return "<strong>" + input_str + "<\\strong>"
        eq_(self.ctx.modes["A"].handler("hello"), "<strong>hello<\\strong>")
        eq_(self.ctx.modes["A"].completion_list, ["a", "b"])
        assert(getattr(self.ctx.modes["A"], "patterns", None)
               is not None)
        assert(getattr(self.ctx.modes["A"], "multiline_patterns", None)
               is not None)

        @self.ctx.add_completer("A")
        def a_completer():
            return ["a", "b", "c"]
        eq_(self.ctx.modes["A"].completion_list_meth(), ["a", "b", "c"])

        @self.ctx.set_show()
        def show():
            return "Showing HotLine"

        assert(hotline.show() == "Showing HotLine")
