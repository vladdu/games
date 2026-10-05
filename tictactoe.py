#!/usr/bin/env python3
"""Terminal tic-tac-toe: a human plays against an unbeatable minimax computer.

Board representation: a tuple of 9 cells, each ``"X"``, ``"O"`` or ``" "``.
Index 0..8 maps to the cell numbers 1..9 shown to the user, numbered left to
right and top to bottom in a 3x3 grid.

The terminal UI uses the ``rich`` library: the board is drawn as a heavy-lined
table with X and O in their own colors, empty cells show a dim guide number
(1-9), the computer's last move is highlighted, and a winning line gets a
green background.

The board rules and the rich rendering helpers are pure functions. A Game
(``play_game``) talks to the human only through a Player I/O object, so it can
be played in tests by a scripted adapter; ``TerminalIO`` is the adapter that
drives the real terminal.
"""

import argparse
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Protocol

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

EMPTY = " "
X = "X"
O = "O"
DRAW = "draw"

# Why a move is rejected (see move_problem).
OUT_OF_RANGE = "out of range"
TAKEN = "taken"

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)


# --------------------------------------------------------------------------
# Pure game logic
# --------------------------------------------------------------------------

def new_board():
    """Return an empty board."""
    return (EMPTY,) * 9


def other(player):
    """Return the opponent of ``player``."""
    return O if player == X else X


def available_moves(board):
    """Return the list of empty cell indices (0-8)."""
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def move_problem(board, index):
    """Return why a move at ``index`` is illegal (``OUT_OF_RANGE`` or
    ``TAKEN``), or None if the move is legal."""
    if not 0 <= index < 9:
        return OUT_OF_RANGE
    if board[index] != EMPTY:
        return TAKEN
    return None


def apply_move(board, index, player):
    """Return a new board with ``player`` placed at ``index``.

    Raises ValueError if the index is out of range or the cell is occupied.
    """
    problem = move_problem(board, index)
    if problem == OUT_OF_RANGE:
        raise ValueError("index out of range: %r" % (index,))
    if problem == TAKEN:
        raise ValueError("cell %d is already occupied" % (index + 1))
    cells = list(board)
    cells[index] = player
    return tuple(cells)


def winner(board):
    """Return ``"X"`` or ``"O"`` for a win, ``"draw"`` for a full board with
    no winner, or ``None`` if the game is still in progress."""
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if EMPTY not in board:
        return DRAW
    return None


def current_player(board):
    """Return whose turn it is (X always moves first)."""
    xs = board.count(X)
    os_ = board.count(O)
    return X if xs == os_ else O


@lru_cache(maxsize=None)
def _minimax(board, to_move, me, depth, alpha, beta):
    """Score ``board`` from ``me``'s perspective with ``to_move`` to play.

    Depth-aware: a win scores ``10 - depth`` (faster wins are better) and a
    loss scores ``depth - 10`` (slower losses are better). Draw is 0.
    """
    result = winner(board)
    if result == me:
        return 10 - depth
    if result == DRAW:
        return 0
    if result is not None:
        return depth - 10

    maximizing = to_move == me
    best = -100 if maximizing else 100
    for move in available_moves(board):
        child = apply_move(board, move, to_move)
        score = _minimax(child, other(to_move), me, depth + 1, alpha, beta)
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def best_move(board, player):
    """Return the best cell index (0-8) for ``player`` on ``board``.

    Uses full minimax with alpha-beta pruning and depth-aware scoring, so the
    move chosen never loses, wins as fast as possible, and when losing is
    unavoidable (impossible from a fair start) delays it as long as possible.
    Ties are broken by lowest index, making the choice deterministic.
    Returns None if the game is already over.
    """
    board = tuple(board)
    if winner(board) is not None:
        return None
    best_score = -100
    choice = None
    for move in available_moves(board):
        child = apply_move(board, move, player)
        # Full window per root child so scores are exact and comparable.
        score = _minimax(child, other(player), player, 1, -100, 100)
        if score > best_score:
            best_score = score
            choice = move
    return choice


def winning_line(board):
    """Return the ``(a, b, c)`` indices of the winning line, or None."""
    for line in WIN_LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return line
    return None


# --------------------------------------------------------------------------
# Rich rendering (pure: builds renderables, does no I/O)
# --------------------------------------------------------------------------

