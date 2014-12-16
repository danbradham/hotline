'''
history
=======
Maintains history for hotline.
'''


class History(object):
    '''Maintains input history for HotLine'''
    _history = [(None, '')]
    _history_index = 0

    def add(self, mode, input_str):
        command = (mode, input_str)
        if input_str:
            try:
                ind = self._history.index(command)
                if ind != 1:
                    self._history.insert(1, command)
            except ValueError:
                self._history.insert(1, command)
        self._history_index = 0

    def next(self):
        if self._history_index > 0:
            self._history_index -= 1
        return self._history[self._history_index]

    def prev(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
        return self._history[self._history_index]
