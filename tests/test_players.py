"""Choosing Players and Difficulty: hot-seat and computer-vs-computer
Games, the messages for every pairing of Players, and the ``--first``,
``--second`` and ``--depth`` flags."""

import io
import unittest
from unittest import mock

from rich.console import Console

from games import connectfour, framework, tictactoe
from games.framework import (DRAW, Computer, GameOver, Human, Moved,
                             MoveRejected, Started, play_game)
from tests.support import ScriptedIO, run_program

TTT = tictactoe.GAME_TYPE
C4 = connectfour.GAME_TYPE


class WholeGameTests(unittest.TestCase):
    def test_hot_seat_game_asks_each_side_in_turn(self):
        # X: 7 8 9 across the top; O answers 4 5.
        io_ = ScriptedIO(["7", "4", "8", "5", "9"])
        result = play_game(TTT, (Human(), Human()), io_)
        self.assertEqual(result, tictactoe.X)
        self.assertEqual(io_.prompts, ["X", "O", "X", "O", "X"])
        self.assertEqual([e.side for e in io_.of_type(Moved)],
                         ["X", "O", "X", "O", "X"])

    def test_hot_seat_rejected_move_asks_the_same_side_again(self):
        io_ = ScriptedIO(["5", "5", "1", "8", "2", "9", "3"])
        result = play_game(TTT, (Human(), Human()), io_)
        self.assertEqual(len(io_.of_type(MoveRejected)), 1)
        self.assertEqual(io_.prompts[:3], ["X", "O", "O"])
        self.assertEqual(result, tictactoe.O)

    def test_computer_vs_computer_tictactoe_at_full_difficulty_is_a_draw(self):
        io_ = ScriptedIO()
        result = play_game(TTT, (Computer(), Computer()), io_)
        self.assertEqual(result, DRAW)
        self.assertEqual(io_.prompts, [])
        self.assertEqual(len(io_.of_type(Moved)), 9)

    def test_computer_vs_computer_connect_four_ends_with_a_result(self):
        io_ = ScriptedIO()
        result = play_game(C4, (Computer(2), Computer(3)), io_)
        self.assertIn(result, (connectfour.RED, connectfour.YELLOW, DRAW))
        self.assertEqual(io_.prompts, [])
        self.assertEqual(len(io_.of_type(GameOver)), 1)

    def test_quitting_in_a_hot_seat_game_propagates(self):
        with self.assertRaises(EOFError):
            play_game(TTT, (Human(), Human()), ScriptedIO(["5"]))


def shown(game_type, *events):
    out = io.StringIO()
    terminal = framework.TerminalIO(game_type, Console(file=out, width=80,
                                                       color_system=None))
    for event in events:
        terminal.show(event)
    return out.getvalue()


def final_state(game_type, players, texts=()):
    io_ = ScriptedIO(texts, game_type=game_type)
    play_game(game_type, players, io_)
    return io_.of_type(GameOver)[0]


class MessageTests(unittest.TestCase):
    def test_one_human_keeps_todays_intro(self):
        out = shown(C4, Started((Computer(4), Human()), C4.initial_state()))
        self.assertIn("You are Yellow, the computer is Red. Red moves first.",
                      out)

    def test_hot_seat_intro_names_each_sides_player(self):
        out = shown(TTT, Started((Human(), Human()), TTT.initial_state()))
        self.assertIn("X: human, O: human. X moves first.", out)
        self.assertNotIn("You are", out)

    def test_computer_intro_names_its_difficulty(self):
        out = shown(C4, Started((Computer(4), Computer(6)),
                                C4.initial_state()))
        self.assertIn("Red: computer (depth 4), Yellow: computer (depth 6). "
                      "Red moves first.", out)

    def test_unlimited_difficulty_is_named_full_depth(self):
        out = shown(TTT, Started((Computer(), Computer(3)),
                                 TTT.initial_state()))
        self.assertIn("X: computer (full depth), O: computer (depth 3).", out)

    def test_hot_seat_end_message_names_the_winning_side(self):
        players = (Human(), Human())
        over = final_state(TTT, players, ["7", "4", "8", "5", "9"])
        out = shown(TTT, Started(players, TTT.initial_state()), over)
        self.assertIn("X wins!", out)
        self.assertNotIn("You win", out)

    def test_computer_vs_computer_end_message_names_the_winner_or_draw(self):
        players = (Computer(1), Computer(4))
        over = final_state(C4, players)
        out = shown(C4, Started(players, C4.initial_state()), over)
        expected = {connectfour.RED: "Red wins!",
                    connectfour.YELLOW: "Yellow wins!",
                    DRAW: "It's a draw!"}[over.result]
        self.assertIn(expected, out)
        self.assertNotIn("computer wins", out)

    def test_hot_seat_prompt_names_the_side_to_move(self):
        out = io.StringIO()
        console = Console(file=out, width=80, color_system=None)
        terminal = framework.TerminalIO(TTT, console)
        terminal.show(Started((Human(), Human()), TTT.initial_state()))
        with mock.patch("builtins.input", return_value="5"):
            terminal.ask_move("X")
        self.assertIn("X: Your move (1-9):", out.getvalue())


