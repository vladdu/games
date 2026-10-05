import io
import os
import unittest

from rich.console import Console
from rich.style import Style

from games import framework
from games.framework import (DRAW, Computer, GameOver, Human, Moved,
                             MoveRejected, Started, play_game)
from games.tictactoe import (EMPTY, GAME_TYPE as game, O, OUT_OF_RANGE,
                             TAKEN, State, X)
from tests.support import (GOLDEN_INPUT, ROOT, ScriptedIO, golden_transcript,
                           run_program)


def board_from(s, last_move=None):
    """Build a state from a 9-char string using X, O and '.' for empty,
    indexed left to right and top to bottom."""
    assert len(s) == 9
    return State(tuple(EMPTY if ch == "." else ch for ch in s), last_move)


def play(*numbers):
    """Return the state after Moves at the keypad ``numbers``, X first."""
    state = game.initial_state()
    for number in numbers:
        move, error = game.parse_move(str(number))
        state = game.apply_move(state, move)
    return state


def computer_move(state):
    """The Cell number the computer (full Difficulty) plays in ``state``."""
    return game.move_text(Computer().choose_move(game, state, None))


class ResultTests(unittest.TestCase):
    def test_rows(self):
        self.assertEqual(game.result(board_from("XXXOO....")), X)
        self.assertEqual(game.result(board_from("XX.OOOX..")), O)
        self.assertEqual(game.result(board_from("OO....XXX")), X)

    def test_columns(self):
        self.assertEqual(game.result(board_from("XO.XO.X..")), X)
        self.assertEqual(game.result(board_from("XO.XO..O.")), O)
        self.assertEqual(game.result(board_from("O.XO.X..X")), X)

    def test_diagonals(self):
        self.assertEqual(game.result(board_from("XO.OX...X")), X)
        self.assertEqual(game.result(board_from("XXO.O.O.X")), O)

    def test_draw(self):
        self.assertEqual(game.result(board_from("XOXXOOOXX")), DRAW)

    def test_ongoing(self):
        self.assertIsNone(game.result(game.initial_state()))
        self.assertIsNone(game.result(board_from("XO..X...O")))

    def test_no_moves_once_won(self):
        self.assertEqual(game.legal_moves(board_from("XXXOO....")), [])


class SideToMoveTests(unittest.TestCase):
    def test_x_moves_first_and_sides_alternate(self):
        self.assertEqual(game.sides, (X, O))
        self.assertEqual(game.to_move(game.initial_state()), X)
        self.assertEqual(game.to_move(play(5)), O)
        self.assertEqual(game.to_move(play(5, 7)), X)

    def test_a_move_places_the_mark_of_the_side_to_move(self):
        self.assertEqual(play(5, 7), board_from("O...X....", last_move=0))


class ComputerTests(unittest.TestCase):
    def test_takes_immediate_win(self):
        self.assertEqual(computer_move(board_from("XX.OO....")), "9")

    def test_prefers_win_over_block(self):
        self.assertEqual(computer_move(board_from("XX.OO.X..")), "6")

    def test_blocks_immediate_loss(self):
        self.assertEqual(computer_move(board_from("XX..O....")), "9")

    def test_blocks_column_threat(self):
        self.assertEqual(computer_move(board_from("O..OX...X")), "1")

    def test_full_difficulty_is_unlimited_and_unbeatable(self):
        self.assertIsNone(game.default_depth)
        self.assertTrue(game.unbeatable(None))


class CellNumberTests(unittest.TestCase):
    # Cells are numbered like a numeric keypad: 7 8 9 / 4 5 6 / 1 2 3.
    KEYPAD = {7: "X........", 8: ".X.......", 9: "..X......",
              4: "...X.....", 5: "....X....", 6: ".....X...",
              1: "......X..", 2: ".......X.", 3: "........X"}

    def test_keypad_order(self):
        for number, board in self.KEYPAD.items():
            self.assertEqual(play(number).cells, board_from(board).cells)
            move, _ = game.parse_move(str(number))
            self.assertEqual(game.move_text(move), str(number))

    def test_parsing_ignores_whitespace(self):
        self.assertEqual(game.parse_move(" 5 \n"), game.parse_move("5"))

    def test_out_of_range_is_left_to_the_game_and_reported_as_typed(self):
        for number in (-1, 0, 10):
            move, error = game.parse_move(str(number))
            self.assertIsNone(error)
            reason = game.move_problem(game.initial_state(), move)
            self.assertEqual(reason, OUT_OF_RANGE)
            self.assertEqual(game.rejection_message(move, reason),
                             "%d is out of range; choose a cell from 1 to 9."
                             % number)

    def test_taken_cell_reported_by_its_number(self):
        move, _ = game.parse_move("7")
        state = play(7)
        self.assertEqual(game.move_problem(state, move), TAKEN)
        self.assertEqual(game.rejection_message(move, TAKEN),
                         "Cell 7 is already taken; pick an empty cell.")

    def test_not_a_number(self):
        for text in ("", "abc", "1.5"):
            move, error = game.parse_move(text)
            self.assertIsNone(move, text)
            self.assertIn("1 to 9", error)


