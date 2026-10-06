import io
import random
import time
import unittest

from rich.console import Console
from rich.style import Style

import games.gomoku as gomoku
from games import framework
from games.framework import (
    DRAW,
    Computer,
    GameOver,
    Human,
    Moved,
    MoveRejected,
    Started,
    matchup,
    play_game,
)
from games.gomoku import BLACK, OFF_BOARD, TAKEN, WHITE
from games.gomoku import GAME_TYPE as game
from tests.support import ScriptedIO, run_program


def point(text):
    """The Move for ``text`` such as "e5"."""
    move, error = game.parse_move(text)
    assert error is None, error
    return move


def play(*texts):
    """Return the state after placing stones on the Points ``texts`` (such
    as "e5") from the start, Black first."""
    state = game.initial_state()
    for text in texts:
        state = game.apply_move(state, point(text))
    return state


def alternate(black, white):
    """Interleave Black's and White's Points, Black first."""
    texts = []
    for i, text in enumerate(black):
        texts.append(text)
        if i < len(white):
            texts.append(white[i])
    return texts


# A full board without a Winning five (X: Black, O: White), from row 9 down.
DRAWN_BOARD = [
    "XXOOXXOOX",
    "OOXXOOXXO",
    "XXOOXXOOX",
    "OOXXOOXXO",
    "XXOOXXOOX",
    "OOXXOOXXO",
    "XXOOXXOOX",
    "OOXXOOXXO",
    "XXOOXXOOX",
]


def drawn_game():
    """The Points of a Game that fills the board without a Winning five."""
    stones = {"X": [], "O": []}
    for i, line in enumerate(DRAWN_BOARD):
        for col, ch in enumerate(line):
            stones[ch].append("%s%d" % ("abcdefghi"[col], 9 - i))
    return alternate(stones["X"], stones["O"])


