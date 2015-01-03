'''
Shout
=====

**Loud Python messaging.**

Shout is a single module providing simple messaging vocabulary for small applications. Shout is NOT a distributed messaging framework.

::

    from shout import Message, hears, shout

    class WhoAreYou(Message):
        pass

    @hears(WhoAreYou)
    def lucky_day():
        return "We are..."

    @hears(WhoAreYou)
    def dusty_bottoms():
        return "The threeee..."

    @hears(WhoAreYou)
    def ned_nederlander():
        return "Amigos!!"

    msg = shout(WhoAreYou)
    print("".join(msg.results))

    # We are...The threeee...Amigos!!
'''

from __future__ import unicode_literals


__author__ = "Dan Bradham"
__email__ = "danieldbradham@gmail.com"
__version__ = "0.2.2"
__license__ = "MIT"
__description__ = "Loud python messaging!"
__url__ = "http://github.com/danbradham/shout"
__all__ = ["Message", "has_ears", "hears", "shout"]


import inspect
import sys
import collections
import itertools
import logging


LFMT = '%(asctime)-15s [%(name)s %(levelname)s] %(message)s'
DFMT = '%Y-%m-%d %H:%M:%S'
FMT = logging.Formatter(LFMT, DFMT)
shandler = logging.StreamHandler()
shandler.setFormatter(FMT)
logger = logging.getLogger('Shout!')
logger.addHandler(shandler)
logger.setLevel(logging.CRITICAL)


ROOM_DEFL = "void"


class MetaMsg(type):
    '''Metaclass adding a listeners dict to each subclass allowing them to keep
    track of their own listeners.'''

    def __new__(kls, name, bases, members):

        cls = super(MetaMsg, kls).__new__(kls, name, bases, members)
        cls.listeners = collections.defaultdict(set)
        logger.debug('New Message type: %s', name)
        return cls

MetaMetaMsg = MetaMsg(str("MetaMetaMsg"), (), {}) # 2n3 compatible metaclass

class Message(MetaMetaMsg):
    ''':class:`Message` s keep track of their listeners and the various rooms
    they are listening to. Instances of :class:`Message` hold args and kwargs
    and when :meth:`shout` is called these are passed to all the appropraite
    listeners. All return values of listeners are collected in
    :attr:`response`. If all listeners execute correctly :attr:`success` is
    set to True. Any Exception raised by a listener will halt the shout after
    binding :attr:`exc` to the offending Exception.

    :param args: Arguments to shout
    :param kwargs: Keyword Arguments to shout
    '''

    def __init__(self, *args, **kwargs):

        try:
            self.rooms = kwargs.pop("inside")
            if isinstance(self.rooms, str):
                self.rooms = (self.rooms, )
        except KeyError:
            self.rooms = (ROOM_DEFL,)
        self.args = args
        self.kwargs = kwargs
        self.response = []
        self.exc = None
        self.success = False
        logger.debug("{0}".format(self))

    def __repr__(self):
        rpr = '{0}({1}, {2})'
        return rpr.format(self.__class__.__name__, self.args, self.kwargs)

    def shout(self):
        '''Sends the instances args and kwargs to the
        appropriate listeners.'''
        logger.debug("Shouting {0}!".format(self.__class__.__name__))

        rooms = (self.listeners[r] for r in self.rooms)
        listeners = itertools.chain.from_iterable(rooms)

        for listener in listeners:
            try:
                response = listener(*self.args, **self.kwargs)
                self.response.append(response)
            except:
                self.exc = sys.exc_info()
                logger.error('%s FAIL!', listener.__name__, exc_info=True)
                return self
        if not self.response:
            self.exc = UserWarning("No listeners in: {0}".format(self.rooms))
            logger.warning(self.exc)
            return self

        self.success = True
        logger.debug("SUCCESS!")
        return self

    @classmethod
    def add_listener(cls, fn):
        for room in fn.rooms:
            cls.listeners[room].add(fn)
        logger.debug("%s hears %s in %s", fn.__name__, cls.__name__, fn.rooms)
        return cls

    @classmethod
    def rem_listener(cls, fn):
        for room in cls.listeners.values():
            room.discard(fn)
        logger.debug("%s no longer hears %s", fn.__name__, cls.__name__)
        return cls

    @staticmethod
    def create(name):
        '''Dynamically create a new type of :class:`Message`.

        :param name: The __class__.__name__ to use.
        '''
        message = type(name, (Message,), {})
        return message


def has_ears(cls):
    '''Class decorator that enables :func:`hears` decorator to be used on
    class methods.
    '''
    cls_init = cls.__init__

    def __init__(self, *args, **kwargs):

        members = inspect.getmembers(self.__class__)
        for name, member in members:
            if getattr(member, "has_ears", False):
                method = getattr(self, member.__name__)
                for msg_type in member.msg_types:
                    msg_type.add_listener(method)
        cls_init(self, *args, **kwargs)
        logger.debug('%s has ears!', cls.__name__)

    cls.__init__ = __init__
    return cls


def typecheck_args(args):
    '''Ensures all args are of type Message.'''
    if isinstance(args, collections.Sequence):
        for item in args:
            if not item in Message.__subclasses__():
                raise TypeError(
                    "All arguments passed to hears must be"
                    " subclasses of Message")
        return True

    raise TypeError(
        "Wrong argument signature passed to hears decorator..."
        "Pass a Message subclass or multiple Message subclasses.")


def hears(*args, **kwargs):
    '''Decorates functions and methods, adding them as listeners to the
    specified :class:`Message` s.

    :param args: :class:`Message` s this function will hear.
    :param inside: Tuple of rooms this function will hear.'''
    def wrapper(fn):

        typecheck_args(args) # Make sure all our args are Message Subclasses

        fn.has_ears = True
        fn.msg_types = args
        fn.rooms = kwargs.get("inside", (ROOM_DEFL,))

        if isinstance(fn.rooms, str):
            fn.rooms = (fn.rooms,)

        argspec = inspect.getargspec(fn)
        if argspec.args and argspec.args[0] == "self":
            return fn

        for msg_type in fn.msg_types:
            msg_type.add_listener(fn)
        return fn
    return wrapper


def shout(msg_type, *args, **kwargs):
    '''A grammatically pleasant way to shout a :class:`Message`.

    shout(Message, "Hello", inside="A") == Message("Hello", inside="A").shout()

    :param msg_type: The type of :class:`Message` to shout.
    :param args: The args to pass to the :class:`Message`.
    :param kwargs: The kwargs to pass to the :class:`Message`.
    :param inside: The rooms to shout inside.'''
    return msg_type(*args, **kwargs).shout()
