'''
HotLine's Events
----------------

Emitted based on various ui actions.
'''
import logging
logger = logging.getLogger("hotline.events")


def receives(event):
    def wrapper(fn):
        fn.event = event
        fn.is_receiver = True
        return fn
    return wrapper


class MetaEvent(type):

    def __new__(cls, name, bases, attrs):

        self = super(MetaEvent, cls).__new__(cls, name, bases, attrs)
        self.handlers = set()
        self.description = self.__doc__
        return self


class Event(object):
    __metaclass__ = MetaEvent

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.send(*args, **kwargs)

    def send(self, *args, **kwargs):
        logger.debug(
            "Sending {0}".format(self.__class__.__name__))

        results = []
        for handler in self.handlers:
            results.append(handler(*args, **kwargs))

        if hasattr(self, "completed"):
            self.completed(*results)

    @classmethod
    def create(cls, name):
        event = type(name, (cls,), {})
        return event

    @classmethod
    def calls(cls, fn):
        logger.debug(
            "{0} now calls {1}".format(cls.__name__, fn))
        cls.handlers.add(fn)
        return cls

    @classmethod
    def doesntcall(cls, fn):
        logger.debug(
            "{0} no longer calls {1}".format(cls.__name__, fn))
        cls.handlers.remove(fn)
        return cls

    @classmethod
    def count(cls):
        return len(cls.handlers)


# Define all of our UI Events
# Make sure we're emitting these from the correct ui elements.
# Handlers added in controller.
class Filter(Event):
    '''Filter store tabs list'''

class Refresh(Event):
    '''Refresh store tabs list'''


class Run(Event):
    '''Run store tabs selected item'''


class Save(Event):
    '''Save script to store'''


class Load(Event):
    '''Load script from store'''


class Delete(Event):
    '''Delete script from store'''


class Help(Event):
    '''Display help in output tab'''


class HotkeyPressed(Event):
    '''Hotkey emitted event'''


class ShowTools(Event):
    '''Show tools'''


class ShowDock(Event):
    '''Show dock'''


class ToggleAutocomplete(Event):
    '''Toggle Autocomplete'''

    completed = Event.create("completed")

class TogglePin(Event):
    '''Toggle Pin'''

    completed = Event.create("completed")

class ToggleMultiline(Event):
    '''Toggle Multiline'''

    completed = Event.create("completed")

class NextMode(Event):
    '''Next Mode'''

    completed = Event.create("completed")

class PreviousMode(Event):
    '''Previous Mode'''

    completed = Event.create("completed")

class NextHistory(Event):
    '''Next in History'''

    completed = Event.create("completed")

class PreviousHistory(Event):
    '''Previous in History'''

    completed = Event.create("completed")

class ClearOutput(Event):
    '''Clear output tab'''