class RulesTests(unittest.TestCase):
    def test_black_moves_first_and_sides_alternate(self):
        self.assertEqual(game.sides, (BLACK, WHITE))
        self.assertEqual(game.to_move(game.initial_state()), BLACK)
        self.assertEqual(game.to_move(play("e5")), WHITE)
        self.assertEqual(game.to_move(play("e5", "a1")), BLACK)

    def test_a_stone_goes_on_any_empty_point(self):
        state = play("a1", "i9", "e5")
        self.assertEqual(gomoku.stone_at(state, 0, 0), BLACK)
        self.assertEqual(gomoku.stone_at(state, 8, 8), WHITE)
        self.assertEqual(gomoku.stone_at(state, 4, 4), BLACK)
        self.assertIsNone(gomoku.stone_at(state, 4, 5))
        self.assertEqual(len(game.legal_moves(state)), 78)
        self.assertNotIn(point("e5"), game.legal_moves(state))

    def test_every_point_is_legal_at_the_start(self):
        self.assertEqual(len(game.legal_moves(game.initial_state())), 81)

    def test_game_in_progress_has_no_result(self):
        self.assertIsNone(game.result(game.initial_state()))
        # Four in a row is not enough.
        self.assertIsNone(
            game.result(play(*alternate(["a1", "b1", "c1", "d1"], ["a9", "b9", "c9"])))
        )

    def test_a_win_in_each_direction(self):
        lines = {
            "row": ["c4", "d4", "e4", "f4", "g4"],
            "column": ["e1", "e2", "e3", "e4", "e5"],
            "rising diagonal": ["a1", "b2", "c3", "d4", "e5"],
            "falling diagonal": ["i1", "h2", "g3", "f4", "e5"],
        }
        white = ["a9", "c9", "e9", "g9"]
        for direction, black in lines.items():
            with self.subTest(direction):
                state = play(*alternate(black, white))
                self.assertEqual(game.result(state), BLACK)
                self.assertEqual(game.legal_moves(state), [])

    def test_a_line_of_six_wins(self):
        black = ["a1", "b1", "d1", "e1", "f1", "c1"]
        state = play(*alternate(black, ["a9", "b9", "c9", "e9", "g9"]))
        self.assertEqual(game.result(state), BLACK)

    def test_white_can_win(self):
        black = ["a9", "c9", "e9", "g9", "i7"]
        state = play(*alternate(black, ["b2", "c3", "d4", "e5", "f6"]))
        self.assertEqual(game.result(state), WHITE)

    def test_full_board_without_five_is_a_draw(self):
        state = play(*drawn_game())
        self.assertEqual(game.legal_moves(state), [])
        self.assertEqual(game.result(state), DRAW)

    def test_off_board_and_taken_points_are_refused(self):
        state = play("e5")
        self.assertEqual(game.move_problem(state, point("j3")), OFF_BOARD)
        self.assertEqual(game.move_problem(state, point("a10")), OFF_BOARD)
        self.assertEqual(game.move_problem(state, point("a0")), OFF_BOARD)
        self.assertEqual(game.move_problem(state, point("e5")), TAKEN)
        self.assertIsNone(game.move_problem(state, point("e6")))
        with self.assertRaises(ValueError):
            game.apply_move(state, point("e5"))

    def test_heuristic_counts_windows_of_five(self):
        empty = game.initial_state()
        self.assertEqual(game.heuristic(empty, BLACK), 0)
        state = play("e5")
        self.assertGreater(game.heuristic(state, BLACK), 0)
        self.assertEqual(game.heuristic(state, WHITE), -game.heuristic(state, BLACK))
        # A four in an open row outweighs scattered stones.
        four = play(*alternate(["b5", "c5", "d5", "e5"], ["a9", "i9", "a1"]))
        self.assertGreater(game.heuristic(four, BLACK), 1000)
        self.assertLess(game.heuristic(four, BLACK), framework.WIN_SCORE / 2)

    def test_heuristic_stays_well_inside_the_win_score(self):
        # Even if every window of five held four stones of one Side.
        most = len(gomoku.WINDOWS) * max(gomoku.WINDOW_SCORES.values())
        self.assertLess(most, framework.WIN_SCORE / 4)
        # And on Games in progress reached by playing random Moves.
        rng = random.Random(3)
        for _ in range(20):
            state = game.initial_state()
            while game.result(state) is None:
                for side in game.sides:
                    self.assertLess(abs(game.heuristic(state, side)), most)
                state = game.apply_move(state, rng.choice(game.legal_moves(state)))
            # And on the finished board, which may hold a five.
            for side in game.sides:
                self.assertLess(abs(game.heuristic(state, side)), most)
        # A board holding a five (or longer) scores like one holding a four.
        five = play(
            *alternate(["a5", "b5", "c5", "d5", "e5"], ["a9", "i9", "a1", "i1"])
        )
        self.assertEqual(game.result(five), BLACK)
        self.assertGreater(game.heuristic(five, BLACK), 1000)
        self.assertLess(game.heuristic(five, BLACK), most)

    def test_computer_settings(self):
        self.assertEqual(game.default_depth, 3)
        self.assertFalse(game.unbeatable(game.default_depth))
        self.assertFalse(game.unbeatable(None))
        self.assertEqual(matchup(game, None), "you vs. the computer")


class SearchMovesTests(unittest.TestCase):
    def points(self, state):
        return [gomoku.point_text(p) for p in game.search_moves(state)]

    def test_only_the_centre_on_an_empty_board(self):
        self.assertEqual(self.points(game.initial_state()), ["e5"])

    def test_empty_points_next_to_a_stone_nearest_the_centre_first(self):
        self.assertEqual(
            self.points(play("e5")), ["e4", "d5", "f5", "e6", "d4", "f4", "d6", "f6"]
        )
        self.assertEqual(self.points(play("a1")), ["b2", "b1", "a2"])

    def test_taken_points_and_points_two_away_are_left_out(self):
        state = play("e5", "f5", "a1")
        moves = self.points(state)
        self.assertEqual(len(moves), 10 + 3)
        self.assertNotIn("e5", moves)
        self.assertNotIn("f5", moves)
        self.assertNotIn("c5", moves)
        self.assertIn("g6", moves)
        self.assertEqual(moves, self.points(state))
        self.assertLessEqual(
            set(game.search_moves(state)), set(game.legal_moves(state))
        )
        self.assertEqual(
            game.search_moves(state),
            [p for p in game.legal_moves(state) if p in game.search_moves(state)],
        )

    def test_none_once_the_game_has_a_result(self):
        state = play(
            *alternate(["c4", "d4", "e4", "f4", "g4"], ["a9", "c9", "e9", "g9"])
        )
        self.assertEqual(game.search_moves(state), [])


