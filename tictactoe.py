#!/usr/bin/env python3
"""Shortcut that starts the games program straight into tic-tac-toe.

Same as ``python3 -m games``; see the ``games`` package.
"""

import sys

from games.tictactoe import main

if __name__ == "__main__":
    sys.exit(main())
