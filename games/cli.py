"""The command line shared by ``python3 -m games`` and the
``python3 tictactoe.py`` shortcut: choosing the Game type, the Players and
the Difficulty."""

import argparse

from games import framework
from games.registry import GAME_TYPES

KINDS = (framework.Human.kind, framework.Computer.kind)

def games_help(game_types):
    """The ``--help`` description of ``python3 -m games``: every Game type
    with its summary, and the menu."""
    return (
        "Play turn-based board games in the terminal. Game types: %s. "
        "Without --game, a menu at startup asks which game to play (type "
        "its number)." % "; ".join("%s (%s)" % (game_type.name,
                                                game_type.summary)
                                   for game_type in game_types))


def players_help(game_types):
    """The ``--help`` paragraph on Players and Difficulty."""
    defaults = "; ".join(
        "%s %s" % (game_type.name,
                   "to the end of the game" if game_type.default_depth is None
                   else game_type.default_depth)
        for game_type in game_types)
    return (
        "Each Side is played by a human or the computer. By default you "
        "play the computer and each game asks \"Do you want to go "
        "first?\". --first and --second choose the Player for the Side that "
        "moves first and second; give both for a hot-seat game between two "
        "people at this terminal (human human) or to watch the computer "
        "play itself (computer computer). Giving only one puts the other "
        "kind of Player on the other Side. --depth sets the computer's "
        "Difficulty: how many moves ahead it looks, 1 or more. Default: %s."
        % defaults)


EPILOG = ("After each game you can play again (y/n) with the same game and "
          "Players. Press Ctrl+C or Ctrl+D to quit at any time.")


def depth(text):
    """argparse type for ``--depth``: a whole number of Moves, 1 or more."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a whole number, got %r"
                                         % text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more, got %d" % value)
    return value


def parser(prog, description, game_type=None):
    """The argument parser; with ``game_type`` there is no ``--game``."""
    game_types = GAME_TYPES.values() if game_type is None else [game_type]
    parser = argparse.ArgumentParser(
        prog=prog, description=description + " " + players_help(game_types),
        epilog=EPILOG)
    if game_type is None:
        parser.add_argument(
            "--game", choices=list(GAME_TYPES), metavar="NAME",
            help="the Game type to play, skipping the menu: %s"
                 % ", ".join(GAME_TYPES))
    parser.add_argument("--first", choices=KINDS,
                        help="who plays the Side that moves first")
    parser.add_argument("--second", choices=KINDS,
                        help="who plays the Side that moves second")
    parser.add_argument("--depth", type=depth, metavar="N",
                        help="how many moves ahead the computer looks "
                             "(1 or more; default: the game's own)")
    return parser


def player_kinds(first, second):
    """The kind of Player for each Side from the flags, or None to ask
    whether the human goes first. A missing flag is the other kind."""
    if first is None and second is None:
        return None
    other = {KINDS[0]: KINDS[1], KINDS[1]: KINDS[0]}
    return (first or other[second], second or other[first])


def main(argv, prog, description=None, game_type=None):
    """Parse ``argv`` and run a Session. With ``game_type`` the Game type
    is fixed and there is no ``--game`` flag or menu. ``description``
    defaults to one naming every registered Game type."""
    if description is None:
        description = games_help(GAME_TYPES.values())
    args = parser(prog, description, game_type).parse_args(argv)
    kinds = player_kinds(args.first, args.second)
    if game_type is None and args.game is not None:
        game_type = GAME_TYPES[args.game]
    if game_type is None:
        return framework.run_menu(GAME_TYPES.values(), kinds=kinds,
                                  depth=args.depth)
    return framework.run(game_type, kinds=kinds, depth=args.depth)
