import sys

from hotline.contexts.bare import BareContext
from hotline.contexts.maya import MayaContext
from hotline.contexts.win import WindowsContext


def best_context():
    """Return the best possible context"""

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
        raise NotImplementedError("Nuke context not implemented")

    platform = sys.platform.rstrip("1234567890")

    if platform == "darwin":
        # TODO return MacContext
        return BareContext

    if platform == "win":
        return WindowsContext

    if platform == "linux":
        # TODO return LinuxContext
        return BareContext

    return BareContext