def games(*args, input=""):
    return run_program(["-m", "games"], *args, input=input)


class CommandLineTests(unittest.TestCase):
    def test_hot_seat_from_the_command_line(self):
        result = games("--game", "tictactoe", "--first", "human",
                       "--second", "human",
                       input="7\n4\n8\n5\n9\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("X: human, O: human. X moves first.", out)
        self.assertNotIn("Do you want to go first?", out)
        self.assertIn("X wins!", out)

    def test_intro_names_the_pairing(self):
        for kinds, subtitle in ((("human", "human"), "human vs. human"),
                                (("computer", "computer"),
                                 "computer vs. computer")):
            result = games("--game", "connect-four", "--first", kinds[0],
                           "--second", kinds[1], "--depth", "1",
                           input="")
            self.assertIn(subtitle, result.stdout)
            self.assertNotIn("you vs.", result.stdout)

    def test_computer_vs_computer_from_the_command_line(self):
        result = games("--game", "tictactoe", "--first", "computer",
                       "--second", "computer", input="n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("X: computer (full depth), O: computer (full depth).",
                      out)
        self.assertEqual(out.count("Computer ("), 9)
        self.assertIn("It's a draw!", out)

    def test_one_flag_puts_the_computer_on_the_other_side(self):
        result = games("--game", "tictactoe", "--first", "computer",
                       input="8\n9\n4\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("You are O, the computer is X.", result.stdout)
        self.assertNotIn("Do you want to go first?", result.stdout)
        result = games("--game", "tictactoe", "--second", "computer",
                       input="")
        self.assertIn("You are X, the computer is O.", result.stdout)

    def test_play_again_keeps_the_players(self):
        result = games("--game", "tictactoe", "--first", "computer",
                       "--second", "computer", input="y\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertEqual(out.count("X: computer (full depth), "
                                   "O: computer (full depth)."), 2)
        self.assertNotIn("Do you want to go first?", out)

    def test_depth_sets_the_difficulty(self):
        result = games("--game", "connect-four", "--first", "computer",
                       "--second", "computer", "--depth", "2", input="n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Red: computer (depth 2), Yellow: computer (depth 2).",
                      result.stdout)

    def test_depth_drops_the_should_not_happen_suffix(self):
        # Looking one Move ahead, the computer walks into a fork.
        result = games("--game", "tictactoe", "--depth", "1",
                       input="y\n7\n9\n5\n1\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("You win!\n", result.stdout)
        self.assertNotIn("should not happen", result.stdout)
        self.assertNotIn("unbeatable", result.stdout)
        self.assertIn("you vs. the computer", result.stdout)

    def test_depth_applies_after_the_menu(self):
        result = run_program(["-m", "games"], "--first", "computer",
                             "--second", "computer", "--depth", "1",
                             input="2\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Red: computer (depth 1), Yellow: computer (depth 1).",
                      result.stdout)

    def test_default_depth_is_the_chosen_game_types(self):
        result = run_program(["-m", "games"], "--first", "computer",
                             "--second", "computer", input="2\nn\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Red: computer (depth %d), Yellow: computer (depth %d)."
                      % (C4.default_depth, C4.default_depth), result.stdout)

    def test_invalid_flag_values_are_errors(self):
        for args in (["--first", "robot"], ["--second", "alien"],
                     ["--depth", "0"], ["--depth", "-3"],
                     ["--depth", "abc"]):
            result = games("--game", "tictactoe", *args)
            self.assertEqual(result.returncode, 2, args)
            self.assertIn("usage:", result.stderr, args)
            self.assertEqual(result.stdout, "", args)

    def test_help_describes_players_and_difficulty(self):
        result = games("--help")
        self.assertEqual(result.returncode, 0)
        text = " ".join(result.stdout.split())
        for phrase in ("--first", "--second", "--depth", "human",
                       "computer", "Do you want to go first?"):
            self.assertIn(phrase, text)

    def test_tictactoe_shortcut_takes_the_same_flags(self):
        result = run_program(["tictactoe.py"], "--first", "computer",
                             "--second", "computer", input="n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("It's a draw!", result.stdout)
        self.assertNotIn("Choose a game:", result.stdout)
        help_ = run_program(["tictactoe.py"], "--help")
        self.assertIn("--depth", help_.stdout)
        self.assertNotIn("--game", help_.stdout)


if __name__ == "__main__":
    unittest.main()
