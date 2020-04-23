# -*- coding: utf-8 -*-
# Standard library imports
import sys

# Local imports
from hotline import Hotline


if __name__ == '__main__':
    style = None
    if len(sys.argv) == 2:
        style = sys.argv[1]
    hl = Hotline(style=style)
    hl.show()
