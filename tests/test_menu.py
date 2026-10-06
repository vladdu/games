"""The startup menu: ``python3 -m games`` without ``--game``."""

import contextlib
import io
import os
import unittest
from unittest import mock

from rich.console import Console

from games import cli, framework
from games.registry import GAME_TYPES
from tests.support import GOLDEN_INPUT, ROOT, golden_transcript, run_program

# Three refused choices, then tic-tac-toe, played with the tic-tac-toe
# golden session (two Games, so "Play again" is answered yes once).
MENU_GOLDEN_INPUT = "0\nabc\n4\n1\n" + GOLDEN_INPUT


def menu_golden_transcript():
    with open(os.path.join(ROOT, "golden_menu_transcript.txt"), encoding="utf-8") as f:
        return f.read()


def menu(input=""):
    return run_program(["-m", "games"], input=input)


class MenuTests(unittest.TestCase):
    def test_lists_every_registered_game_type(self):
        result = menu()
        self.assertEqual(result.returncode, 0, result.stderr)
        for number, game_type in enumerate(GAME_TYPES.values(), 1):
            self.assertIn("%d. %s" % (number, game_type.title), result.stdout)

    def test_gomoku_is_the_third_entry(self):
        result = menu(input="3\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("  3. Gomoku", result.stdout)
        self.assertIn("Type a point such as e5", result.stdout)

    def test_plays_the_chosen_game_type(self):
        result = menu(input="2\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("you vs. the computer", result.stdout)
        self.assertIn("Do you want to go first? (y/n):", result.stdout)
        self.assertNotIn("Cells are numbered", result.stdout)

    def test_refuses_invalid_choices_and_asks_again(self):
        result = menu(input="0\nabc\n4\n2\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Please enter a number from 1 to 3."), 3)
        self.assertEqual(result.stdout.count("Game (1-3):"), 4)
        self.assertIn("you vs. the computer", result.stdout)

    def test_end_of_input_at_the_menu_quits(self):
        result = menu(input="")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.rstrip().endswith("Goodbye!"))
        self.assertNotIn("Do you want to go first?", result.stdout)

    def test_ctrl_c_at_the_menu_quits(self):
        out = io.StringIO()
        console = Console(file=out, width=80, color_system=None)
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            status = framework.run_menu(GAME_TYPES.values(), console)
        self.assertEqual(status, 0)
        self.assertTrue(out.getvalue().rstrip().endswith("Goodbye!"))

    def test_play_again_keeps_the_chosen_game_type(self):
        # Connect Four, human second, then play again going second: the
        # menu is not shown again and the second Game is Connect Four too.
        result = menu(input="2\nn\n" + "4\n" * 21 + "y\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertEqual(out.count("Choose a game:"), 1)
        self.assertEqual(out.count("You are Yellow, the computer is Red."), 2)

    def test_golden_transcript(self):
        result = menu(input=MENU_GOLDEN_INPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, menu_golden_transcript())

    def test_golden_transcript_is_the_menu_then_tictactoe(self):
        # The menu path adds only the menu in front of the tic-tac-toe
        # golden session.
        self.assertTrue(menu_golden_transcript().endswith(golden_transcript()))

    def test_help_describes_the_menu(self):
        result = run_program(["-m", "games"], "--help")
        self.assertEqual(result.returncode, 0)
        text = " ".join(result.stdout.split())
        self.assertIn("Without --game, a menu", text)
        self.assertNotIn("Choose a game:", text)

    def test_help_describes_every_registered_game_type(self):
        """Adding a Game type to the registry is enough for --help to
        describe it."""

        class Checkers:
            name = "checkers"
            title = "Checkers"
            summary = "Checkers on an 8x8 board; jump to capture"
            default_depth = 5

        out = io.StringIO()
        # Wide enough that argparse does not wrap inside "Tic-tac-toe".
        with (
            mock.patch.dict(GAME_TYPES, checkers=Checkers()),
            mock.patch.dict(os.environ, COLUMNS="500"),
            contextlib.redirect_stdout(out),
            self.assertRaises(SystemExit),
        ):
            cli.main(["--help"], "python3 -m games")
        text = " ".join(out.getvalue().split())
        self.assertIn("checkers (Checkers on an 8x8 board; jump to capture)", text)
        self.assertIn("tictactoe (Tic-tac-toe on a 3x3 grid", text)
        self.assertIn("connect-four (Connect Four on a 7x6 board", text)
        self.assertIn("gomoku (Gomoku on a 9x9 board", text)


if __name__ == "__main__":
    unittest.main()
