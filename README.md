#HotLine
The popup script editor for Autodesk Maya!


##Requirements

  -  PyQt4

##Installation
Place hotline.py in your scripts directory.
Set a hotkey to the following python script:
```python
import maya.cmds as cmds
try:
    hl.enter()
except:
    from hotline import HotLine
    hl = HotLine()
    hl.enter()
```

##Key Bindings
    
  -  Up and Down - Shuffle through Hotline history
  -  Tab key - Change input mode
