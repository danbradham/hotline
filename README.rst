=======
Hotline
=======
Hotline is a pop-up input field written in Python with PyQt/PySide modeled after the command palette from Sublime Text. The API can be used to extend and customize Hotline by using the Context, Mode, and Command objects.


Available Contexts
==================

 - Autodesk Maya

    - Rename - rename selected nodes using hotlines Renamer minilanguage

        - **Pre_+** - adds a prefix
        - **+_Suf** - adds a suffix
        - **-rem** - removes a string
        - **search replace** - search for a string a replace it
        - **full_name_##** - full name replacement with a padded index

    - Select - select nodes using glob and regex patterns
    - Connect - connect attributes
    - Node - create DAG and DG nodes
    - Python - execute python commands
    - Mel - execute mel commands

 - Windows

    - Powershell - execute Powershell commands
    - CMD - execute Batch commands
    - Run - run
    - Python - execute python commands


Using Hotline
=============
::

    from hotline import Hotline
    hl = Hotline()
    hl.show()

Hotline will attempt to use the best available context. You can also specify one.
::

    from hotline import Hotline, MayaContext
    hl = Hotline(MayaContext)
    hl.show()


Hotline in Autodesk Maya
========================

To allow for maximum flexibility hotline doesn't do anything sneaky like use singletons or a cache to maintain instances for you. In Maya this means you'll need to keep track of an instance of the Hotline ui. Here's how I'm doing that currently::

    from hotline import Hotline
    import __main__

    if not hasattr(__main__, 'hl'):
        __main__.hl = Hotline()

    __main__.hl.show()

Create a new runtime command with the above code and bind a hotkey to it.


Install Hotline
===============
::

    pip install hotline


To Do List
==========

 - Adjust Context API to make it easier to extend existing contexts
 - Add additional dialogs to make multi-stage commands more rich
 - Create settings dialog that can be used to adjust context settings
 - Persist history and settings

completed
=========

 - **Implement input history**
