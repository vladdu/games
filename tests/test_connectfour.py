import io
import unittest

from rich.console import Console
from rich.style import Style

import games.connectfour as c4
from games.connectfour import (RED, YELLOW, DRAW, OUT_OF_RANGE, FULL,
                               Started, Moved, MoveRejected, GameOver)


def play(*columns):
    """Return the state after dropping discs in ``columns`` (1-7, as typed)
    from the start, Red first."""
    state = c4.new_state()
    for column in columns:
        state = c4.apply_move(state, column - 1)
    return state


class RulesTests(unittest.TestCase):
    def test_red_moves_first_and_sides_alternate(self):
        self.assertEqual(c4.to_move(c4.new_state()), RED)
        self.assertEqual(c4.to_move(play(4)), YELLOW)
        self.assertEqual(c4.to_move(play(4, 4)), RED)

    def test_discs_fall_to_the_lowest_empty_row(self):
        state = play(4, 4, 3)
        self.assertEqual(c4.disc_at(state, 3, 0), RED)
        self.assertEqual(c4.disc_at(state, 3, 1), YELLOW)
        self.assertEqual(c4.disc_at(state, 2, 0), RED)
        self.assertIsNone(c4.disc_at(state, 2, 1))

    def test_game_in_progress_has_no_result(self):
        self.assertIsNone(c4.result(c4.new_state()))
        self.assertIsNone(c4.result(play(1, 1, 2, 2, 3, 3)))

    def test_horizontal_win(self):
        self.assertEqual(c4.result(play(1, 1, 2, 2, 3, 3, 4)), RED)

    def test_vertical_win(self):
        self.assertEqual(c4.result(play(1, 2, 1, 2, 1, 2, 3, 2)), YELLOW)

    def test_diagonal_wins(self):
        # Rising: Red at (1,0) (2,1) (3,2) (4,3).
        self.assertEqual(c4.result(play(1, 2, 2, 3, 3, 4, 3, 4, 4, 7, 4)),
                         RED)
        # Falling: Red at (7,0) (6,1) (5,2) (4,3).
        self.assertEqual(c4.result(play(7, 6, 6, 5, 5, 4, 5, 4, 4, 1, 4)),
                         RED)

    def test_full_board_without_four_is_a_draw(self):
        # A drawn Game found by random playouts.
        moves = [int(ch) for ch in
                 "547125662261271266215743771576315353334444"]
        state = play(*moves)
        self.assertEqual(c4.legal_moves(state), [])
        self.assertEqual(c4.result(state), DRAW)


class ScriptedIO:
    """Player I/O for a scripted human: plays ``moves`` (column indices,
    legal or not) in order, then the leftmost column with room."""

    def __init__(self, first, moves=()):
        self.first = first
        self.moves = list(moves)
        self.events = []

    def wants_first(self):
        return self.first

    def choose_move(self, state):
        if self.moves:
            return self.moves.pop(0)
        return c4.legal_moves(state)[0]

    def show(self, event):
        self.events.append(event)

    def of_type(self, kind):
        return [e for e in self.events if isinstance(e, kind)]


class GameTests(unittest.TestCase):
    def test_human_first_plays_red_to_a_result(self):
        io = ScriptedIO(first=True, moves=[3])
        result = c4.play_game(io)
        self.assertEqual(io.events[0], Started(RED, YELLOW))
        moved = io.of_type(Moved)
        self.assertEqual((moved[0].side, moved[0].column), (RED, 3))
        self.assertEqual([m.side for m in moved[:4]],
                         [RED, YELLOW, RED, YELLOW])
        over = io.events[-1]
        self.assertIsInstance(over, GameOver)
        self.assertEqual(over.result, result)
        self.assertEqual(over.state, moved[-1].state)
        self.assertEqual(c4.result(over.state), result)

    def test_computer_first_plays_red(self):
        io = ScriptedIO(first=False)
        c4.play_game(io)
        self.assertEqual(io.events[0], Started(YELLOW, RED))
        self.assertEqual(io.of_type(Moved)[0].side, RED)

    def test_out_of_range_column_rejected_and_asked_again(self):
        io = ScriptedIO(first=True, moves=[7, -1, 0])
        c4.play_game(io)
        self.assertEqual(io.events[1:3], [MoveRejected(7, OUT_OF_RANGE),
                                          MoveRejected(-1, OUT_OF_RANGE)])
        self.assertEqual(io.events[3].column, 0)

    def test_full_column_rejected_and_asked_again(self):
        io = ScriptedIO(first=True, moves=[0, 0, 1])
        c4.play_game(io, start=play(1, 1, 1, 1, 1, 1))
        self.assertEqual(io.events[1:3], [MoveRejected(0, FULL),
                                          MoveRejected(0, FULL)])
        self.assertEqual((io.events[3].side, io.events[3].column), (RED, 1))

    def test_quitting_propagates(self):
        class QuittingIO(ScriptedIO):
            def choose_move(self, state):
                raise EOFError
        with self.assertRaises(EOFError):
            c4.play_game(QuittingIO(first=True))


