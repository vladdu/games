"""Entry point: ``python3 -m games [--game NAME]``. Without ``--game`` a
startup menu asks which Game type to play."""

import argparse
import sys

from games import framework
from games.registry import GAME_TYPES


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m games",
        description="Play turn-based board games in the terminal against "
                    "the computer. Game types: tictactoe (Tic-tac-toe on a "
                    "3x3 grid against an unbeatable computer; enter a cell "
                    "number 1-9, numbered like a numeric keypad) and "
                    "connect-four (Connect Four on a 7x6 board; enter a "
                    "column number 1-7 to drop a disc, Red moves first). "
                    "You choose whether to go first. Without --game, a menu "
                    "at startup asks which game to play (type its number).",
        epilog="After each game you can play the same game again (y/n). "
               "Press Ctrl+C or Ctrl+D to quit at any time.")
    parser.add_argument(
        "--game", choices=list(GAME_TYPES),
        metavar="NAME",
        help="the Game type to play, skipping the menu: %s"
             % ", ".join(GAME_TYPES))
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.game is None:
        return framework.run_menu(GAME_TYPES.values())
    return framework.run(GAME_TYPES[args.game])


sys.exit(main())