def cells(numbers):
    return [str(n) for n in numbers]


class GameTests(unittest.TestCase):
    def test_human_first_draw(self):
        scripted = ScriptedIO(cells([5, 8, 4, 3, 1]))
        players = (Human(), Computer())
        self.assertEqual(play_game(game, players, scripted), DRAW)
        self.assertEqual(scripted.events, [
            Started(players, game.initial_state()),
            Moved(X, 4, board_from("....X....", 4)),
            Moved(O, 0, board_from("O...X....", 0)),
            Moved(X, 1, board_from("OX..X....", 1)),
            Moved(O, 7, board_from("OX..X..O.", 7)),
            Moved(X, 3, board_from("OX.XX..O.", 3)),
            Moved(O, 5, board_from("OX.XXO.O.", 5)),
            Moved(X, 8, board_from("OX.XXO.OX", 8)),
            Moved(O, 2, board_from("OXOXXO.OX", 2)),
            Moved(X, 6, board_from("OXOXXOXOX", 6)),
            GameOver(DRAW, board_from("OXOXXOXOX", 6)),
        ])
        self.assertEqual(scripted.prompts, [X] * 5)

    def test_computer_first_win(self):
        scripted = ScriptedIO(cells([8, 9]))
        players = (Computer(), Human())
        self.assertEqual(play_game(game, players, scripted), X)
        self.assertEqual(scripted.events, [
            Started(players, game.initial_state()),
            Moved(X, 0, board_from("X........", 0)),
            Moved(O, 1, board_from("XO.......", 1)),
            Moved(X, 3, board_from("XO.X.....", 3)),
            Moved(O, 2, board_from("XOOX.....", 2)),
            Moved(X, 6, board_from("XOOX..X..", 6)),
            GameOver(X, board_from("XOOX..X..", 6)),
        ])

    def test_rejected_moves_and_bad_text_are_asked_again(self):
        scripted = ScriptedIO(["abc", "10", "0", "5", "5", "7", "8"])
        with self.assertRaises(EOFError):
            play_game(game, (Human(), Computer()), scripted)
        self.assertEqual(len(scripted.parse_errors), 1)
        self.assertEqual(scripted.events[1:7], [
            MoveRejected(9, OUT_OF_RANGE),
            MoveRejected(-1, OUT_OF_RANGE),
            Moved(X, 4, board_from("....X....", 4)),
            Moved(O, 0, board_from("O...X....", 0)),
            MoveRejected(4, TAKEN),
            MoveRejected(0, TAKEN),
        ])
        self.assertEqual(scripted.events[7],
                         Moved(X, 1, board_from("OX..X....", 1)))

    def test_quitting_propagates(self):
        scripted = ScriptedIO()
        with self.assertRaises(EOFError):
            play_game(game, (Human(), Computer()), scripted)
        self.assertEqual(scripted.of_type(Moved), [])

    def test_starts_from_a_given_state(self):
        scripted = ScriptedIO()
        start = board_from("XX.OO....")
        self.assertEqual(play_game(game, (Computer(), Human()), scripted,
                                   start=start), X)
        self.assertEqual(scripted.events[0].state, start)


class NeverLosesTests(unittest.TestCase):
    """Exhaustively try every human Move sequence against the computer."""

    def _explore(self, state, computer, counter):
        result = game.result(state)
        if result is not None:
            self.assertNotEqual(
                result, O if computer == X else X,
                "the computer (%s) lost on %r" % (computer, state))
            counter[result] = counter.get(result, 0) + 1
            return
        if game.to_move(state) == computer:
            move = Computer().choose_move(game, state, None)
            self.assertIn(move, game.legal_moves(state))
            self._explore(game.apply_move(state, move), computer, counter)
        else:
            for move in game.legal_moves(state):
                self._explore(game.apply_move(state, move), computer, counter)

    def test_computer_first_never_loses(self):
        counter = {}
        self._explore(game.initial_state(), X, counter)
        self.assertNotIn(O, counter)
        self.assertGreater(sum(counter.values()), 0)

    def test_computer_second_never_loses(self):
        counter = {}
        self._explore(game.initial_state(), O, counter)
        self.assertNotIn(X, counter)
        self.assertGreater(sum(counter.values()), 0)


