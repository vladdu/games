import io
import os
import subprocess
import sys
import unittest

from rich.console import Console
from rich.style import Style

import tictactoe as t
from tictactoe import (X, O, EMPTY, DRAW, OUT_OF_RANGE, TAKEN, Started,
                       Moved, MoveRejected, GameOver)


def board_from(s):
    """Build a board from a 9-char string using X, O and '.' for empty."""
    assert len(s) == 9
    return tuple(EMPTY if ch == "." else ch for ch in s)


class WinnerTests(unittest.TestCase):
    def test_rows(self):
        self.assertEqual(t.winner(board_from("XXXOO....")), X)
        self.assertEqual(t.winner(board_from("XX.OOOX..")), O)
        self.assertEqual(t.winner(board_from("OO....XXX")), X)

    def test_columns(self):
        self.assertEqual(t.winner(board_from("XO.XO.X..")), X)
        self.assertEqual(t.winner(board_from("XO.XO..O.")), O)
        self.assertEqual(t.winner(board_from("O.XO.X..X")), X)

    def test_diagonals(self):
        self.assertEqual(t.winner(board_from("XO.OX...X")), X)
        self.assertEqual(t.winner(board_from("XXO.O.O.X")), O)

    def test_draw(self):
        self.assertEqual(t.winner(board_from("XOXXOOOXX")), DRAW)

    def test_ongoing(self):
        self.assertIsNone(t.winner(t.new_board()))
        self.assertIsNone(t.winner(board_from("XO..X...O")))


class BestMoveTests(unittest.TestCase):
    def test_takes_immediate_win(self):
        # X to move, can win at index 2 (top row).
        board = board_from("XX.OO....")
        self.assertEqual(t.best_move(board, X), 2)

    def test_prefers_win_over_block(self):
        # O to move: O can win at 5 rather than just blocking X at 2.
        board = board_from("XX.OO.X..")
        self.assertEqual(t.best_move(board, O), 5)

    def test_blocks_immediate_loss(self):
        # O to move, X threatens top row at index 2.
        board = board_from("XX..O....")
        self.assertEqual(t.best_move(board, O), 2)

    def test_blocks_column_threat(self):
        # X to move, O threatens left column at index 6.
        board = board_from("O..OX...X")
        self.assertEqual(t.best_move(board, X), 6)

    def test_game_over_returns_none(self):
        self.assertIsNone(t.best_move(board_from("XXXOO...."), O))


class ParseMoveTests(unittest.TestCase):
    def test_number(self):
        self.assertEqual(t.parse_move(" 5 \n"), (4, None))

    def test_range_is_left_to_the_game(self):
        self.assertEqual(t.parse_move("10"), (9, None))
        self.assertEqual(t.parse_move("-1"), (-2, None))

    def test_not_a_number(self):
        for text in ("", "abc", "1.5"):
            index, error = t.parse_move(text)
            self.assertIsNone(index, text)
            self.assertTrue(error, text)


class ScriptedIO:
    """PlayerIO adapter for tests: plays the given moves (indices) and
    records every Game event. Raises EOFError when it runs out of moves,
    like a terminal reaching end of input."""

    def __init__(self, first, moves):
        self.first = first
        self.moves = list(moves)
        self.events = []

    def wants_first(self):
        return self.first

    def choose_move(self, board):
        if not self.moves:
            raise EOFError
        return self.moves.pop(0)

    def show(self, event):
        self.events.append(event)


class GameTests(unittest.TestCase):
    def test_human_first_draw(self):
        io = ScriptedIO(True, [4, 1, 3, 8, 6])
        self.assertEqual(t.play_game(io), DRAW)
        self.assertEqual(io.events, [
            Started(X, O),
            Moved(X, 4, board_from("....X...."), None),
            Moved(O, 0, board_from("O...X...."), 0),
            Moved(X, 1, board_from("OX..X...."), 0),
            Moved(O, 7, board_from("OX..X..O."), 7),
            Moved(X, 3, board_from("OX.XX..O."), 7),
            Moved(O, 5, board_from("OX.XXO.O."), 5),
            Moved(X, 8, board_from("OX.XXO.OX"), 5),
            Moved(O, 2, board_from("OXOXXO.OX"), 2),
            Moved(X, 6, board_from("OXOXXOXOX"), 2),
            GameOver(DRAW, board_from("OXOXXOXOX"), None),
        ])

    def test_computer_first_win(self):
        io = ScriptedIO(False, [1, 2])
        self.assertEqual(t.play_game(io), X)
        self.assertEqual(io.events, [
            Started(O, X),
            Moved(X, 0, board_from("X........"), 0),
            Moved(O, 1, board_from("XO......."), 0),
            Moved(X, 3, board_from("XO.X....."), 3),
            Moved(O, 2, board_from("XOOX....."), 3),
            Moved(X, 6, board_from("XOOX..X.."), 6),
            GameOver(X, board_from("XOOX..X.."), (0, 3, 6)),
        ])

    def test_illegal_moves_rejected_and_asked_again(self):
        io = ScriptedIO(True, [9, -1, 4, 4, 0, 1])
        with self.assertRaises(EOFError):
            t.play_game(io)
        self.assertEqual(io.events[1:7], [
            MoveRejected(9, OUT_OF_RANGE),
            MoveRejected(-1, OUT_OF_RANGE),
            Moved(X, 4, board_from("....X...."), None),
            Moved(O, 0, board_from("O...X...."), 0),
            MoveRejected(4, TAKEN),
            MoveRejected(0, TAKEN),
        ])
        self.assertEqual(io.events[7], Moved(X, 1, board_from("OX..X...."), 0))

    def test_quitting_propagates(self):
        io = ScriptedIO(True, [])
        with self.assertRaises(EOFError):
            t.play_game(io)
        self.assertEqual(io.events, [Started(X, O)])


