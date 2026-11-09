import io
import unittest

from rich.console import Console
from rich.style import Style

import games.connectfour as c4
from games import framework
from games.connectfour import FULL, OUT_OF_RANGE, RED, YELLOW
from games.connectfour import GAME_TYPE as game
from games.framework import (
    DRAW,
    Computer,
    GameOver,
    Human,
    Moved,
    MoveRejected,
    Started,
    play_game,
)
from tests.support import GOLDEN_INPUT, ScriptedIO, golden_transcript, run_program


def play(*columns):
    """Return the state after dropping discs in ``columns`` (1-7, as typed)
    from the start, Red first."""
    state = game.initial_state()
    for column in columns:
        state = game.apply_move(state, column - 1)
    return state


class RulesTests(unittest.TestCase):
    def test_red_moves_first_and_sides_alternate(self):
        self.assertEqual(game.to_move(game.initial_state()), RED)
        self.assertEqual(game.to_move(play(4)), YELLOW)
        self.assertEqual(game.to_move(play(4, 4)), RED)

    def test_discs_fall_to_the_lowest_empty_row(self):
        state = play(4, 4, 3)
        self.assertEqual(c4.GRID.piece(state.cells, (3, 0)), RED)
        self.assertEqual(c4.GRID.piece(state.cells, (3, 1)), YELLOW)
        self.assertEqual(c4.GRID.piece(state.cells, (2, 0)), RED)
        self.assertIsNone(c4.GRID.piece(state.cells, (2, 1)))
        self.assertEqual(state.last_move, (2, 0))

    def test_game_in_progress_has_no_result(self):
        self.assertIsNone(game.result(game.initial_state()))
        self.assertIsNone(game.result(play(1, 1, 2, 2, 3, 3)))

    def test_horizontal_win(self):
        self.assertEqual(game.result(play(1, 1, 2, 2, 3, 3, 4)), RED)

    def test_vertical_win(self):
        self.assertEqual(game.result(play(1, 2, 1, 2, 1, 2, 3, 2)), YELLOW)

    def test_diagonal_wins(self):
        # Rising: Red at (1,0) (2,1) (3,2) (4,3).
        self.assertEqual(game.result(play(1, 2, 2, 3, 3, 4, 3, 4, 4, 7, 4)), RED)
        # Falling: Red at (7,0) (6,1) (5,2) (4,3).
        self.assertEqual(game.result(play(7, 6, 6, 5, 5, 4, 5, 4, 4, 1, 4)), RED)

    def test_full_board_without_four_is_a_draw(self):
        # A drawn Game found by random playouts.
        moves = [int(ch) for ch in "547125662261271266215743771576315353334444"]
        state = play(*moves)
        self.assertEqual(game.legal_moves(state), [])
        self.assertEqual(game.result(state), DRAW)


def human_vs_computer(human_first, texts=(), start=None):
    """Play a Game with a scripted human, who types ``texts`` and then the
    first legal column (centre first), against the computer at the default
    Difficulty. Return the Player I/O (with its events) and the Result."""
    scripted = ScriptedIO(texts, game_type=game)
    players = (
        (Human(), Computer(game.default_depth))
        if human_first
        else (Computer(game.default_depth), Human())
    )
    return scripted, play_game(game, players, scripted, start=start)


class GameTests(unittest.TestCase):
    def test_human_first_plays_red_to_a_result(self):
        scripted, result = human_vs_computer(True, ["4"])
        self.assertEqual(
            scripted.events[0], Started((Human(), Computer(6)), game.initial_state())
        )
        moved = scripted.of_type(Moved)
        self.assertEqual((moved[0].side, moved[0].move), (RED, 3))
        self.assertEqual([m.side for m in moved[:4]], [RED, YELLOW, RED, YELLOW])
        over = scripted.events[-1]
        self.assertIsInstance(over, GameOver)
        self.assertEqual(over.result, result)
        self.assertEqual(over.state, moved[-1].state)
        self.assertEqual(game.result(over.state), result)

    def test_computer_first_plays_red(self):
        scripted, _ = human_vs_computer(False)
        self.assertEqual(scripted.of_type(Moved)[0].side, RED)
        self.assertEqual(set(scripted.prompts), {YELLOW})

    def test_out_of_range_column_rejected_and_asked_again(self):
        scripted, _ = human_vs_computer(True, ["8", "0", "x", "1"])
        self.assertEqual(
            scripted.events[1:3],
            [MoveRejected(7, OUT_OF_RANGE), MoveRejected(-1, OUT_OF_RANGE)],
        )
        self.assertEqual(len(scripted.parse_errors), 1)
        self.assertEqual(scripted.events[3].move, 0)

    def test_full_column_rejected_and_asked_again(self):
        scripted, _ = human_vs_computer(
            True, ["1", "1", "2"], start=play(1, 1, 1, 1, 1, 1)
        )
        self.assertEqual(
            scripted.events[1:3], [MoveRejected(0, FULL), MoveRejected(0, FULL)]
        )
        self.assertEqual((scripted.events[3].side, scripted.events[3].move), (RED, 1))

    def test_quitting_propagates(self):
        with self.assertRaises(EOFError):
            play_game(game, (Human(), Computer()), ScriptedIO())


