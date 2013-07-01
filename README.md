HotLine
=======
Dan Bradham 2013

A convenient popup script editor.
Use the up and down keys to shuffle through HotLine History.


Requirements:

1. PyQt4 installed in a location available to Maya.

Installation:

1. Place hotline.py in your scripts directory.
2. Set a hotkey to the following python script:

import maya.cmds as cmds
try:
    hl.enter()
except:
    from hotline import HotLine
    hl = HotLine()
    hs.enter()