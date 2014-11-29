from .shout import Message


class ToggleMultiline(Message):
    '''Shout to toggle multiline'''


class ToggleAutocomplete(Message):
    '''Shout to toggle autocomplete'''


class ToggleToolbar(Message):
    '''Shout to toggle toolbar'''


class TogglePin(Message):
    '''Shout to toggle pin'''


class NextMode(Message):
    '''Shout to go to next mode'''


class PrevMode(Message):
    '''Shout to go to previous mode'''


class NextHistory(Message):
    '''Shout to go to next in history'''


class PrevHistory(Message):
    '''Shout to go to previous in history'''


class Execute(Message):
    '''Shout to execute string'''


class ShowDock(Message):
    '''Shout to show dock'''


class ShowHelp(Message):
    '''Shout to show help'''


class ClearOutput(Message):
    '''Shout to clear output'''


class AdjustSize(Message):
    '''Shout to adjust size'''


class Store_Run(Message):
    '''Shout to run selected item in store'''


class Store_Save(Message):
    '''Shout to save current text to store'''


class Store_Load(Message):
    '''Shout to load selected item in store'''


class Store_Delete(Message):
    '''Shout to delete selected item in store'''


class Store_Refresh(Message):
    '''Shout to refresh store'''