class ComputerTacticsTests(unittest.TestCase):
    def test_takes_a_win_in_one_move(self):
        # Yellow (computer) has columns 1-3 on the bottom row. The human,
        # Red, makes a vertical three in column 7 that Yellow could block,
        # but Yellow wins in column 4 instead.
        scripted, result = human_vs_computer(True, ["7"], start=play(7, 1, 7, 2, 6, 3))
        self.assertEqual(result, YELLOW)
        last = scripted.of_type(Moved)[-1]
        self.assertEqual((last.side, last.move), (YELLOW, 3))

    def test_blocks_the_opponents_win_in_one_move(self):
        # Yellow (the human) has three in column 7; Red (computer) to move.
        scripted, _ = human_vs_computer(False, start=play(1, 7, 2, 7, 1, 7))
        first = scripted.of_type(Moved)[0]
        self.assertEqual((first.side, first.move), (RED, 6))

    def test_blocks_a_horizontal_threat(self):
        # The human, Red, completes columns 2-4 on the bottom row; column 5
        # is Yellow's, so the computer must block in column 1.
        scripted, _ = human_vs_computer(True, ["4"], start=play(2, 5, 3, 5))
        reply = scripted.of_type(Moved)[1]
        self.assertEqual((reply.side, reply.move), (YELLOW, 0))

    def test_a_move_takes_about_a_second_or_less(self):
        import time

        state = game.initial_state()
        started = time.perf_counter()
        Computer(game.default_depth).choose_move(game, state, None)
        self.assertLess(time.perf_counter() - started, 1.0)


class ParseMoveTests(unittest.TestCase):
    def test_column_numbers_are_one_based(self):
        self.assertEqual(game.parse_move("1"), (0, None))
        self.assertEqual(game.parse_move(" 7 "), (6, None))

    def test_range_is_left_to_the_game(self):
        self.assertEqual(game.parse_move("8"), (7, None))
        self.assertEqual(game.parse_move("0"), (-1, None))

    def test_not_a_number(self):
        column, error = game.parse_move("abc")
        self.assertIsNone(column)
        self.assertIn("1 to 7", error)


def render(state):
    """Render the board; return its plain text and the styled glyphs as
    ``(row of text, glyph, Style)`` for every non-space, non-line glyph."""
    console = Console(
        record=True, width=80, color_system="truecolor", file=io.StringIO()
    )
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
    def test_thin_grid_with_column_header(self):
        text, glyphs = render(game.initial_state())
        for ch in "┌┬┐├┼┤└┴┘│─":
            self.assertIn(ch, text, ch)
        header = [g for g in glyphs if g[0] == glyphs[0][0]]
        self.assertEqual("".join(ch for _, ch, _ in header), "1234567")
        self.assertTrue(all(style.bold for _, _, style in header))
        lines = text.splitlines()
        # One separator under the header and between each of the 6 rows.
        self.assertEqual(sum("┼" in line for line in lines), 6)
        self.assertEqual(lines[0].count("┬"), 6)

    def test_discs_drawn_from_the_bottom_in_distinct_colors(self):
        _, glyphs = render(play(1, 1, 7))
        discs = [g for g in glyphs if g[1] in "RY"]
        self.assertEqual([ch for _, ch, _ in discs], ["Y", "R", "R"])
        (y_line, _, yellow), (r_line, _, red), _ = discs
        self.assertLess(y_line, r_line)  # Yellow is on top of Red.
        self.assertEqual(yellow.color.name, "yellow")
        self.assertEqual(red.color.name, "red")
        self.assertTrue(red.bold and yellow.bold)

    def test_most_recent_move_highlighted(self):
        _, glyphs = render(play(1, 1, 7))
        reversed_discs = [
            (ch, style.color.name) for _, ch, style in glyphs if style.reverse
        ]
        self.assertEqual(reversed_discs, [("R", "red")])
        # It is the disc in column 7, the last one drawn on the bottom row.
        self.assertTrue(glyphs[-1][2].reverse)

    def test_winning_four_on_green(self):
        _, glyphs = render(play(1, 1, 2, 2, 3, 3, 4))
        green = [
            ch
            for _, ch, style in glyphs
            if style.bgcolor is not None and style.bgcolor.name == "green"
        ]
        self.assertEqual(green, ["R"] * 4)
        others = [
            ch
            for _, ch, style in glyphs
            if ch in "RY" and (style.bgcolor is None or style.bgcolor.name != "green")
        ]
        self.assertEqual(others, ["Y"] * 3)

    def test_a_line_of_five_is_all_on_green(self):
        # Red's fifth disc, in column 3, joins 1-2 and 4-5 on the bottom row.
        _, glyphs = render(play(1, 1, 2, 2, 4, 4, 5, 5, 3))
        green = [
            ch
            for _, ch, style in glyphs
            if style.bgcolor is not None and style.bgcolor.name == "green"
        ]
        self.assertEqual(green, ["R"] * 5)


