# Hotline

Hotline is a pop-up input field written for Qt for Python modeled after the command palette from Sublime Text. The API can be used to extend and customize Hotline by using the Context, Mode, and Command objects.

## Available Contexts

### Autodesk Maya

- **Rename** - rename selected nodes using hotline's Renamer. The following tokens are available:
  - **Pre_+** - adds a prefix
  - **+_Suf** - adds a suffix
  - **-rem** - removes a substring
  - **search replace** - search for a string and replace it
  - **full_name_##** - full name replacement with a padded index
  - **full_name_##(10)** - full name replacement with padded index and custom start value.

- **Select** - select nodes using glob and regex patterns
- **Connect** - connect attributes
- **Node** - create DAG and DG nodes
- **Python** - execute Python commands
- **Mel** - execute MEL commands

### Windows

- **Powershell** - execute Powershell commands
- **CMD** - execute Batch commands
- **Run** - run applications
- **Python** - execute Python commands

## Using Hotline

```python
from hotline import Hotline
hl = Hotline()
hl.show()
```

Hotline will attempt to use the best available context. You can also specify one:

```python
from hotline import Hotline, MayaContext
hl = Hotline(MayaContext)
hl.show()
```

## Hotline in Autodesk Maya

Hotline supports a convenient method for launching a builtin instance of Hotline.

```python
import hotline
hotline.show()
```

Create a new runtime command with the above code and bind a hotkey to it.

## Install Hotline from Pypi

```bash
pip install hotline
```
