# -----------------------------------------------------------------------------
# Copyright © 2009- The QtPy Contributors
#
# Released under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Dev CLI entry point for QtPy, a compat layer for the Python Qt bindings."""

from . import cli


def main():
    return cli.main()


if __name__ == "__main__":
    main()