class TerminalIOTests(unittest.TestCase):
    def _shown(self, *events):
        out = io.StringIO()
        terminal = framework.TerminalIO(game, Console(file=out, color_system=None))
        for event in events:
            terminal.show(event)
        return out.getvalue()

    def test_rejected_moves_use_the_typed_column_number(self):
        self.assertIn("Column 1 is full", self._shown(MoveRejected(0, FULL)))
        self.assertIn(
            "8 is out of range; choose a column from 1 to 7",
            self._shown(MoveRejected(7, OUT_OF_RANGE)),
        )

    def test_end_messages_address_the_human(self):
        state = game.initial_state()
        started = Started((Human(), Computer(6)), state)
        self.assertIn("You win!", self._shown(started, GameOver(RED, state)))
        self.assertNotIn(
            "should not happen", self._shown(started, GameOver(RED, state))
        )
        self.assertIn(
            "The computer wins!", self._shown(started, GameOver(YELLOW, state))
        )
        self.assertIn("It's a draw!", self._shown(started, GameOver(DRAW, state)))


def connect_four(*args, input=""):
    return run_program(["-m", "games"], "--game", "connect-four", *args, input=input)


class CommandLineTests(unittest.TestCase):
    def test_plays_connect_four_against_the_computer(self):
        result = connect_four(input="y\nabc\n9\n4\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("Connect Four", out)
        self.assertIn("Do you want to go first? (y/n):", out)
        self.assertIn("You are Red, the computer is Yellow. Red moves first.", out)
        self.assertIn("│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │", out)
        self.assertIn("Your move (1-7):", out)
        self.assertIn("Please enter a column number from 1 to 7 (got 'abc').", out)
        self.assertIn("9 is out of range; choose a column from 1 to 7.", out)
        self.assertRegex(out, r"Computer \(Yellow\) plays column [1-7]\.")
        self.assertTrue(out.rstrip().endswith("Goodbye!"))

    def test_plays_a_whole_game_and_asks_to_play_again(self):
        # The human goes second and cycles through the columns (full ones
        # are rejected) until the Game ends; extra lines are refused by the
        # play-again prompt, and the last one answers it.
        result = connect_four(input="n\n" + "1\n2\n3\n4\n5\n6\n7\n" * 7 + "n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("You are Yellow, the computer is Red.", out)
        self.assertRegex(
            out,
            r"(You win!|The computer wins!|It's a draw!)"
            r"\n\nPlay again\? \(y/n\):",
        )
        self.assertTrue(out.rstrip().endswith("Goodbye!"))

    def test_tictactoe_by_name_plays_like_the_golden_transcript(self):
        result = run_program(["-m", "games"], "--game", "tictactoe", input=GOLDEN_INPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, golden_transcript())

    def test_unknown_game_type_lists_the_valid_names(self):
        result = run_program(["-m", "games"], "--game", "chess")
        self.assertEqual(result.returncode, 2)
        self.assertIn("chess", result.stderr)
        self.assertIn("tictactoe", result.stderr)
        self.assertIn("connect-four", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_help_mentions_connect_four_and_game(self):
        result = run_program(["-m", "games"], "--help")
        self.assertEqual(result.returncode, 0)
        text = " ".join(result.stdout.split())
        self.assertIn("--game", text)
        self.assertIn("Connect Four", text)
        self.assertIn("connect-four", text)
        self.assertNotIn("Goodbye", result.stdout)
