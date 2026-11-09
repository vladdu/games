# Line Game types share a Grid module outside the Game type interface

Tic-tac-toe, Connect Four and Gomoku each wrote the same rule, a Line of N or more on a grid, in their own way: tic-tac-toe as 8 hard-coded lines, Connect Four as windows of four, Gomoku as a walk along each direction. Connect Four and Gomoku also had near-copies of the window heuristic. We chose one deep module, `games/grid.py`: a `Grid(width, height, n)` value that each of these Game types builds once and asks for the piece at a point, the cells after placing a piece, the Line through a point, and the window heuristic. All three store their board as a flat tuple from the bottom left, with None for an empty place, and record the point where the last piece landed.

The Grid stays out of the Game type interface. A Game type chooses to use it; the framework (the Game loop, the computer search, Player I/O) never depends on it. A Game type without Lines, or with a board that is not a grid, ignores it and keeps writing its own `result` and `heuristic`. Rendering, including highlighting the winning Line, stays in each Game type's `render`.

## Considered Options

- **Make the Grid part of `GameType`** (for example, the framework highlights the winning Line itself): would force every future Game type into the Line shape, so a game won by captures or territory could not join.
- **Free functions taking `(cells, width, height, n)` on every call**: the same four arguments at every call site, and nowhere to compute the windows through each point once.
- **Keep each Game type's own State and pass the Grid a "piece at (column, row)" function**: the Grid would call back into the Game type for every place it reads, so part of what it should own would stay outside it, and Connect Four's columns-of-tuples would remain a second board shape.
- **An option for "exactly N wins"**: no Game type needs it yet; add it when one does.
