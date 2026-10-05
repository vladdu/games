# Tic-tac-toe

A terminal game in which a human plays tic-tac-toe against an unbeatable computer.

## Language

**Game**:
One game of tic-tac-toe between the human and the computer, from the first move to the Result.
_Avoid_: Match, round, session

**Cell**:
One of the nine squares of the board, numbered 1-9 for the human, left to right and top to bottom.
_Avoid_: Square, position, slot

**Move**:
A player placing their mark in an empty Cell. X always moves first.
_Avoid_: Turn, play

**Rejected move**:
A Move the human asked for that the Game refused, because the Cell is taken or does not exist.
_Avoid_: Invalid input, error

**Result**:
How a Game ended: X won, O won, or a draw.
_Avoid_: Outcome, score

**Winning line**:
The three Cells in a row, column or diagonal that hold the winner's marks.

**Player I/O**:
Everything the Game needs from the human's side: whether they go first, their Moves, and being told what happened.
_Avoid_: UI, console, frontend

**Game event**:
Something the Game tells Player I/O has happened: the Game started, a Move was made, a Move was rejected, or the Game is over.
_Avoid_: Message, notification
