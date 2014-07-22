from .views import Base, Dock, Editor
from .events import *
from contexts import CTX


class HotLine(Base):

    def __init__(self, parent=None):
        super(HotLine, self).__init__(parent)

        self.dock = Dock(parent)