def hot_seat(texts):
    """Play a Game between two scripted humans, who type ``texts`` and then
    the first legal Point. Return the Player I/O and the Result."""
    scripted = ScriptedIO(texts, game_type=game)
    return scripted, play_game(game, (Human(), Human()), scripted)


class GameTests(unittest.TestCase):
    def test_two_humans_play_to_a_win(self):
        black = ["c4", "d4", "e4", "f4", "g4"]
        scripted, result = hot_seat(alternate(black, ["a9", "c9", "e9", "g9"]))
        self.assertEqual(result, BLACK)
        self.assertEqual(scripted.events[0], Started((Human(), Human()), play()))
        moved = scripted.of_type(Moved)
        self.assertEqual(len(moved), 9)
        self.assertEqual([m.side for m in moved[:3]], [BLACK, WHITE, BLACK])
        self.assertEqual(moved[0].move, point("c4"))
        self.assertEqual(scripted.events[-1], GameOver(BLACK, moved[-1].state))

    def test_off_board_and_taken_points_rejected_and_asked_again(self):
        scripted, _ = hot_seat(["e5", "e5", "j3", "a10", "a0", "d4"])
        self.assertEqual(
            scripted.of_type(MoveRejected),
            [
                MoveRejected(point("e5"), TAKEN),
                MoveRejected(point("j3"), OFF_BOARD),
                MoveRejected(point("a10"), OFF_BOARD),
                MoveRejected(point("a0"), OFF_BOARD),
            ],
        )
        moved = scripted.of_type(Moved)
        self.assertEqual((moved[1].side, moved[1].move), (WHITE, point("d4")))

    def test_unparseable_text_is_asked_again(self):
        scripted, _ = hot_seat(["xyz", "5e", "e", "e5"])
        self.assertEqual(
            scripted.parse_errors,
            [
                "Please enter a point such as e5 (got 'xyz').",
                "Please enter a point such as e5 (got '5e').",
                "Please enter a point such as e5 (got 'e').",
            ],
        )
        self.assertEqual(scripted.of_type(Moved)[0].move, point("e5"))

    def test_a_full_board_is_a_draw(self):
        scripted, result = hot_seat(drawn_game())
        self.assertEqual(result, DRAW)
        self.assertEqual(len(scripted.of_type(Moved)), 81)

    def test_quitting_propagates(self):
        with self.assertRaises(EOFError):
            play_game(game, (Human(), Human()), ScriptedIO())


def human_vs_computer(human_first, texts=(), start=None):
    """Play a Game with a scripted human, who types ``texts`` and then the
    first legal Point (centre first), against the computer at the default
    Difficulty. Return the Player I/O (with its events) and the Result."""
    scripted = ScriptedIO(texts, game_type=game)
    computer = Computer(game.default_depth)
    players = (Human(), computer) if human_first else (computer, Human())
    return scripted, play_game(game, players, scripted, start=start)


# A Game in progress after ten Moves each, Black to move: a crowded centre
# with many search Moves.
MID_GAME = play(
    *alternate(
        ["e5", "d4", "f6", "c3", "e3", "d6", "g5", "f4", "c5", "e7"],
        ["e4", "f5", "d5", "g7", "b2", "e6", "c6", "f3", "d3", "g4"],
    )
)


