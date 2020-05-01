# -*- coding: utf-8 -*-
from __future__ import absolute_import
__title__ = 'hotline'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__license__ = 'MIT'
__url__ = 'https://github.com/danbradham/hotline.git'
__description__ = 'Sublime text like Qt Command Palette'
__version__ = '0.7.3'

import os

this_package = os.path.dirname(__file__)

from hotline import styles
from hotline.app import Hotline
from hotline.anim import *
from hotline.mode import Mode
from hotline.command import Command
from hotline.context import Context
from hotline.utils import execute_in_main_thread
from hotline.contexts import *
