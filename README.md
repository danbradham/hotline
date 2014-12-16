#HotLine
A pop-up input field with customizable settings. Supporting multiple modes, syntax highlighting, and inline autocompletion.</br>

![hotline-header][hotline-header]
HotLine is like a supped up version of Nuke's node creator.  Best of all, it works *anywhere* through the use of context modules.  These modules make use of the HotLine api to add Modes and parent HotLine to any existing PyQt application. One prepackaged context is for Autodesk Maya.

#HotLine's Maya Context
There are five different modes in HotLine's Maya context.

| Mode       | Usage                                                      | Auto-Completes   |
| ---------- | ---------------------------------------------------------- | ---------------- |
| **PY**thon | execute python script                                      | maya.cmds module |
| **MEL**    | execute mel script                                         | mel commands     |
| **SEL**ect | select scene nodes using standard Maya selection wildcards | scene nodes      |
| **REN**ame | rename selected nodes using a mini token language          | N/A              |
| **NODE**   | create scene nodes                                         | Maya scene nodes |
| **CNCT**   | connect attributes                                         | Maya scene nodes |


##Node Mode
![hotline-node][hotline-node]
Node creation mode is almost exactly like Nuke's node creator.  Simply input the node you'd like to create and press return.  There is one added feature for convenience, if you input a second string, this will be the name of the newly created node.


##Rename Mode
The rename mode requires a bit of instruction.  I created a simple token language to give users all the renaming functionality of scripts like Comet's renamer without multiple input fields.  Let's go through the various tokens available in rename mode.

**selected nodes:** joint1, joint2, joint3

![hotline-pound][hotline-pound]
>**results:** arm_01_BIND, arm_02_BIND, arm_03_BIND
>A single string renames the selected nodes.  "#" symbols are replaced with a sequence of numbers.  Using multiple "#" increases the padding of the digit.

![hotline-prefix][hotline-prefix]
>**results:** L_arm_01_BIND, L_arm_02_BIND, L_arm_03_BIND
>"+" adds a prefix if it comes after the input string.

![hotline-suffix][hotline-suffix]
>**results:** L_arm_01_BIND_JNT, L_arm_02_BIND_JNT, L_arm_03_BIND_JNT
>"+" adds a suffix if it comes before the input string.

![hotline-remove][hotline-remove]
>**results:** L_arm_01_JNT, L_arm_02_JNT, L_arm_03_JNT
>Removes the string following "-" from each of the selected nodes.

![hotline-replace][hotline-replace]
>**results:** R_arm_01_JNT, R_arm_02_JNT, R_arm_03_JNT
>If two strings are input, the first string is replaced by the second.


##Dependencies
-  PyQt4 or PySide

PyQt4 or PySide is required to use HotLine.  Unfortunately, Autodesk compiled Python with Visual Studio 2010. So you can't use one of the official builds of PyQt4 if you're looking to use the Maya Context.  [Nathan Horne][Nathan Horne] has links to windows binaries for PyQt4 and PySide compiled against Maya 2013 and Maya 2012, these will work just fine. If you're using Maya 2014 try HotLine out of the box. Maya 2014 is supposed to come packaged with PySide, though, I haven't tested it out myself.


##Getting HotLine
```
git clone git@github.com:danbradham/HotLine.git
cd HotLine
python setup.py install
```

If you're looking to use the Autodesk Maya context bind a key to the following python script:
```python
import hotline
import hotline.contexts.mayactx
hotline.show()
```


[Nathan Horne]: http://nathanhorne.com/
[hotline-header]: http://danbradham.github.io/images/hotline-header.png
[hotline-pound]: http://danbradham.github.io/images/hotline-pound.png
[hotline-prefix]: http://danbradham.github.io/images/hotline-prefix.png
[hotline-suffix]: http://danbradham.github.io/images/hotline-suffix.png
[hotline-remove]: http://danbradham.github.io/images/hotline-remove.png
[hotline-replace]: http://danbradham.github.io/images/hotline-replace.png
[hotline-node]: http://danbradham.github.io/images/hotline-node.png