class NeverLosesTests(unittest.TestCase):
    """Exhaustively try every human move sequence against the AI."""

    def _explore(self, board, turn, ai, counter):
        result = t.winner(board)
        if result is not None:
            self.assertNotEqual(
                result, t.other(ai),
                "AI (%s) lost on board %r" % (ai, board))
            counter[result] = counter.get(result, 0) + 1
            return
        if turn == ai:
            move = t.best_move(board, ai)
            self.assertIn(move, t.available_moves(board))
            self._explore(t.apply_move(board, move, ai), t.other(turn), ai,
                          counter)
        else:
            for move in t.available_moves(board):
                self._explore(t.apply_move(board, move, turn), t.other(turn),
                              ai, counter)

    def test_ai_first_never_loses(self):
        counter = {}
        self._explore(t.new_board(), X, X, counter)
        self.assertNotIn(O, counter)
        self.assertGreater(sum(counter.values()), 0)

    def test_ai_second_never_loses(self):
        counter = {}
        self._explore(t.new_board(), X, O, counter)
        self.assertNotIn(X, counter)
        self.assertGreater(sum(counter.values()), 0)


class WinningLineTests(unittest.TestCase):
    def test_lines(self):
        self.assertEqual(t.winning_line(board_from("XXXOO....")), (0, 1, 2))
        self.assertEqual(t.winning_line(board_from("XXO.O.O.X")), (2, 4, 6))

    def test_no_line(self):
        self.assertIsNone(t.winning_line(t.new_board()))
        self.assertIsNone(t.winning_line(board_from("XOXXOOOXX")))


class RenderingTests(unittest.TestCase):
    def _render(self, renderable):
        console = Console(record=True, width=60, color_system=None,
                          file=io.StringIO())
        console.print(renderable)
        return console.export_text()

    def _style(self, text):
        """Combined style of a single-glyph Text (base style + spans)."""
        style = Style.parse(str(text.style)) if text.style else Style()
        for span in text.spans:
            style += Style.parse(str(span.style))
        return style

    def test_board_has_full_grid_lines(self):
        out = self._render(t.board_table(board_from("O.X.X....")))
        for ch in "┏┳┓┣╋┫┗┻┛┃━":
            self.assertIn(ch, out, ch)
        lines = out.splitlines()
        # Horizontal separators run the full width with junctions.
        self.assertEqual(sum("╋" in line for line in lines), 2)
        self.assertEqual(lines[0].count("┳"), 2)

    def test_board_shows_pieces_and_guide_numbers(self):
        out = self._render(t.board_table(board_from("O.X.X....")))
        for ch in "OX246789":
            self.assertIn(ch, out, ch)
        self.assertNotIn("1", out)
        self.assertNotIn("3", out)
        self.assertNotIn("5", out)

    def test_cell_styles(self):
        board = board_from("O.X.X....")
        self.assertEqual(self._style(t.cell_text(board, 0)),
                         Style.parse("bold magenta"))
        self.assertEqual(self._style(t.cell_text(board, 2)),
                         Style.parse("bold cyan"))
        guide = t.cell_text(board, 1)
        self.assertEqual(guide.plain, "2")
        self.assertTrue(self._style(guide).dim)

    def test_last_move_highlighted(self):
        board = board_from("O.X.X....")
        self.assertTrue(self._style(t.cell_text(board, 0, last_move=0)).reverse)
        self.assertFalse(self._style(t.cell_text(board, 2, last_move=0)).reverse)

    def test_winning_cells_highlighted(self):
        board = board_from("XXXOO....")
        line = t.winning_line(board)
        for i in line:
            style = self._style(t.cell_text(board, i, win_line=line))
            self.assertEqual(style.bgcolor.name, "green", i)
            self.assertTrue(style.bold)
        self.assertIsNone(self._style(t.cell_text(board, 3, win_line=line))
                          .bgcolor)

    def test_player_text_colors(self):
        self.assertEqual(t.player_text(X).style, "bold cyan")
        self.assertEqual(t.player_text(O).style, "bold magenta")


HERE = os.path.dirname(os.path.abspath(__file__))


class CommandLineTests(unittest.TestCase):
    SCRIPT = os.path.join(HERE, "tictactoe.py")

    def _run(self, *args, input=""):
        env = dict(os.environ, NO_COLOR="1", COLUMNS="80",
                   PYTHONIOENCODING="utf-8")
        env.pop("FORCE_COLOR", None)
        return subprocess.run([sys.executable, self.SCRIPT] + list(args),
                              input=input, capture_output=True, text=True,
                              encoding="utf-8", env=env, timeout=30)

    def test_help(self):
        for flag in ("--help", "-h"):
            result = self._run(flag)
            self.assertEqual(result.returncode, 0, flag)
            self.assertIn("usage:", result.stdout, flag)
            self.assertIn("unbeatable", result.stdout, flag)
            # The game does not start.
            self.assertNotIn("Goodbye", result.stdout, flag)

    def test_unknown_argument(self):
        result = self._run("--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)

    def test_golden_transcript(self):
        # Two games: the human goes first (with every kind of bad input) and
        # draws, then goes second and loses. golden_transcript.txt was
        # recorded from the game before the Game / Terminal I/O split.
        moves = ["y", "abc", "10", "5", "5", "2", "4", "9", "7",
                 "maybe", "y", "n", "2", "3", "n"]
        result = self._run(input="\n".join(moves) + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(os.path.join(HERE, "golden_transcript.txt"),
                  encoding="utf-8") as f:
            self.assertEqual(result.stdout, f.read())


if __name__ == "__main__":
    unittest.main()