class ComputerTacticsTests(unittest.TestCase):
    def test_takes_a_win_in_one_move(self):
        # Yellow (computer) has columns 1-3 on the bottom row. The human,
        # Red, makes a vertical three in column 7 that Yellow could block,
        # but Yellow wins in column 4 instead.
        io = ScriptedIO(first=True, moves=[6])
        result = c4.play_game(io, start=play(7, 1, 7, 2, 6, 3))
        self.assertEqual(result, YELLOW)
        last = io.of_type(Moved)[-1]
        self.assertEqual((last.side, last.column), (YELLOW, 3))

    def test_blocks_the_opponents_win_in_one_move(self):
        # Yellow (the human) has three in column 7; Red (computer) to move.
        io = ScriptedIO(first=False)
        c4.play_game(io, start=play(1, 7, 2, 7, 1, 7))
        first = io.of_type(Moved)[0]
        self.assertEqual((first.side, first.column), (RED, 6))

    def test_blocks_a_horizontal_threat(self):
        # The human, Red, completes columns 2-4 on the bottom row; column 5
        # is Yellow's, so the computer must block in column 1.
        io = ScriptedIO(first=True, moves=[3])
        c4.play_game(io, start=play(2, 5, 3, 5))
        reply = io.of_type(Moved)[1]
        self.assertEqual((reply.side, reply.column), (YELLOW, 0))

    def test_a_move_takes_about_a_second_or_less(self):
        import time
        state = c4.new_state()
        started = time.perf_counter()
        c4.best_move(state)
        self.assertLess(time.perf_counter() - started, 1.0)


class ParseMoveTests(unittest.TestCase):
    def test_column_numbers_are_one_based(self):
        self.assertEqual(c4.parse_move("1"), (0, None))
        self.assertEqual(c4.parse_move(" 7 "), (6, None))

    def test_range_is_left_to_the_game(self):
        self.assertEqual(c4.parse_move("8"), (7, None))
        self.assertEqual(c4.parse_move("0"), (-1, None))

    def test_not_a_number(self):
        column, error = c4.parse_move("abc")
        self.assertIsNone(column)
        self.assertIn("1 to 7", error)

    def test_every_legal_move_parses_back(self):
        for column in c4.legal_moves(c4.new_state()):
            self.assertEqual(c4.parse_move(str(column + 1)), (column, None))


def render(state):
    """Render the board; return its plain text and the styled glyphs as
    ``(row of text, glyph, Style)`` for every non-space, non-line glyph."""
    console = Console(record=True, width=80, color_system="truecolor",
                      file=io.StringIO())
    glyphs = []
    line = 0
    for segment in console.render(c4.board_table(state)):
        if segment.text == "\n":
            line += 1
            continue
        for ch in segment.text:
            if ch.isalnum():
                glyphs.append((line, ch, segment.style or Style()))
    console.print(c4.board_table(state))
    return console.export_text(styles=False), glyphs


class RenderingTests(unittest.TestCase):
    def test_heavy_grid_with_column_header(self):
        text, glyphs = render(c4.new_state())
        for ch in "┏┳┓┣╋┫┗┻┛┃━":
            self.assertIn(ch, text, ch)
        header = [g for g in glyphs if g[0] == glyphs[0][0]]
        self.assertEqual("".join(ch for _, ch, _ in header), "1234567")
        self.assertTrue(all(style.bold for _, _, style in header))
        lines = text.splitlines()
        # One separator under the header and between each of the 6 rows.
        self.assertEqual(sum("╋" in line for line in lines), 6)
        self.assertEqual(lines[0].count("┳"), 6)

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
        reversed_discs = [(ch, style.color.name)
                          for _, ch, style in glyphs if style.reverse]
        self.assertEqual(reversed_discs, [("R", "red")])
        # It is the disc in column 7, the last one drawn on the bottom row.
        self.assertTrue(glyphs[-1][2].reverse)

    def test_winning_four_on_green(self):
        _, glyphs = render(play(1, 1, 2, 2, 3, 3, 4))
        green = [ch for _, ch, style in glyphs
                 if style.bgcolor is not None
                 and style.bgcolor.name == "green"]
        self.assertEqual(green, ["R"] * 4)
        others = [ch for _, ch, style in glyphs
                  if ch in "RY" and (style.bgcolor is None
                                     or style.bgcolor.name != "green")]
        self.assertEqual(others, ["Y"] * 3)
