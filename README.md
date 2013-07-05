HotLine
=======
Dan Bradham 2013

The popup script editor!


Requirements:

    PyQt4 installed in a location available to Maya.

Installation:

    Place hotline.py in your scripts directory.
    Set a hotkey to the following python script:

    import maya.cmds as cmds
    try:
        hl.enter()
    except:
        from hotline import HotLine
        hl = HotLine()
        hl.enter()

Key Bindings:
    
    Up and Down keys - Hotline history
    Tab key - change mode
