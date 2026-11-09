"""Connect Four, the second Game type: Red and Yellow alternate Moves,
dropping discs into a 7x6 board; four in a row wins.

State representation: an immutable ``State`` holding the 42 places row by
row from the bottom left (``"Red"``, ``"Yellow"`` or None), and the point
``(column, row)`` where the most recent disc landed (or None at the start).
A Move is a column index 0-6; the human types it as 1-7. Red always moves
first.
"""

from dataclasses import dataclass

from rich import box
from rich.table import Table
from rich.text import Text

from games.framework import DRAW
from games.grid import Grid

COLUMNS = 7
ROWS = 6
RED = "Red"
YELLOW = "Yellow"
GRID = Grid(COLUMNS, ROWS, 4)


@dataclass(frozen=True)
class State:
    """A Connect Four position: ``cells`` holds the disc on every place, row
    by row from the bottom left, and ``last_move`` is the point where the
    most recent disc landed."""

    cells: tuple = (None,) * (COLUMNS * ROWS)
    last_move: tuple | None = None


def landing_row(state, column):
    """The lowest empty row in ``column``, or None if it is full."""
    for row in range(ROWS):
        if GRID.piece(state.cells, (column, row)) is None:
            return row
    return None


def is_full(state, column):
    """Whether ``column`` has no empty place left."""
    return GRID.piece(state.cells, (column, ROWS - 1)) is not None


# Legal Moves are listed centre first: the computer's search tries them in
# this order, which prunes more, and among equally good Moves plays the first.
MOVE_ORDER = (3, 2, 4, 1, 5, 0, 6)

# Why a Move is rejected (see ConnectFour.move_problem).
OUT_OF_RANGE = "out of range"
FULL = "full"

DEFAULT_DEPTH = 6
# Score of a window of four holding n discs of one Side and none of the
# other, for the heuristic of the shared search.
WINDOW_SCORES = {1: 1, 2: 10, 3: 50}


# --------------------------------------------------------------------------
# Rich rendering (pure: builds renderables, does no I/O)
# --------------------------------------------------------------------------

SIDE_STYLES = {RED: "bold red", YELLOW: "bold yellow"}
DISC_GLYPHS = {RED: "R", YELLOW: "Y"}
HEADER_STYLE = "bold"
LAST_MOVE_STYLE = "reverse"
WIN_STYLE = "bold white on green"


def _place_text(state, column, row, win):
    disc = GRID.piece(state.cells, (column, row))
    if disc is None:
        return Text(" ")
    text = Text(DISC_GLYPHS[disc], style=SIDE_STYLES[disc])
    if (column, row) in win:
        text.stylize(WIN_STYLE)
    elif (column, row) == state.last_move:
        text.stylize(LAST_MOVE_STYLE)
    return text


def board_table(state):
    """Return a rich Table drawing the board as a thin-lined 7x6 grid under
    a header of column numbers. The most recent Move is highlighted, and the
    winning four (if any) is shown on a green background."""
    table = Table(
        box=box.SQUARE,
        show_header=True,
        show_lines=True,
        padding=(0, 1),
        pad_edge=True,
    )
    for column in range(COLUMNS):
        table.add_column(
            Text(str(column + 1), style=HEADER_STYLE), justify="center", min_width=1
        )
    win = GRID.line(state.cells, state.last_move) or ()
    for row in reversed(range(ROWS)):
        table.add_row(
            *(_place_text(state, column, row, win) for column in range(COLUMNS))
        )
    return table


# --------------------------------------------------------------------------
# The Game type
# --------------------------------------------------------------------------

REJECTION_MESSAGES = {
    OUT_OF_RANGE: "%d is out of range; choose a column from 1 to 7.",
    FULL: "Column %d is full; pick another column.",
}


class ConnectFour:
    """Connect Four as a Game type (see ``games.framework.GameType``)."""

    name = "connect-four"
    title = "Connect Four"
    summary = (
        "Connect Four on a 7x6 board; enter a column number 1-7 to "
        "drop a disc, Red moves first"
    )
    sides = (RED, YELLOW)
    default_depth = DEFAULT_DEPTH

    def side_style(self, side):
        return SIDE_STYLES[side]

    def initial_state(self):
        return State()

    def to_move(self, state):
        # Red when both Sides have as many discs.
        discs = COLUMNS * ROWS - state.cells.count(None)
        return RED if discs % 2 == 0 else YELLOW

    def legal_moves(self, state):
        # The columns that still have room, centre first.
        if GRID.line(state.cells, state.last_move) is not None:
            return []
        return [c for c in MOVE_ORDER if not is_full(state, c)]

    def move_problem(self, state, move):
        if not 0 <= move < COLUMNS:
            return OUT_OF_RANGE
        if is_full(state, move):
            return FULL
        return None

    def apply_move(self, state, move):
        problem = self.move_problem(state, move)
        if problem is not None:
            raise ValueError("column %r is %s" % (move, problem))
        point = (move, landing_row(state, move))
        return State(GRID.place(state.cells, point, self.to_move(state)), point)

    def result(self, state):
        four = GRID.line(state.cells, state.last_move)
        if four is not None:
            return GRID.piece(state.cells, four[0])
        if None not in state.cells:
            return DRAW
        return None

    def heuristic(self, state, side):
        # Every open window of four (holding discs of only one Side) counts
        # for the Side holding it, more the fuller it is.
        return GRID.score(state.cells, side, WINDOW_SCORES)

    def unbeatable(self, depth):
        return False

    def parse_move(self, text):
        text = text.strip()
        try:
            number = int(text)
        except ValueError:
            return None, ("Please enter a column number from 1 to 7 (got %r)." % text)
        return number - 1, None

    def move_text(self, move):
        return str(move + 1)

    def describe_move(self, move):
        return "column [bold]%d[/]" % (move + 1)

    def rejection_message(self, move, reason):
        return REJECTION_MESSAGES[reason] % (move + 1)

    def move_prompt(self):
        return "Your move (1-7):"

    def render(self, state):
        return board_table(state)

    def intro(self, against_computer):
        return [
            Text(
                "Type a column number from 1 to 7 to drop a disc; "
                "the most recent move is highlighted."
            ),
        ]


GAME_TYPE = ConnectFour()
