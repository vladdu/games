"""Gomoku, the third Game type: Black and White alternate Moves, placing
stones on any empty Point of a 9x9 board; five or more in a row wins
(freestyle, with no opening rules).

State representation: an immutable ``State`` holding the 81 Points row by
row from the bottom left (``"Black"``, ``"White"`` or None), and the Point
of the most recent Move (or None at the start). A Move is a Point
``(column, row)``, both 0-8 on the board; the human types it as a column
letter a-i and a row number 1-9, such as e5. Black always moves first.
"""

import re
from dataclasses import dataclass

from rich import box
from rich.table import Table
from rich.text import Text

from games.framework import DRAW
from games.grid import Grid

SIZE = 9
BLACK = "Black"
WHITE = "White"
LETTERS = "abcdefghi"
GRID = Grid(SIZE, SIZE, 5)


@dataclass(frozen=True)
class State:
    """A Gomoku position: ``points`` holds the stone on every Point, row by
    row from the bottom left, and ``last_move`` is the Point of the most
    recent Move."""

    points: tuple = (None,) * (SIZE * SIZE)
    last_move: tuple | None = None


def on_board(column, row):
    return 0 <= column < SIZE and 0 <= row < SIZE


# Legal Moves and search Moves are listed nearest to the centre first:
# among equally good Moves the computer's search plays the first.
POINT_ORDER = tuple(
    sorted(
        ((column, row) for row in range(SIZE) for column in range(SIZE)),
        key=lambda p: ((p[0] - 4) ** 2 + (p[1] - 4) ** 2, p[1], p[0]),
    )
)

CENTRE = (4, 4)

# The Points within distance 1 of each Point (counting diagonals), for the
# search Moves.
NEIGHBOURS = {
    (column, row): tuple(
        (column + dc, row + dr)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        if (dc or dr) and on_board(column + dc, row + dr)
    )
    for column in range(SIZE)
    for row in range(SIZE)
}

# Why a Move is rejected (see Gomoku.move_problem).
OFF_BOARD = "off the board"
TAKEN = "taken"

# Default Difficulty: the deepest search keeping a mid-game computer Move
# under about a second (depth 4 takes several seconds by the tenth Move).
DEFAULT_DEPTH = 3
# Score of a window of five holding n stones of one Side and none of the
# other, for the heuristic of the shared search. A won window (five) scores
# like a four, keeping the heuristic total and well inside the Win score.
WINDOW_SCORES = {1: 1, 2: 10, 3: 100, 4: 1000, 5: 1000}


def point_text(move):
    """The text a human types for the Point ``move``, such as "e5"."""
    column, row = move
    return "%s%d" % (chr(ord("a") + column), row + 1)


# --------------------------------------------------------------------------
# Rich rendering (pure: builds renderables, does no I/O)
# --------------------------------------------------------------------------

SIDE_STYLES = {BLACK: "bold", WHITE: "bold bright_white"}
STONE_GLYPHS = {BLACK: "●", WHITE: "○"}
LABEL_STYLE = "bold"
LAST_MOVE_STYLE = "reverse"
WIN_STYLE = "on green"


def _stone_text(state, column, row, win):
    stone = GRID.piece(state.points, (column, row))
    if stone is None:
        return Text(" ")
    text = Text(STONE_GLYPHS[stone], style=SIDE_STYLES[stone])
    if (column, row) in win:
        text.stylize(WIN_STYLE)
    elif (column, row) == state.last_move:
        text.stylize(LAST_MOVE_STYLE)
    return text


def board_table(state):
    """Return a rich Table drawing the board as a thin-lined 9x9 grid."""
    table = Table(
        box=box.SQUARE,
        show_header=False,
        show_lines=True,
        padding=(0, 1),
        pad_edge=True,
    )
    for _ in range(SIZE):
        table.add_column(justify="center", min_width=1)
    win = GRID.line(state.points, state.last_move) or ()
    for row in reversed(range(SIZE)):
        table.add_row(*(_stone_text(state, column, row, win) for column in range(SIZE)))
    return table


