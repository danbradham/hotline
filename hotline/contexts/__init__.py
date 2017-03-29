# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
from .maya import MayaContext
# from .nuke import NukeContext
from .win import WindowsContext
# from .linux import LinuxContext
# from .mac import MacContext
from .bare import BareContext

def best_context():
    '''Return the best possible context'''

    try:
        import maya.cmds
    except ImportError:
        pass
    else:
        return MayaContext

    try:
        import nuke
    except ImportError:
        pass
    else:
        raise NotImplementedError('Nuke context not implemented')

    platform = sys.platform.rstrip('1234567890')

    if platform == 'darwin':
        # TODO return MacContext
        return BareContext

    if platform == 'win':
        return WindowsContext

    if platform == 'linux':
        # TODO return LinuxContext
        return BareContext

    return BareContext