class ComputerTests(unittest.TestCase):
    def test_completes_a_five(self):
        # The computer, Black, has c5-f5 open at g5; White threatens too.
        start = play(*alternate(["c5", "d5", "e5", "f5"], ["b5", "c6", "d6", "e6"]))
        scripted, result = human_vs_computer(False, start=start)
        self.assertEqual(result, BLACK)
        (move,) = scripted.of_type(Moved)
        self.assertEqual((move.side, move.move), (BLACK, point("g5")))

    def test_blocks_a_four_with_one_open_end(self):
        # The human, Black, has b5-e5 with a5 taken by White: f5 wins next.
        start = play(*alternate(["b5", "c5", "d5", "e5"], ["a5", "h8", "h2"]))
        scripted, _ = human_vs_computer(True, start=start)
        first = scripted.of_type(Moved)[0]
        self.assertEqual((first.side, first.move), (WHITE, point("f5")))

    def test_computer_against_itself_ends_with_a_result(self):
        computer = Computer(game.default_depth)
        scripted = ScriptedIO()
        result = play_game(game, (computer, computer), scripted)
        self.assertIn(result, (BLACK, WHITE, DRAW))
        self.assertEqual(scripted.events[-1], GameOver(result, scripted.state))
        self.assertEqual(game.result(scripted.state), result)

    def test_a_mid_game_move_takes_about_a_second_or_less(self):
        self.assertEqual(game.to_move(MID_GAME), BLACK)
        self.assertIsNone(game.result(MID_GAME))
        started = time.perf_counter()
        Computer(game.default_depth).choose_move(game, MID_GAME, None)
        self.assertLess(time.perf_counter() - started, 1.5)


class ParseMoveTests(unittest.TestCase):
    def test_letter_then_number(self):
        self.assertEqual(game.parse_move("e5"), ((4, 4), None))
        self.assertEqual(game.parse_move("a1"), ((0, 0), None))
        self.assertEqual(game.parse_move("i9"), ((8, 8), None))

    def test_case_and_spaces_do_not_matter(self):
        for text in ("E5", "e 5", " e5 ", "E 5"):
            with self.subTest(text):
                self.assertEqual(game.parse_move(text), ((4, 4), None))

    def test_the_board_is_left_to_the_game(self):
        self.assertEqual(game.parse_move("j3"), ((9, 2), None))
        self.assertEqual(game.parse_move("a10"), ((0, 9), None))
        self.assertEqual(game.parse_move("a0"), ((0, -1), None))

    def test_other_shapes_are_refused(self):
        for text in ("abc", "", "5", "e", "5e", "e5x", "ee5", "e-1", "e 5 5"):
            with self.subTest(text):
                move, error = game.parse_move(text)
                self.assertIsNone(move)
                self.assertEqual(
                    error, "Please enter a point such as e5 (got %r)." % text.strip()
                )

    def test_move_text_and_description(self):
        self.assertEqual(game.move_text((4, 4)), "e5")
        self.assertEqual(game.move_text((9, 2)), "j3")
        self.assertEqual(game.describe_move((4, 4)), "point [bold]e5[/]")

    def test_rejection_messages(self):
        self.assertEqual(
            game.rejection_message(point("j3"), OFF_BOARD),
            "j3 is off the board; columns are a-i and rows 1-9.",
        )
        self.assertEqual(
            game.rejection_message(point("e5"), TAKEN),
            "e5 is taken; pick an empty point.",
        )


def render(state):
    """Render the board; return its plain text lines and the styled glyphs
    as ``(line, column, glyph, Style)`` for every glyph that is not a
    space or a grid line."""
    console = Console(
        record=True, width=80, color_system="truecolor", file=io.StringIO()
    )
    glyphs = []
    line = column = 0
    for segment in console.render(game.render(state)):
        if segment.text == "\n":
            line += 1
            column = 0
            continue
        for ch in segment.text:
            if ch.isalnum() or ch in "●○":
                glyphs.append((line, column, ch, segment.style or Style()))
            column += 1
    console.print(game.render(state))
    return console.export_text(styles=False).splitlines(), glyphs


