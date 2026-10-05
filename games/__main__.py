"""Entry point: ``python3 -m games [--game NAME]``."""

import argparse
import sys

from games import connectfour, tictactoe

# Game type names on the command line, and how to start each one.
GAME_TYPES = {
    "tictactoe": tictactoe.run,
    "connect-four": connectfour.run,
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m games",
        description="Play turn-based board games in the terminal against "
                    "the computer. Game types: tictactoe (Tic-tac-toe on a "
                    "3x3 grid against an unbeatable computer; enter a cell "
                    "number 1-9, numbered like a numeric keypad) and "
                    "connect-four (Connect Four on a 7x6 board; enter a "
                    "column number 1-7 to drop a disc, Red moves first). "
                    "You choose whether to go first.",
        epilog="After each game you can play again (y/n). "
               "Press Ctrl+C or Ctrl+D to quit at any time.")
    parser.add_argument(
        "--game", choices=list(GAME_TYPES), default="tictactoe",
        metavar="NAME",
        help="the Game type to play: %s (default: tictactoe)"
             % ", ".join(GAME_TYPES))
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    return GAME_TYPES[args.game]()


sys.exit(main())
