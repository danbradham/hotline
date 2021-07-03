=======
Hotline
=======
Hotline is a pop-up input field written for Qt for Python modeled after the command palette from Sublime Text. The API can be used to extend and customize Hotline by using the Context, Mode, and Command objects.


Available Contexts
==================

 - Autodesk Maya

    - Rename - rename selected nodes using hotline's Renamer. The following
        tokens are available.

        - **Pre_+** - adds a prefix
        - **+_Suf** - adds a suffix
        - **-rem** - removes a substring
        - **search replace** - search for a string a replace it
        - **full_name_##** - full name replacement with a padded index
        - **full_name_##(10)** - full name replacement with padded index and
            custom start value.

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

To allow for maximum flexibility hotline doesn't do anything sneaky like use singletons or a cache to maintain instances for you. In Maya this means you'll need to keep track of an instance of the Hotline ui. Here's one way to do that::

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

