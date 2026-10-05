"""Helpers shared by the tests: a scripted Player I/O for whole Games
in-process, and running the program as a process."""

import os
import subprocess
import sys

from games.framework import GameOver, Moved, Started

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScriptedIO:
    """Player I/O for scripted humans: answers each Move prompt with the
    next of ``texts`` and records every Game event and parse error. When
    the texts run out it raises EOFError, like a terminal at end of input,
    or, given ``game_type``, plays the first legal Move instead."""

    def __init__(self, texts=(), game_type=None):
        self.texts = list(texts)
        self.game_type = game_type
        self.events = []
        self.prompts = []
        self.parse_errors = []
        self.state = None

    def ask_move(self, side):
        self.prompts.append(side)
        if self.texts:
            return self.texts.pop(0)
        if self.game_type is None:
            raise EOFError
        move = self.game_type.legal_moves(self.state)[0]
        return self.game_type.move_text(move)

    def show_parse_error(self, message):
        self.parse_errors.append(message)

    def show(self, event):
        self.events.append(event)
        if isinstance(event, (Started, Moved, GameOver)):
            self.state = event.state

    def of_type(self, kind):
        return [e for e in self.events if isinstance(e, kind)]


# Two tic-tac-toe Games: the human goes first (with every kind of bad input)
# and draws, then goes second and loses. golden_transcript.txt was first
# recorded before the Game / Terminal I/O split, and re-recorded when cells
# were renumbered in keypad order.
GOLDEN_INPUT = "\n".join(["y", "abc", "10", "5", "5", "8", "4", "3", "1",
                          "maybe", "y", "n", "8", "9", "n"]) + "\n"


def run_program(command, *args, input=""):
    """Run ``command`` (a list) from the project root with plain output."""
    env = dict(os.environ, NO_COLOR="1", COLUMNS="80",
               PYTHONIOENCODING="utf-8")
    env.pop("FORCE_COLOR", None)
    return subprocess.run([sys.executable] + command + list(args),
                          input=input, capture_output=True, text=True,
                          encoding="utf-8", env=env, cwd=ROOT, timeout=30)


def golden_transcript():
    with open(os.path.join(ROOT, "golden_transcript.txt"),
              encoding="utf-8") as f:
        return f.read()
