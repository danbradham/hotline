#HotLine
The popup script editor for Autodesk Maya!</br>

Inspired by Nuke's popup node creator, HotLine is a popup editor with serveral
modes:

-  **PY**thon: execute python code
-  **MEL**: execute mel code
-  **SEL**ect: select nodes using wildcards
-  **REN**ame: rename nodes using various tokens
-  **NODE**: create nodes

Each mode has it's own dropdown autocompletion list.



##Installation
Requires **PyQt4**</br>
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