class RenderingTests(unittest.TestCase):
    def test_heavy_grid_with_labels_on_every_edge(self):
        lines, glyphs = render(game.initial_state())
        text = "\n".join(lines)
        for ch in "┏┳┓┣╋┫┗┻┛┃━":
            self.assertIn(ch, text, ch)
        # 9 rows: 8 separators between them.
        self.assertEqual(sum("╋" in line for line in lines), 8)
        letters = "abcdefghi"
        top = [g for g in glyphs if g[0] == glyphs[0][0]]
        bottom = [g for g in glyphs if g[0] == glyphs[-1][0]]
        self.assertEqual("".join(g[2] for g in top), letters)
        self.assertEqual("".join(g[2] for g in bottom), letters)
        numbers = [g for g in glyphs if g[2].isdigit()]
        # Each row number on both sides, 9 at the top.
        self.assertEqual(
            "".join(g[2] for g in numbers), "".join(d * 2 for d in "987654321")
        )
        self.assertTrue(all(style.bold for *_, style in top + bottom + numbers))

    def test_labels_line_up_with_the_points(self):
        lines, glyphs = render(play("a1", "i9"))
        stones = [g for g in glyphs if g[2] in "●○"]
        (white_line, white_col, _, _), (black_line, black_col, _, _) = stones
        top = [g for g in glyphs if g[0] == glyphs[0][0]]
        # The stone on a1 is under the letter a and beside the number 1.
        self.assertEqual(black_col, top[0][1])
        self.assertEqual(white_col, top[-1][1])
        ones = [g for g in glyphs if g[2] == "1"]
        nines = [g for g in glyphs if g[2] == "9"]
        self.assertEqual({g[0] for g in ones}, {black_line})
        self.assertEqual({g[0] for g in nines}, {white_line})
        self.assertLess(ones[0][1], black_col)
        self.assertGreater(ones[1][1], black_col)

    def test_stones_in_their_glyphs_and_styles(self):
        _, glyphs = render(play("e5", "e6", "a1"))
        stones = {(g[0], g[1]): (g[2], g[3]) for g in glyphs if g[2] in "●○"}
        self.assertEqual(sorted(ch for ch, _ in stones.values()), ["○", "●", "●"])
        for ch, style in stones.values():
            self.assertTrue(style.bold)
            if ch == "○":
                self.assertEqual(style.color.name, "bright_white")
            else:
                self.assertIsNone(style.color)

    def test_most_recent_move_highlighted(self):
        _, glyphs = render(play("e5", "e6", "a1"))
        reversed_stones = [(g[2], g[0]) for g in glyphs if g[3].reverse]
        self.assertEqual(len(reversed_stones), 1)
        self.assertEqual(reversed_stones[0][0], "●")
        # a1 is the lowest stone drawn.
        lowest = max(g[0] for g in glyphs if g[2] in "●○")
        self.assertEqual(reversed_stones[0][1], lowest)

    def test_winning_five_on_green(self):
        black = ["a1", "b1", "d1", "e1", "f1", "c1"]
        _, glyphs = render(play(*alternate(black, ["a9", "b9", "c9", "e9", "g9"])))

        def green(style):
            return style.bgcolor is not None and style.bgcolor.name == "green"

        self.assertEqual([g[2] for g in glyphs if green(g[3])], ["●"] * 6)
        others = [g[2] for g in glyphs if g[2] in "●○" and not green(g[3])]
        self.assertEqual(others, ["○"] * 5)


class TerminalIOTests(unittest.TestCase):
    def test_rejected_moves_name_the_point(self):
        out = io.StringIO()
        terminal = framework.TerminalIO(game, Console(file=out, color_system=None))
        terminal.show(MoveRejected(point("e5"), TAKEN))
        terminal.show(MoveRejected(point("j3"), OFF_BOARD))
        self.assertIn("e5 is taken; pick an empty point.", out.getvalue())
        self.assertIn("j3 is off the board", out.getvalue())


def gomoku_program(*args, input=""):
    return run_program(["-m", "games"], "--game", "gomoku", *args, input=input)


class CommandLineTests(unittest.TestCase):
    def test_hot_seat_game(self):
        texts = alternate(["c4", "d4", "e4", "f4", "g4"], ["a9", "c9", "e9", "g9"])
        result = gomoku_program(
            "--first",
            "human",
            "--second",
            "human",
            input="xyz\nj3\n" + "\n".join(texts) + "\nn\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("Gomoku", out)
        self.assertIn("Black: human, White: human. Black moves first.", out)
        self.assertIn("Black: Your move (e.g. e5):", out)
        self.assertIn("Please enter a point such as e5 (got 'xyz').", out)
        self.assertIn("j3 is off the board; columns are a-i and rows 1-9.", out)
        self.assertIn("Black wins!", out)
        self.assertTrue(out.rstrip().endswith("Goodbye!"))

    def test_help_mentions_gomoku(self):
        result = run_program(["-m", "games"], "--help")
        self.assertEqual(result.returncode, 0)
        text = " ".join(result.stdout.split())
        self.assertIn("gomoku", text)
        self.assertIn("Gomoku on a 9x9 board", text)


if __name__ == "__main__":
    unittest.main()
