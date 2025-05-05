__title__ = "hotline"
__author__ = "Dan Bradham"
__email__ = "danielbradham@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/danbradham/hotline.git"
__description__ = "Popup command palette for Autodesk Maya. Create, rename, select, and connect nodes - FAST."
__version__ = "1.0.0"

import os

this_package = os.path.dirname(__file__)

from hotline import styles
from hotline.anim import *
from hotline.app import Hotline
from hotline.command import Command
from hotline.context import Context
from hotline.contexts import *
from hotline.mode import Mode
from hotline.utils import execute_in_main_thread
