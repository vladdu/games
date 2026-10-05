"""Tic-tac-toe, the first Game type: X and O alternate Moves, placing their
mark in an empty Cell of a 3x3 grid; three in a row wins.

State: an immutable ``State`` holding the 9 Cells (each ``"X"``, ``"O"`` or
``" "``, indexed 0..8 left to right and top to bottom) and the index of the
most recent Move (None at the start). A Move is a Cell index 0-8. The Cell
numbers 1..9 shown to the human follow a numeric keypad instead (7 8 9 on the
top row, 1 2 3 on the bottom); ``cell_number`` and ``cell_index`` convert
between them.

The board is drawn as a heavy-lined rich table with X and O in their own
colors; empty Cells show a dim guide number (1-9), the most recent Move is
highlighted, and a Winning line gets a green background.
"""

from dataclasses import dataclass
from typing import Optional

from rich import box
from rich.table import Table
from rich.text import Text

from games.framework import DRAW

EMPTY = " "
X = "X"
O = "O"

# Why a Move is rejected (see move_problem).
OUT_OF_RANGE = "out of range"
TAKEN = "taken"

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


@dataclass(frozen=True)
class State:
    """A tic-tac-toe position: the 9 ``cells`` and the index of the most
    recent Move, ``last_move``."""
    cells: tuple = (EMPTY,) * 9
    last_move: Optional[int] = None


# --------------------------------------------------------------------------
# Rules (pure functions)
# --------------------------------------------------------------------------

def _to_move(cells):
    return X if cells.count(X) == cells.count(O) else O


def _find_line(cells):
    """Return the first ``(a, b, c)`` line held by one Side, or None."""
    for line in WIN_LINES:
        a, b, c = line
        if cells[a] != EMPTY and cells[a] == cells[b] == cells[c]:
            return line
    return None


def _result(cells):
    line = _find_line(cells)
    if line is not None:
        return cells[line[0]]
    if EMPTY not in cells:
        return DRAW
    return None


def _empty_cells(cells):
    return [i for i, cell in enumerate(cells) if cell == EMPTY]


def _place(cells, index):
    placed = list(cells)
    placed[index] = _to_move(cells)
    return tuple(placed)


def move_problem(state, index):
    """Return why a Move at ``index`` is illegal (``OUT_OF_RANGE`` or
    ``TAKEN``), or None if it is legal."""
    if not 0 <= index < 9:
        return OUT_OF_RANGE
    if state.cells[index] != EMPTY:
        return TAKEN
    return None


def apply_move(state, index):
    """Return the state after the Side to move places its mark at
    ``index``. Raises ValueError if the Move is not legal."""
    problem = move_problem(state, index)
    if problem is not None:
        raise ValueError("cell index %r is %s" % (index, problem))
    return State(_place(state.cells, index), index)


# --------------------------------------------------------------------------
# Rich rendering (pure: builds renderables, does no I/O)
# --------------------------------------------------------------------------

SIDE_STYLES = {X: "bold cyan", O: "bold magenta"}
GUIDE_STYLE = "dim grey50"
LAST_MOVE_STYLE = "reverse"
WIN_STYLE = "bold white on green"


def cell_number(index):
    """Return the keypad-order number (1-9) the human sees for Cell
    ``index``. Indices outside 0-8 map to ``index + 1``, so a rejected Move
    can still be reported with the number the human typed."""
    if not 0 <= index < 9:
        return index + 1
    row, col = divmod(index, 3)
    return (2 - row) * 3 + col + 1


def cell_index(number):
    """Return the Cell index for the keypad-order ``number``; the inverse
    of ``cell_number`` (flipping the rows is its own inverse)."""
    return cell_number(number - 1) - 1


def _cell_text(state, index, win_line):
    cell = state.cells[index]
    if cell == EMPTY:
        return Text(str(cell_number(index)), style=GUIDE_STYLE)
    text = Text(cell, style=SIDE_STYLES[cell])
    if win_line is not None and index in win_line:
        text.stylize(WIN_STYLE)
    elif index == state.last_move:
        text.stylize(LAST_MOVE_STYLE)
    return text


def board_table(state):
    """Return a rich Table drawing the board as a 3x3 grid with full lines.
    The most recent Move is highlighted and the Winning line, if any, is on
    a green background."""
    table = Table(
        box=box.HEAVY,
        show_header=False,
        show_lines=True,
        padding=(1, 3),
        pad_edge=True,
    )
    for _ in range(3):
        table.add_column(justify="center", vertical="middle", min_width=1)
    win_line = _find_line(state.cells)
    for r in range(3):
        table.add_row(*(_cell_text(state, r * 3 + c, win_line)
                        for c in range(3)))
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
    sides = (X, O)
    default_depth = None  # unlimited: the computer is unbeatable

    def side_style(self, side):
        return SIDE_STYLES[side]

    def initial_state(self):
        return State()

    def to_move(self, state):
        return _to_move(state.cells)

    def legal_moves(self, state):
        if _result(state.cells) is not None:
            return []
        return _empty_cells(state.cells)

    def move_problem(self, state, move):
        return move_problem(state, move)

    def apply_move(self, state, move):
        return apply_move(state, move)

    def result(self, state):
        return _result(state.cells)

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
        return cell_index(number), None

    def move_text(self, move):
        return str(cell_number(move))

    def describe_move(self, move):
        return "[bold]%d[/]" % cell_number(move)

    def rejection_message(self, move, reason):
        return REJECTION_MESSAGES[reason] % cell_number(move)

    def move_prompt(self):
        return "Your move (1-9):"

    def render(self, state):
        return board_table(state)

    def intro(self):
        return [
            Text("Cells are numbered like this "
                 "(the computer's last move is highlighted):"),
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
    "and 1 2 3 on the bottom.")


def main(argv=None):
    """``python3 tictactoe.py``: tic-tac-toe with the games command line,
    minus ``--game``."""
    from games import cli  # cli imports the registry, which imports us
    return cli.main(argv, None, DESCRIPTION, GAME_TYPE)
