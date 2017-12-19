# -*- coding: utf-8 -*-
from collections import namedtuple


ModeCommand = namedtuple('ModeCommand', 'mode command')


class History(object):

    def __init__(self):
        self._list = [None]
        self.index = 0

    def add(self, item):
        self._list.insert(1, item)
        self.index = 0

    def insert(self, index, item):
        self._list.insert(index, item)
        self.index = index

    def next(self):
        self.index = max(self.index - 1, 0)
        return self._list[self.index]

    def prev(self):
        self.index = min(self.index + 1, len(self._list) - 1)
        return self._list[self.index]
