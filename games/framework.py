"""What every Game type shares: the Game loop, Players, Game events, the
terminal Player I/O and the session around Games.

A Game type is an object with the ``GameType`` interface. States are
immutable values and Moves are values only the Game type looks inside; the
framework only passes them back to the Game type.

``play_game`` plays one Game with one Player per Side and reports what
happens as Game events to a Player I/O. ``TerminalIO`` is the Player I/O for
a human at a terminal, and ``run`` is a whole terminal session of one Game
type (choosing who goes first, playing again).
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol

from rich.console import Console
from rich.text import Text

DRAW = "draw"


class GameType(Protocol):
    """What the framework needs from a Game type."""

    name: str            # for the command line, e.g. "connect-four"
    title: str           # for people, e.g. "Connect Four"
    sides: tuple         # the Sides in turn order, by display name
    default_depth: Optional[int]  # default Difficulty; None is unlimited

    def side_style(self, side) -> str:
        """The rich style the Side is shown in."""

    def initial_state(self):
        """The state a Game starts from."""

    def to_move(self, state):
        """The Side to move in a state that has no Result yet."""

    def legal_moves(self, state) -> list:
        """The legal Moves, or [] once the Game has a Result. The computer
        searches them in this order and, among equally good Moves, plays
        the first, so put the likeliest good Moves first."""

    def move_problem(self, state, move) -> Optional[str]:
        """Why ``move`` is rejected in ``state``, or None if it is legal."""

    def apply_move(self, state, move):
        """The state after ``move``; ValueError if it is not legal."""

    def result(self, state):
        """A Side for a win, DRAW, or None while the Game is in progress."""

    def heuristic(self, state, side) -> float:
        """Score of a state in progress from ``side``'s point of view, for
        the computer's search where it stops before the end of the Game.
        It must stay well inside +/- ``WIN_SCORE / 2``."""

    def unbeatable(self, depth) -> bool:
        """True if the computer cannot lose at Difficulty ``depth``."""

    def parse_move(self, text) -> tuple:
        """``(move, None)`` or ``(None, error message)``. The Move is not
        checked against any state."""

    def move_text(self, move) -> str:
        """The text a human types for ``move`` (``parse_move``'s inverse)."""

    def describe_move(self, move) -> str:
        """Rich markup naming a Move, e.g. "column [bold]4[/]"."""

    def rejection_message(self, move, reason) -> str:
        """The message telling the human why ``move`` was rejected."""

    def move_prompt(self) -> str:
        """The prompt for a human's Move, e.g. "Your move (1-7):"."""

    def render(self, state):
        """A rich renderable of the board, highlighting the most recent Move
        and the winning line, both worked out from the state."""

    def intro(self) -> list:
        """Rich renderables shown once when a session starts."""


# --------------------------------------------------------------------------
# Game events
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Started:
    """The Game has started from ``state``; ``players`` holds the Player
    playing each Side, in the Game type's Side order."""
    players: tuple
    state: Any


@dataclass(frozen=True)
class Moved:
    """``side`` made ``move``, giving ``state``."""
    side: Any
    move: Any
    state: Any


@dataclass(frozen=True)
class MoveRejected:
    """``move`` was refused for ``reason``; the Side will be asked again."""
    move: Any
    reason: str


@dataclass(frozen=True)
class GameOver:
    """The Game ended with ``result`` (a Side or DRAW) on ``state``."""
    result: Any
    state: Any


# --------------------------------------------------------------------------
# Players
# --------------------------------------------------------------------------

class PlayerIO(Protocol):
    """Everything a Game needs from human Players. Methods may raise
    EOFError or KeyboardInterrupt to quit; the Game lets them propagate."""

    def ask_move(self, side) -> str:
        """Return the text the human playing ``side`` typed for a Move."""

    def show_parse_error(self, message) -> None:
        """Tell the human their text could not be read as a Move."""

    def show(self, event) -> None:
        """Tell the humans about a Game event."""


@dataclass(frozen=True)
class Human:
    """A human Player: types Moves through the Player I/O, and is asked
    again while the text is not a Move."""
    kind = "human"

    def choose_move(self, game_type, state, io):
        side = game_type.to_move(state)
        while True:
            move, error = game_type.parse_move(io.ask_move(side))
            if error is None:
                return move
            io.show_parse_error(error)


@dataclass(frozen=True)
class Computer:
    """The computer, looking ``depth`` Moves ahead (None: unlimited)."""
    depth: Optional[int] = None
    kind = "computer"

    def choose_move(self, game_type, state, io):
        return best_move(game_type, state, self.depth)


# --------------------------------------------------------------------------
# The computer's search (ADR 0001)
# --------------------------------------------------------------------------

# A win ``ply`` Moves from now scores WIN_SCORE - ply and a loss
# ply - WIN_SCORE, so faster wins and slower losses score higher.
WIN_SCORE = 1_000_000
_INFINITY = 2 * WIN_SCORE


def best_move(game_type, state, depth=None):
    """The Move the Side to move in ``state`` should make, looking ``depth``
    Moves ahead (None: to the end of the Game), or None if the Game is
    over. Depth-limited alpha-beta search; among equally good Moves the
    first in ``legal_moves`` order is chosen, so the choice is
    deterministic."""
    if game_type.result(state) is not None:
        return None
    me = game_type.to_move(state)
    choice = None
    alpha = -_INFINITY
    for move in game_type.legal_moves(state):
        score = _score(game_type, game_type.apply_move(state, move), me,
                       None if depth is None else depth - 1, 1,
                       alpha, _INFINITY)
        if choice is None or score > alpha:
            # A later Move scoring no better than alpha may return a bound
            # rather than its exact score, but never one above alpha.
            choice, alpha = move, max(alpha, score)
    return choice


def _score(game_type, state, me, depth, ply, alpha, beta):
    """Alpha-beta score of ``state`` from ``me``'s point of view, ``ply``
    Moves from the root and looking ``depth`` more Moves ahead (None:
    unlimited)."""
    outcome = game_type.result(state)
    if outcome is not None:
        if outcome == DRAW:
            return 0
        return WIN_SCORE - ply if outcome == me else ply - WIN_SCORE
    if depth == 0:
        return game_type.heuristic(state, me)

    maximizing = game_type.to_move(state) == me
    best = -_INFINITY if maximizing else _INFINITY
    next_depth = None if depth is None else depth - 1
    for move in game_type.legal_moves(state):
        score = _score(game_type, game_type.apply_move(state, move), me,
                       next_depth, ply + 1, alpha, beta)
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


# --------------------------------------------------------------------------
# The Game loop
# --------------------------------------------------------------------------

def play_game(game_type, players, io, start=None):
    """Play one Game of ``game_type`` with ``players`` (one per Side, in
    Side order) from ``start`` (the initial state by default), reporting
    Game events to ``io``. Returns the Result."""
    players = tuple(players)
    by_side = dict(zip(game_type.sides, players))
    state = start if start is not None else game_type.initial_state()
    io.show(Started(players, state))
    while game_type.result(state) is None:
        side = game_type.to_move(state)
        while True:
            move = by_side[side].choose_move(game_type, state, io)
            reason = game_type.move_problem(state, move)
            if reason is None:
                break
            io.show(MoveRejected(move, reason))
        state = game_type.apply_move(state, move)
        io.show(Moved(side, move, state))
    outcome = game_type.result(state)
    io.show(GameOver(outcome, state))
    return outcome


# --------------------------------------------------------------------------
# Terminal Player I/O
# --------------------------------------------------------------------------

class TerminalIO:
    """Player I/O for a human at a terminal, drawn with rich.

    The board is shown before every turn: it is drawn lazily, just before
    the next prompt or computer Move, so the final board is drawn only once,
    with its winning line.
    """

    def __init__(self, game_type, console):
        self.game_type = game_type
        self.console = console
        self._players = {}
        self._pending_state = None

    def side_text(self, side):
        return Text(side, style=self.game_type.side_style(side))

    def say(self, *parts, style=None):
        """Print a line made of strings (rich markup) and Text objects."""
        line = Text()
        for part in parts:
            line.append(Text.from_markup(part) if isinstance(part, str)
                        else part)
        self.console.print(line, style=style)

    def ask(self, prompt):
        """Prompt with rich markup. Raises EOFError on EOF."""
        return self.console.input("[bold yellow]%s[/] " % prompt)

    def ask_yes_no(self, prompt):
        """Prompt until the user answers y/yes or n/no."""
        while True:
            answer = self.ask(prompt).strip().lower()
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False
            self.say("[red]Please answer 'y' or 'n'.[/]")

    # Player I/O

    def ask_move(self, side):
        self._draw_pending_board()
        return self.ask(self.game_type.move_prompt())

    def show_parse_error(self, message):
        self.say(Text(message, style="red"))

    def show(self, event):
        game_type = self.game_type
        if isinstance(event, Started):
            self._players = dict(zip(game_type.sides, event.players))
            self.say("You are ", self.side_text(self._side_of(Human)),
                     ", the computer is ",
                     self.side_text(self._side_of(Computer)), ". ",
                     self.side_text(game_type.sides[0]), " moves first.")
            self.console.print()
            self._pending_state = event.state
        elif isinstance(event, Moved):
            self._draw_pending_board()
            if isinstance(self._players[event.side], Computer):
                self.say("Computer (", self.side_text(event.side),
                         ") plays %s." % game_type.describe_move(event.move))
            self.console.print()
            self._pending_state = event.state
        elif isinstance(event, MoveRejected):
            self.say(Text(game_type.rejection_message(event.move,
                                                      event.reason),
                          style="red"))
        elif isinstance(event, GameOver):
            self._pending_state = None
            self.console.print(game_type.render(event.state))
            if event.result == DRAW:
                self.say("[bold yellow]It's a draw![/]")
            elif isinstance(self._players[event.result], Human):
                computer = self._players[self._side_of(Computer)]
                suffix = (" (This should not happen...)"
                          if game_type.unbeatable(computer.depth) else "")
                self.say("[bold green]You win!%s[/]" % suffix)
            else:
                self.say("[bold red]The computer wins![/]")

    def _side_of(self, kind):
        """The one Side played by a Player of ``kind``."""
        (side,) = [s for s, p in self._players.items() if isinstance(p, kind)]
        return side

    def _draw_pending_board(self):
        if self._pending_state is not None:
            self.console.print(self.game_type.render(self._pending_state))
            self._pending_state = None


# --------------------------------------------------------------------------
# Session
# --------------------------------------------------------------------------

def choose_players(game_type, io):
    """Session setup: one human against the computer at the Game type's
    default Difficulty, the human choosing whether to go first."""
    computer = Computer(game_type.default_depth)
    if io.ask_yes_no("Do you want to go first? (y/n):"):
        return (Human(), computer)
    return (computer, Human())


def run(game_type, console=None):
    """Play Games of ``game_type`` at the terminal until the human stops."""
    io = TerminalIO(game_type, console or Console(highlight=False))
    for renderable in game_type.intro():
        io.console.print(renderable)
    io.console.print()
    try:
        while True:
            play_game(game_type, choose_players(game_type, io), io)
            io.console.print()
            if not io.ask_yes_no("Play again? (y/n):"):
                break
            io.console.print()
    except (EOFError, KeyboardInterrupt):
        io.console.print()
    io.say("[bold]Goodbye![/]")
    return 0