PLAYER_STYLES = {X: "bold cyan", O: "bold magenta"}
GUIDE_STYLE = "dim grey50"
LAST_MOVE_STYLE = "reverse"
WIN_STYLE = "bold white on green"


def player_text(player):
    """Return ``player`` ("X" or "O") as a styled rich Text."""
    return Text(player, style=PLAYER_STYLES[player])


def cell_text(board, index, last_move=None, win_line=None):
    """Return the styled Text for one cell.

    Pieces use their player color; empty cells show a dim guide number. The
    computer's last move is reversed and winning cells get a green background.
    """
    if board[index] == EMPTY:
        return Text(str(index + 1), style=GUIDE_STYLE)
    text = player_text(board[index])
    if win_line is not None and index in win_line:
        text.stylize(WIN_STYLE)
    elif index == last_move:
        text.stylize(LAST_MOVE_STYLE)
    return text


def board_table(board, last_move=None, win_line=None):
    """Return a rich Table drawing the board as a 3x3 grid with full lines."""
    table = Table(
        box=box.HEAVY,
        show_header=False,
        show_lines=True,
        padding=(1, 3),
        pad_edge=True,
    )
    for _ in range(3):
        table.add_column(justify="center", vertical="middle", min_width=1)
    for r in range(3):
        table.add_row(*(cell_text(board, r * 3 + c, last_move, win_line)
                        for c in range(3)))
    return table


# --------------------------------------------------------------------------
# Game
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Started:
    """The Game has started; ``human`` and ``computer`` are X and O."""
    human: str
    computer: str


@dataclass(frozen=True)
class Moved:
    """``player`` moved at ``index``, giving ``board``.

    ``last_computer_move`` is the index of the computer's most recent move
    (possibly this one), or None if the computer has not moved yet.
    """
    player: str
    index: int
    board: tuple
    last_computer_move: Optional[int]


@dataclass(frozen=True)
class MoveRejected:
    """The human's move at ``index`` was refused for ``reason``
    (``OUT_OF_RANGE`` or ``TAKEN``); the human will be asked again."""
    index: int
    reason: str


@dataclass(frozen=True)
class GameOver:
    """The Game ended with ``result`` (X, O or DRAW) on ``board``.
    ``winning_line`` is None for a draw."""
    result: str
    board: tuple
    winning_line: Optional[tuple]


class PlayerIO(Protocol):
    """Everything a Game needs from the human's side.

    Methods may raise EOFError or KeyboardInterrupt to quit; the Game lets
    them propagate.
    """

    def wants_first(self) -> bool:
        """Return True if the human moves first (and so plays X)."""

    def choose_move(self, board) -> int:
        """Return the index the human wants to move at. It need not be
        legal: the Game rejects it with a MoveRejected event and asks
        again."""

    def show(self, event) -> None:
        """Tell the human about a Game event."""


def play_game(io):
    """Play one full Game against the human behind ``io`` (a PlayerIO).

    Returns the result (``"X"``, ``"O"`` or ``"draw"``).
    """
    human = X if io.wants_first() else O
    computer = other(human)
    io.show(Started(human, computer))

    board = new_board()
    turn = X
    last_computer_move = None
    while winner(board) is None:
        if turn == human:
            move = _human_move(io, board)
        else:
            move = best_move(board, computer)
            last_computer_move = move
        board = apply_move(board, move, turn)
        io.show(Moved(turn, move, board, last_computer_move))
        turn = other(turn)

    result = winner(board)
    io.show(GameOver(result, board, winning_line(board)))
    return result


def _human_move(io, board):
    """Ask the human for a move until a legal one is given."""
    while True:
        move = io.choose_move(board)
        problem = move_problem(board, move)
        if problem is None:
            return move
        io.show(MoveRejected(move, problem))


# --------------------------------------------------------------------------
# Terminal I/O
# --------------------------------------------------------------------------

def parse_move(text):
    """Turn the human's input into a cell index. Return ``(index, None)`` on
    success or ``(None, error_message)`` if it is not a number. The index is
    not checked against the board."""
    text = text.strip()
    try:
        number = int(text)
    except ValueError:
        return None, "Please enter a number from 1 to 9 (got %r)." % text
    return number - 1, None


