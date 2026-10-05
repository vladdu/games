"""Entry point: ``python3 -m games [--game NAME] [--first KIND]
[--second KIND] [--depth N]``. Without ``--game`` a startup menu asks which
Game type to play."""

import sys

from games import cli

DESCRIPTION = (
    "Play turn-based board games in the terminal. Game types: tictactoe "
    "(Tic-tac-toe on a 3x3 grid; enter a cell number 1-9, numbered like a "
    "numeric keypad) and connect-four (Connect Four on a 7x6 board; enter "
    "a column number 1-7 to drop a disc, Red moves first). Without --game, "
    "a menu at startup asks which game to play (type its number).")

sys.exit(cli.main(None, "python3 -m games", DESCRIPTION))
