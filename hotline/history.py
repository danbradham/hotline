'''
history
=======
Maintains history for hotline.
'''

class History(object):
    '''Maintains input history for HotLine'''
    _history = ['']
    _history_index = 0

    def add(self, input_str):
        if input_str:
            try:
                ind = self._history.index(input_str)
                if ind != 1:
                    self._history.insert(1, input_str)
            except ValueError:
                self._history.insert(1, input_str)
        self._history_index = 0

    def next(self):
        if self._history_index > 0:
            self._history_index -= 1
        return self._history[self._history_index]

    def prev(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
        return self._history[self._history_index]
