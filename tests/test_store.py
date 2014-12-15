import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
import hotline

store = hotline.Store(hotline.config_path('store.json'))
store['polySphere'] = {
    'command': 'import maya.cmds as cmds; cmds.polySphere();',
    'mode': 'PY',
    'autoload': False,
}
store.save()
