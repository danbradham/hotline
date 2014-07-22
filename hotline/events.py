'''
HotLine's Events
----------------

Emitted based on various ui actions.
'''
from .core import Event

# Define all of our UI Events
# Make sure we're emitting these from the correct ui elements.
# Handlers added in controller.
store_filter = Event("Filter")
store_refresh = Event("Refresh")
store_run = Event("Run")
store_save = Event("Save")
store_load = Event("Load")
store_delete = Event("Delete")
show_help = Event("Help")
hotkey = Event("Hotkey Pressed")
tgl_tools = Event("Show Tools")
show_dock = Event("Show Dock")
tgl_auto = Event("Toggle Autocomplete")
tgl_pin = Event("Toggle Pin")
next_mode = Event("Next Mode")
prev_mode = Event("Previous Mode")
run = Event("Run")
next_hist = Event("Next History")
prev_hist = Event("Previous History")
clear_out = Event("Clear Output")
