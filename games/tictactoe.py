"""Tic-tac-toe, the first Game type: X and O alternate Moves, placing their
mark in an empty Cell of a 3x3 grid; three in a row wins.

State: an immutable ``State`` holding the 9 Cells (each ``"X"``, ``"O"`` or
None, row by row from the bottom left) and the point ``(column, row)`` of the
most recent Move (None at the start). A Move is a Cell index 0-8. Bottom-left
order is numeric keypad order (7 8 9 on the top row, 1 2 3 on the bottom), so
the Cell number shown to the human is the index + 1.

The board is drawn as a thin-lined rich table with X and O in their own
colors; empty Cells show a dim guide number (1-9), the most recent Move is
highlighted, and a Winning line gets a green background.
"""

from dataclasses import dataclass

from rich import box
from rich.table import Table
from rich.text import Text

from games.framework import DRAW
from games.grid import Grid

X = "X"
O = "O"
GRID = Grid(3, 3, 3)
# Legal Moves are listed top row first, as the Cells are drawn: the computer
# plays the first of equally good Moves, so this order fixes its choices.
MOVE_ORDER = (6, 7, 8, 3, 4, 5, 0, 1, 2)

# Why a Move is rejected (see TicTacToe.move_problem).
OUT_OF_RANGE = "out of range"
TAKEN = "taken"


@dataclass(frozen=True)
class State:
    """A tic-tac-toe position: the 9 ``cells`` from the bottom left and the
    point where the most recent Move landed, ``last_move``."""

    cells: tuple = (None,) * 9
    last_move: tuple | None = None


# --------------------------------------------------------------------------
# Rules (pure functions)
# --------------------------------------------------------------------------


def _to_move(cells):
    return X if cells.count(X) == cells.count(O) else O


def _point(index):
    return index % GRID.width, index // GRID.width


# --------------------------------------------------------------------------
# Rich rendering (pure: builds renderables, does no I/O)
# --------------------------------------------------------------------------

SIDE_STYLES = {X: "bold cyan", O: "bold magenta"}
GUIDE_STYLE = "dim grey50"
LAST_MOVE_STYLE = "reverse"
WIN_STYLE = "bold white on green"


def _cell_text(state, point, win_line):
    cell = GRID.piece(state.cells, point)
    if cell is None:
        return Text(str(point[1] * GRID.width + point[0] + 1), style=GUIDE_STYLE)
    text = Text(cell, style=SIDE_STYLES[cell])
    if win_line is not None and point in win_line:
        text.stylize(WIN_STYLE)
    elif point == state.last_move:
        text.stylize(LAST_MOVE_STYLE)
    return text


def board_table(state):
    """Return a rich Table drawing the board as a 3x3 grid with full lines.
    The most recent Move is highlighted and the Winning line, if any, is on
    a green background."""
    table = Table(
        box=box.SQUARE,
        show_header=False,
        show_lines=True,
        padding=(1, 3),
        pad_edge=True,
    )
    for _ in range(GRID.width):
        table.add_column(justify="center", vertical="middle", min_width=1)
    win_line = GRID.line(state.cells, state.last_move)
    for r in reversed(range(GRID.height)):  # top row first
        table.add_row(*(_cell_text(state, (c, r), win_line) for c in range(GRID.width)))
    return table


# --------------------------------------------------------------------------
# The Game type
# --------------------------------------------------------------------------

REJECTION_MESSAGES = {
    OUT_OF_RANGE: "%d is out of range; choose a cell from 1 to 9.",
    TAKEN: "Cell %d is already taken; pick an empty cell.",
}


class TicTacToe:
    """Tic-tac-toe as a Game type (see ``games.framework.GameType``)."""

    name = "tictactoe"
    title = "Tic-tac-toe"
    summary = (
        "Tic-tac-toe on a 3x3 grid; enter a cell number 1-9, "
        "numbered like a numeric keypad"
    )
    sides = (X, O)
    default_depth = None  # unlimited: the computer is unbeatable

    def side_style(self, side):
        return SIDE_STYLES[side]

    def initial_state(self):
        return State()

    def to_move(self, state):
        return _to_move(state.cells)

    def legal_moves(self, state):
        if self.result(state) is not None:
            return []
        return [i for i in MOVE_ORDER if state.cells[i] is None]

    def move_problem(self, state, move):
        if not 0 <= move < 9:
            return OUT_OF_RANGE
        if GRID.piece(state.cells, _point(move)) is not None:
            return TAKEN
        return None

    def apply_move(self, state, move):
        problem = self.move_problem(state, move)
        if problem is not None:
            raise ValueError("cell index %r is %s" % (move, problem))
        point = _point(move)
        return State(GRID.place(state.cells, point, self.to_move(state)), point)

    def result(self, state):
        line = GRID.line(state.cells, state.last_move)
        if line is not None:
            return GRID.piece(state.cells, line[0])
        if None not in state.cells:
            return DRAW
        return None

    def heuristic(self, state, side):
        # Tic-tac-toe is always searched to the end of the Game.
        return 0

    def unbeatable(self, depth):
        return depth is None

    def parse_move(self, text):
        text = text.strip()
        try:
            number = int(text)
        except ValueError:
            return None, "Please enter a number from 1 to 9 (got %r)." % text
        return number - 1, None

    def move_text(self, move):
        return str(move + 1)

    def describe_move(self, move):
        return "[bold]%d[/]" % (move + 1)

    def rejection_message(self, move, reason):
        return REJECTION_MESSAGES[reason] % (move + 1)

    def move_prompt(self):
        return "Your move (1-9):"

    def render(self, state):
        return board_table(state)

    def intro(self, against_computer):
        highlighted = (
            "the computer's last move" if against_computer else "the most recent move"
        )
        return [
            Text("Cells are numbered like this (%s is highlighted):" % highlighted),
            board_table(State()),
        ]


GAME_TYPE = TicTacToe()


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

DESCRIPTION = (
    "Play tic-tac-toe in the terminal, by default against an unbeatable "
    "computer. X always moves first; enter a cell number 1-9 to move. "
    "Cells are numbered like a numeric keypad, with 7 8 9 on the top row "
    "and 1 2 3 on the bottom."
)


def main(argv=None):
    """The ``tictactoe`` console script: tic-tac-toe with the games command line,
    minus ``--game``."""
    from games import cli  # cli imports the registry, which imports us

    return cli.main(argv, None, DESCRIPTION, GAME_TYPE)
