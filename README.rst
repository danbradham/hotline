=======
HotLine
=======
A pop-up input field with customizable settings. Supporting multiple modes, syntax highlighting, and inline autocompletion.

HotLine is like a supped up version of Nuke's node creator. Best of all, it works *anywhere* through the use of context modules. These modules make use of the HotLine api to add Modes and parent HotLine to an existing PySide application. Currently HotLine only comes with a Context for Autodesk Maya.

------------
Maya Context
------------
The maya context comes with several useful modes including Node Creation, Python Scripting, Mel Scripting, Scene Selection, Node Connection and Renaming.

------------------
Installing Hotline
------------------

distutils/setuptools
====================

::

    git clone git@github.com:danbradham/hotline.git
    cd hotline
    python setup.py install

pip
===

::

    pip install hotline


Making use of the Maya Context
==============================

If you're looking to use the Autodesk Maya context bind a key to the following python script:

::

    import hotline
    hotline.show()
