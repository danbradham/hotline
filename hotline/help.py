'''
help.py
-------
Generate a help string for HotLine.
'''

from .settings import Settings

keys = Settings("key.hotline-settings")

#Generate hotkey table
col1_max = max([len(key) for key in keys["standard"].keys()]) + 1
col2_max = max([len(value) for value in keys["standard"].values()]) + 2
col3_max = max([len(value) for value in keys["multiline"].values()]) + 1
row_template = "| {0:<{col1_max}}| {1:<{col2_max}}| {2:<{col3_max}}|"
hotkey_table = []
for command, hotkey in keys["standard"].iteritems():
    row = row_template.format(
        command,
        hotkey,
        keys["multiline"][command],
        col1_max=col1_max,
        col2_max=col2_max,
        col3_max=col3_max)
    hotkey_table.append(row)

help_string = '''
|        Hotkey       | singleline |   multiline    |
| ------------------- | ---------- | -------------- |
{hotkeys}
'''.format(hotkeys="\n".join(hotkey_table))

help_html = '''

<html>
<a href="http://danbradham.com">Dan Bradham</a> 2014</b>
Visit <a href="http://github.com/danbradham/HotLine">Github</a> for more help
and the latest information regarding HotLine.
</html>
'''