def render(state):
    """Render the board; return its plain text and the styled glyphs as
    ``(line, glyph, Style)`` for every letter or digit."""
    console = Console(record=True, width=60, color_system="truecolor",
                      file=io.StringIO())
    glyphs = []
    line = 0
    for segment in console.render(game.render(state)):
        if segment.text == "\n":
            line += 1
            continue
        for ch in segment.text:
            if ch.isalnum():
                glyphs.append((line, ch, segment.style or Style()))
    console.print(game.render(state))
    return console.export_text(styles=False), glyphs


class RenderingTests(unittest.TestCase):
    def test_board_has_full_grid_lines(self):
        out, _ = render(board_from("O.X.X...."))
        for ch in "┏┳┓┣╋┫┗┻┛┃━":
            self.assertIn(ch, out, ch)
        lines = out.splitlines()
        # Horizontal separators run the full width with junctions.
        self.assertEqual(sum("╋" in line for line in lines), 2)
        self.assertEqual(lines[0].count("┳"), 2)

    def test_board_shows_marks_and_guide_numbers(self):
        _, glyphs = render(board_from("O.X.X...."))
        rows = {}
        for line, ch, _ in glyphs:
            rows.setdefault(line, []).append(ch)
        # Empty Cells show their keypad numbers.
        self.assertEqual(list(rows.values()),
                         [["O", "8", "X"], ["4", "X", "6"], ["1", "2", "3"]])

    def test_mark_and_guide_styles(self):
        _, glyphs = render(board_from("O.X.X...."))
        styles = {ch: style for _, ch, style in glyphs}
        self.assertEqual(styles["O"].color.name, "magenta")
        self.assertEqual(styles["X"].color.name, "cyan")
        self.assertTrue(styles["O"].bold and styles["X"].bold)
        self.assertTrue(styles["8"].dim)

    def test_most_recent_move_highlighted_whichever_side_made_it(self):
        for state, mark in ((play(5, 7), "O"), (play(5, 7, 9), "X")):
            _, glyphs = render(state)
            self.assertEqual([ch for _, ch, style in glyphs if style.reverse],
                             [mark])
        _, glyphs = render(game.initial_state())
        self.assertFalse(any(style.reverse for _, _, style in glyphs))

    def test_winning_line_on_green(self):
        _, glyphs = render(play(7, 4, 8, 5, 9))
        green = [ch for _, ch, style in glyphs
                 if style.bgcolor is not None
                 and style.bgcolor.name == "green"]
        self.assertEqual(green, ["X"] * 3)
        self.assertTrue(all(style.bold for _, ch, style in glyphs
                            if ch == "X"))
        self.assertFalse(any(style.reverse for _, _, style in glyphs))


class TerminalIOTests(unittest.TestCase):
    def _shown(self, *events):
        out = io.StringIO()
        terminal = framework.TerminalIO(game, Console(file=out,
                                                      color_system=None))
        for event in events:
            terminal.show(event)
        return out.getvalue()

    def test_rejected_move_uses_keypad_number(self):
        self.assertIn("Cell 7 is already taken",
                      self._shown(MoveRejected(0, TAKEN)))
        self.assertIn("10 is out of range",
                      self._shown(MoveRejected(9, OUT_OF_RANGE)))

    def test_a_human_win_is_impossible_only_at_full_difficulty(self):
        won = board_from("XXXOO....", 2)
        full = self._shown(Started((Human(), Computer()), game.initial_state()),
                           GameOver(X, won))
        self.assertIn("You win! (This should not happen...)", full)
        weaker = self._shown(Started((Human(), Computer(2)),
                                     game.initial_state()),
                             GameOver(X, won))
        self.assertIn("You win!", weaker)
        self.assertNotIn("should not happen", weaker)


class CommandLineTests(unittest.TestCase):
    """``python3 tictactoe.py``: the shortcut straight into tic-tac-toe."""

    def _run(self, *args, input=""):
        return run_program([os.path.join(ROOT, "tictactoe.py")], *args,
                           input=input)

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
        result = self._run(input=GOLDEN_INPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, golden_transcript())


if __name__ == "__main__":
    unittest.main()
