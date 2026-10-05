#!/usr/bin/env python3
"""Terminal tic-tac-toe: a human plays against an unbeatable minimax computer.

Board representation: a tuple of 9 cells, each ``"X"``, ``"O"`` or ``" "``.
Index 0..8 maps to the cell numbers 1..9 shown to the user, numbered left to
right and top to bottom in a 3x3 grid.

The terminal UI uses the ``rich`` library: the board is drawn as a heavy-lined
table with X and O in their own colors, empty cells show a dim guide number
(1-9), the computer's last move is highlighted, and a winning line gets a
green background.

The game logic and the rich rendering helpers (everything above the "I/O"
section) are pure functions, so they can be tested without any terminal
interaction.
"""

import argparse
import sys
from functools import lru_cache

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

EMPTY = " "
X = "X"
O = "O"
DRAW = "draw"

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


def apply_move(board, index, player):
    """Return a new board with ``player`` placed at ``index``.

    Raises ValueError if the index is out of range or the cell is occupied.
    """
    if not 0 <= index < 9:
        raise ValueError("index out of range: %r" % (index,))
    if board[index] != EMPTY:
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


def parse_move(text, board):
    """Validate user input. Return ``(index, None)`` on success or
    ``(None, error_message)`` on failure."""
    text = text.strip()
    try:
        number = int(text)
    except ValueError:
        return None, "Please enter a number from 1 to 9 (got %r)." % text
    if not 1 <= number <= 9:
        return None, "%d is out of range; choose a cell from 1 to 9." % number
    index = number - 1
    if board[index] != EMPTY:
        return None, "Cell %d is already taken; pick an empty cell." % number
    return index, None


# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------

console = Console(highlight=False)


def say(*parts, style=None):
    """Print a line made of strings (rich markup) and Text objects."""
    line = Text()
    for part in parts:
        line.append(Text.from_markup(part) if isinstance(part, str) else part)
    console.print(line, style=style)


def show_board(board, last_move=None, win_line=None):
    console.print(board_table(board, last_move, win_line))


def ask(prompt):
    """Prompt with rich markup. Raises EOFError on EOF."""
    return console.input("[bold yellow]%s[/] " % prompt)


def ask_yes_no(prompt):
    """Prompt until the user answers y/yes or n/no. Raises EOFError on EOF."""
    while True:
        answer = ask(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        say("[red]Please answer 'y' or 'n'.[/]")


def ask_move(board):
    """Prompt the human until a valid move is entered; return its index."""
    while True:
        index, error = parse_move(ask("Your move (1-9):"), board)
        if error is None:
            return index
        say(Text(error, style="red"))


def play_game():
    """Play one full game. Returns the result (``"X"``, ``"O"`` or ``"draw"``)."""
    human_first = ask_yes_no("Do you want to go first? (y/n):")
    human = X if human_first else O
    computer = other(human)
    say("You are ", player_text(human), ", the computer is ",
        player_text(computer), ". ", player_text(X), " moves first.")
    console.print()

    board = new_board()
    turn = X
    last_computer_move = None
    while winner(board) is None:
        show_board(board, last_computer_move)
        if turn == human:
            move = ask_move(board)
        else:
            move = best_move(board, computer)
            last_computer_move = move
            say("Computer (", player_text(computer), ") plays [bold]%d[/]."
                % (move + 1))
        board = apply_move(board, move, turn)
        turn = other(turn)
        console.print()

    show_board(board, last_computer_move, winning_line(board))
    result = winner(board)
    if result == DRAW:
        say("[bold yellow]It's a draw![/]")
    elif result == human:
        say("[bold green]You win! (This should not happen...)[/]")
    else:
        say("[bold red]The computer wins![/]")
    return result


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
    console.print(Panel.fit(
        Text.assemble(
            ("Tic-tac-toe", "bold"), "\n",
            "you vs. the unbeatable computer"),
        border_style="bright_blue", box=box.DOUBLE, padding=(0, 4)))
    say("Cells are numbered like this "
        "(the computer's last move is highlighted):")
    show_board(new_board())
    console.print()
    try:
        while True:
            play_game()
            console.print()
            if not ask_yes_no("Play again? (y/n):"):
                break
            console.print()
    except (EOFError, KeyboardInterrupt):
        console.print()
    say("[bold]Goodbye![/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