REJECTION_MESSAGES = {
    OUT_OF_RANGE: "%d is out of range; choose a cell from 1 to 9.",
    TAKEN: "Cell %d is already taken; pick an empty cell.",
}


class TerminalIO:
    """PlayerIO adapter for a human at a terminal, drawn with rich.

    The board is shown before every turn: it is drawn lazily, just before
    the next prompt or computer move, so the final board is drawn only once,
    with its winning line.
    """

    def __init__(self, console):
        self.console = console
        self._human = None
        self._computer = None
        self._last_computer_move = None
        self._pending_board = None

    def say(self, *parts, style=None):
        """Print a line made of strings (rich markup) and Text objects."""
        line = Text()
        for part in parts:
            line.append(Text.from_markup(part) if isinstance(part, str)
                        else part)
        self.console.print(line, style=style)

    def show_board(self, board, last_move=None, win_line=None):
        self.console.print(board_table(board, last_move, win_line))

    def ask(self, prompt):
        """Prompt with rich markup. Raises EOFError on EOF."""
        return self.console.input("[bold yellow]%s[/] " % prompt)

    def ask_yes_no(self, prompt):
        """Prompt until the user answers y/yes or n/no. Raises EOFError on
        EOF."""
        while True:
            answer = self.ask(prompt).strip().lower()
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False
            self.say("[red]Please answer 'y' or 'n'.[/]")

    # PlayerIO

    def wants_first(self):
        return self.ask_yes_no("Do you want to go first? (y/n):")

    def choose_move(self, board):
        self._draw_pending_board()
        while True:
            index, error = parse_move(self.ask("Your move (1-9):"))
            if error is None:
                return index
            self.say(Text(error, style="red"))

    def show(self, event):
        if isinstance(event, Started):
            self._human, self._computer = event.human, event.computer
            self._last_computer_move = None
            self.say("You are ", player_text(event.human),
                     ", the computer is ", player_text(event.computer), ". ",
                     player_text(X), " moves first.")
            self.console.print()
            self._pending_board = new_board()
        elif isinstance(event, Moved):
            self._draw_pending_board()
            if event.player == self._computer:
                self.say("Computer (", player_text(event.player),
                         ") plays [bold]%d[/]." % (event.index + 1))
            self.console.print()
            self._last_computer_move = event.last_computer_move
            self._pending_board = event.board
        elif isinstance(event, MoveRejected):
            message = REJECTION_MESSAGES[event.reason] % (event.index + 1)
            self.say(Text(message, style="red"))
        elif isinstance(event, GameOver):
            self._pending_board = None
            self.show_board(event.board, self._last_computer_move,
                            event.winning_line)
            if event.result == DRAW:
                self.say("[bold yellow]It's a draw![/]")
            elif event.result == self._human:
                self.say("[bold green]You win! (This should not happen...)[/]")
            else:
                self.say("[bold red]The computer wins![/]")

    def _draw_pending_board(self):
        if self._pending_board is not None:
            self.show_board(self._pending_board, self._last_computer_move)
            self._pending_board = None


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def parse_args(argv=None):
    """Parse command-line arguments (only ``-h``/``--help`` is supported)."""
    parser = argparse.ArgumentParser(
        description="Play tic-tac-toe in the terminal against an unbeatable "
                    "minimax computer. You choose whether to go first (X "
                    "always moves first), then enter a cell number 1-9 to "
                    "move; cells are numbered left to right, top to bottom.",
        epilog="After each game you can play again (y/n). "
               "Press Ctrl+C or Ctrl+D to quit at any time.")
    return parser.parse_args(argv)


def main(argv=None):
    parse_args(argv)
    io = TerminalIO(Console(highlight=False))
    io.console.print(Panel.fit(
        Text.assemble(
            ("Tic-tac-toe", "bold"), "\n",
            "you vs. the unbeatable computer"),
        border_style="bright_blue", box=box.DOUBLE, padding=(0, 4)))
    io.say("Cells are numbered like this "
           "(the computer's last move is highlighted):")
    io.show_board(new_board())
    io.console.print()
    try:
        while True:
            play_game(io)
            io.console.print()
            if not io.ask_yes_no("Play again? (y/n):"):
                break
            io.console.print()
    except (EOFError, KeyboardInterrupt):
        io.console.print()
    io.say("[bold]Goodbye![/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
