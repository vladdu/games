"""Connect Four, the second Game type: Red and Yellow alternate Moves,
dropping discs into a 7x6 board; four in a row wins.

State representation: an immutable ``State`` holding the 7 columns, each a
tuple of the discs in it from the bottom up (``"Red"`` or ``"Yellow"``), and
the column of the most recent Move (or None at the start). A Move is a
column index 0-6; the human types it as 1-7. Red always moves first.
"""

from dataclasses import dataclass
from typing import Optional

from rich import box
from rich.table import Table
from rich.text import Text

from games.framework import DRAW

COLUMNS = 7
ROWS = 6
RED = "Red"
YELLOW = "Yellow"


@dataclass(frozen=True)
class State:
    """A Connect Four position: ``columns`` holds each column's discs from
    the bottom up, and ``last_move`` is the column of the most recent Move."""
    columns: tuple = ((),) * COLUMNS
    last_move: Optional[int] = None


def new_state():
    """Return the empty board, Red to move."""
    return State()


def to_move(state):
    """Return the Side to move: Red when both Sides have as many discs."""
    discs = sum(len(column) for column in state.columns)
    return RED if discs % 2 == 0 else YELLOW


def disc_at(state, column, row):
    """Return the disc at ``column`` (0-6) and ``row`` (0 = bottom), or
    None if that place is empty."""
    discs = state.columns[column]
    return discs[row] if row < len(discs) else None


# Legal Moves are listed centre first: the computer's search tries them in
# this order, which prunes more, and among equally good Moves plays the first.
MOVE_ORDER = (3, 2, 4, 1, 5, 0, 6)


def legal_moves(state):
    """Return the columns (0-6) that still have room, centre first."""
    if _find_four(state) is not None:
        return []
    return [c for c in MOVE_ORDER if len(state.columns[c]) < ROWS]


def apply_move(state, column):
    """Return the state after the Side to move drops a disc in ``column``.

    Raises ValueError if the Move is not legal.
    """
    if not 0 <= column < COLUMNS:
        raise ValueError("column out of range: %r" % (column,))
    if len(state.columns[column]) >= ROWS:
        raise ValueError("column %d is full" % column)
    columns = list(state.columns)
    columns[column] = columns[column] + (to_move(state),)
    return State(tuple(columns), column)


def _lines():
    """Yield every window of four places as ``((col, row), ...)``."""
    for col in range(COLUMNS):
        for row in range(ROWS):
            for dc, dr in ((1, 0), (0, 1), (1, 1), (1, -1)):
                end_col, end_row = col + 3 * dc, row + 3 * dr
                if 0 <= end_col < COLUMNS and 0 <= end_row < ROWS:
                    yield tuple((col + i * dc, row + i * dr)
                                for i in range(4))


WINDOWS = tuple(_lines())


def _find_four(state):
    """Return the first window of four held by one Side, or None."""
    for window in WINDOWS:
        first = disc_at(state, *window[0])
        if first is not None and all(disc_at(state, c, r) == first
                                     for c, r in window[1:]):
            return window
    return None


def result(state):
    """Return RED or YELLOW for a win, DRAW for a full board with no four
    in a row, or None while the Game is in progress."""
    four = _find_four(state)
    if four is not None:
        return disc_at(state, *four[0])
    if all(len(column) == ROWS for column in state.columns):
        return DRAW
    return None


def winning_four(state):
    """Return the ``(col, row)`` places of the winning four, or None."""
    return _find_four(state)


# Why a Move is rejected (see move_problem).
OUT_OF_RANGE = "out of range"
FULL = "full"


def move_problem(state, column):
    """Return why dropping a disc in ``column`` is not allowed
    (``OUT_OF_RANGE`` or ``FULL``), or None if the Move is legal."""
    if not 0 <= column < COLUMNS:
        return OUT_OF_RANGE
    if len(state.columns[column]) >= ROWS:
        return FULL
    return None


# --------------------------------------------------------------------------
# The computer: its heuristic for the shared search
# --------------------------------------------------------------------------

DEFAULT_DEPTH = 6
# Score of a window of four holding n discs of one Side and none of the
# other.
WINDOW_SCORES = {1: 1, 2: 10, 3: 50}


def heuristic(state, side):
    """Score a position in progress from ``side``'s point of view: every
    open window of four (holding discs of only one Side) counts for the
    Side holding it, more the fuller it is."""
    score = 0
    for window in WINDOWS:
        mine = theirs = 0
        for c, r in window:
            disc = disc_at(state, c, r)
            if disc == side:
                mine += 1
            elif disc is not None:
                theirs += 1
        if mine and not theirs:
            score += WINDOW_SCORES[mine]
        elif theirs and not mine:
            score -= WINDOW_SCORES[theirs]
    return score


# --------------------------------------------------------------------------
# Rich rendering (pure: builds renderables, does no I/O)
# --------------------------------------------------------------------------

SIDE_STYLES = {RED: "bold red", YELLOW: "bold yellow"}
DISC_GLYPHS = {RED: "R", YELLOW: "Y"}
HEADER_STYLE = "bold"
LAST_MOVE_STYLE = "reverse"
WIN_STYLE = "bold white on green"


def _place_text(state, column, row, win):
    disc = disc_at(state, column, row)
    if disc is None:
        return Text(" ")
    text = Text(DISC_GLYPHS[disc], style=SIDE_STYLES[disc])
    if (column, row) in win:
        text.stylize(WIN_STYLE)
    elif column == state.last_move and row == len(state.columns[column]) - 1:
        text.stylize(LAST_MOVE_STYLE)
    return text


def board_table(state):
    """Return a rich Table drawing the board as a heavy-lined 7x6 grid under
    a header of column numbers. The most recent Move is highlighted, and the
    winning four (if any) is shown on a green background."""
    table = Table(
        box=box.HEAVY,
        show_header=True,
        show_lines=True,
        padding=(0, 1),
        pad_edge=True,
    )
    for column in range(COLUMNS):
        table.add_column(Text(str(column + 1), style=HEADER_STYLE),
                         justify="center", min_width=1)
    win = winning_four(state) or ()
    for row in reversed(range(ROWS)):
        table.add_row(*(_place_text(state, column, row, win)
                        for column in range(COLUMNS)))
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
    summary = ("Connect Four on a 7x6 board; enter a column number 1-7 to "
               "drop a disc, Red moves first")
    sides = (RED, YELLOW)
    default_depth = DEFAULT_DEPTH

    def side_style(self, side):
        return SIDE_STYLES[side]

    def initial_state(self):
        return new_state()

    def to_move(self, state):
        return to_move(state)

    def legal_moves(self, state):
        return legal_moves(state)

    def move_problem(self, state, move):
        return move_problem(state, move)

    def apply_move(self, state, move):
        return apply_move(state, move)

    def result(self, state):
        return result(state)

    def heuristic(self, state, side):
        return heuristic(state, side)

    def unbeatable(self, depth):
        return False

    def parse_move(self, text):
        text = text.strip()
        try:
            number = int(text)
        except ValueError:
            return None, ("Please enter a column number from 1 to 7 "
                          "(got %r)." % text)
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
            Text("Type a column number from 1 to 7 to drop a disc; "
                 "the most recent move is highlighted."),
        ]


GAME_TYPE = ConnectFour()
