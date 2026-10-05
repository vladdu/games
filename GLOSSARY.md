# Board games

A terminal game framework in which people play turn-based board games, starting with tic-tac-toe, against each other or against the computer.

## Language

### Framework

**Game type**:
A kind of game the framework can play, such as Tic-tac-toe or Connect Four. Each Game type has its own rules, its own way of drawing its board, and its own computer opponent.
_Avoid_: Game (on its own), ruleset, variant

**Game**:
One playthrough of a Game type, from the first move to the Result.
_Avoid_: Match, round, session

**Side**:
A place in a Game's turn order, such as first or second. Each Game type names its Sides: X and O in Tic-tac-toe, Red and Yellow in Connect Four.
_Avoid_: Player (for the place itself), color, mark, seat

**Player**:
Whoever plays a Side in a Game: a human or the computer.
_Avoid_: User, opponent, seat

**Move**:
One action by the Side to move, in whatever form the Game type defines. The Game type also decides which Side moves next, so turns need not strictly alternate.
_Avoid_: Turn, play

**Rejected move**:
A Move a human asked for that the Game refused because the Game type does not allow it.
_Avoid_: Invalid input, error

**Result**:
How a Game ended: one Side won, or it was a draw.
_Avoid_: Outcome, score

**Difficulty**:
How strong the computer plays, given as how many Moves ahead it looks.
_Avoid_: Level, skill

**Player I/O**:
Everything a Game needs from a human Player: their Moves, and being told what happened.
_Avoid_: UI, console, frontend

**Game event**:
Something the Game tells Player I/O has happened: the Game started, a Move was made, a Move was rejected, or the Game is over.
_Avoid_: Message, notification

### Tic-tac-toe

**Cell**:
One of the nine squares of the board, numbered 1-9 for the human in numeric keypad order: 7 8 9 on the top row, 1 2 3 on the bottom. A Tic-tac-toe Move places the Side's mark in an empty Cell. X always moves first.
_Avoid_: Square, position, slot

**Winning line**:
The three Cells in a row, column or diagonal that hold the winner's marks.