def board(state):
    """Return the board grid with the column letters above and below it
    and the row numbers on both sides. The most recent Move is highlighted,
    and the Winning five (if any) is shown on a green background."""
    # Each Point is drawn 4 characters apart, 2 from the grid's left edge.
    letters = Text("  " + "   ".join(LETTERS), style=LABEL_STYLE)
    # Row 9 is on the second line, under the top edge of the grid.
    numbers = Text(
        "\n" + "\n\n".join(str(row) for row in range(SIZE, 0, -1)) + "\n",
        style=LABEL_STYLE,
    )
    grid = Table.grid(padding=(0, 1))
    for _ in range(3):
        grid.add_column()
    grid.add_row("", letters, "")
    grid.add_row(numbers, board_table(state), numbers)
    grid.add_row("", letters, "")
    return grid


# --------------------------------------------------------------------------
# The Game type
# --------------------------------------------------------------------------

REJECTION_MESSAGES = {
    OFF_BOARD: "%s is off the board; columns are a-i and rows 1-9.",
    TAKEN: "%s is taken; pick an empty point.",
}

# A letter and a number of up to 3 digits (after lower-casing), spaces allowed
# between; the digit limit keeps int() from refusing a huge number.
POINT_PATTERN = re.compile(r"([a-z])\s*([0-9]{1,3})")


class Gomoku:
    """Gomoku as a Game type (see ``games.framework.GameType``)."""

    name = "gomoku"
    title = "Gomoku"
    summary = "Gomoku on a 9x9 board; enter a point such as e5, Black moves first"
    sides = (BLACK, WHITE)
    default_depth = DEFAULT_DEPTH

    def side_style(self, side):
        return SIDE_STYLES[side]

    def initial_state(self):
        return State()

    def to_move(self, state):
        # Black when both Sides have as many stones.
        stones = SIZE * SIZE - state.points.count(None)
        return BLACK if stones % 2 == 0 else WHITE

    def legal_moves(self, state):
        # The empty Points, nearest to the centre first.
        if GRID.line(state.points, state.last_move) is not None:
            return []
        return [p for p in POINT_ORDER if GRID.piece(state.points, p) is None]

    def search_moves(self, state):
        # The empty Points next to a stone (diagonals too), nearest to the
        # centre first; on an empty board, just the centre.
        empty = self.legal_moves(state)
        if len(empty) == SIZE * SIZE:
            return [CENTRE]
        return [
            p
            for p in empty
            if any(GRID.piece(state.points, n) is not None for n in NEIGHBOURS[p])
        ]

    def move_problem(self, state, move):
        if not on_board(*move):
            return OFF_BOARD
        if GRID.piece(state.points, move) is not None:
            return TAKEN
        return None

    def apply_move(self, state, move):
        problem = self.move_problem(state, move)
        if problem is not None:
            raise ValueError("point %s is %s" % (point_text(move), problem))
        return State(GRID.place(state.points, move, self.to_move(state)), move)

    def result(self, state):
        five = GRID.line(state.points, state.last_move)
        if five is not None:
            return GRID.piece(state.points, five[0])
        if None not in state.points:
            return DRAW
        return None

    def heuristic(self, state, side):
        # Every open window of five (holding stones of only one Side)
        # counts for the Side holding it, more the fuller it is.
        return GRID.score(state.points, side, WINDOW_SCORES)

    def unbeatable(self, depth):
        return False

    def parse_move(self, text):
        text = text.strip()
        match = POINT_PATTERN.fullmatch(text.lower())
        if match is None:
            return None, ("Please enter a point such as e5 (got %r)." % text)
        letter, number = match.groups()
        return (ord(letter) - ord("a"), int(number) - 1), None

    def move_text(self, move):
        return point_text(move)

    def describe_move(self, move):
        return "point [bold]%s[/]" % point_text(move)

    def rejection_message(self, move, reason):
        return REJECTION_MESSAGES[reason] % point_text(move)

    def move_prompt(self):
        return "Your move (e.g. e5):"

    def render(self, state):
        return board(state)

    def intro(self, against_computer):
        return [
            Text(
                "Type a point such as e5 (a column letter a-i, then a row "
                "number 1-9) to place a stone; the most recent move is "
                "highlighted."
            ),
        ]


GAME_TYPE = Gomoku()
