Status: ready-for-agent

# Spec: One Grid module for the Line Game types

## Problem Statement

Tic-tac-toe, Connect Four and Gomoku are all won by a Line: N or more pieces of one Side in an unbroken row, column or diagonal. Each Game type writes that rule its own way (`WIN_LINES` and `_find_line`, `WINDOWS` and `_find_four`, a direction walk in `_find_five`), and Connect Four and Gomoku keep near-copies of the window heuristic. Changing the rule means changing it in several places: the recent "check for a win only through the most recent Move" speed-up had to be written twice. Each Game type also stores its board differently (top-down cells, columns of discs, bottom-up points).

## Solution

Add one deep module, `games/grid.py`, and have all three Game types use it (ADR 0003). A `Grid(width, height, n)` is built once per Game type. It works out the windows of N, and the windows through each point, once. Its operations take the cells and return answers; it never stores the cells. The three Game types store their board as a flat tuple from the bottom left, with None for an empty place, and record the point where the last piece landed. Nothing changes for the person playing, except that a Connect Four Line of five or more is highlighted in full.

## User Stories

1. As a developer, I want the Line rule written once, so that a fix or speed-up to it reaches every Line Game type.
2. As a developer, I want the window heuristic counted once, with each Game type supplying only its score table, so that Connect Four and Gomoku can't drift apart.
3. As a developer, I want the three Game types to store their boards the same way, so that I can read any of them without learning a new representation.
4. As a developer adding a Line Game type, I want to describe it by its width, height and N, and get the win check and heuristic for free.
5. As a developer adding a Game type without Lines, I want to ignore the Grid entirely, so that it doesn't constrain my design.
6. As a Connect Four player, I want a Line of five or more highlighted in full, so that I see the whole Winning four.
7. As a player of any Game type, I want everything else (Moves, messages, boards, the computer's strength and speed) unchanged.

## Implementation Decisions

- **Vocabulary.** Line is a new Framework term in the glossary. Winning four is now "four or more". Winning line, Winning four and Winning five stay as the game-specific names.
- **The Grid stays out of the Game type interface** (ADR 0003). `GameType` in `games/framework.py` does not change, and the framework never imports `games/grid.py`.
- **`Grid(width, height, n)`**: an immutable value, built once per Game type at module load. It computes once:
  - the windows of `n` points in each of the four directions
  - the windows through each point
- **Cells**: a flat tuple of `width * height` places, row by row from the bottom left, so point `(column, row)` is index `row * width + column`. An empty place is `None`.
- **Operations** (names to be fixed in ticket 01). Each takes the cells:
  - the piece at a point
  - the cells after placing a piece at a point
  - the Line through a point: the whole unbroken run of `n` or more of that point's Side in any direction, as a tuple of points from one end; `None` if there isn't one, or if the point is empty
  - the window heuristic for a Side, given a score table `{count: score}`: each window holding only that Side's pieces adds `table[count]`, each holding only the other Side's subtracts it, and mixed or empty windows count 0
- **Win rule**: N or more wins. There is no option for "exactly N".
- **`last_move`**: every State records the point where the last piece landed (None at the start). `result` asks the Grid for the Line through `last_move`. A State with a Line but no `last_move` has no Result, which holds for every State built by `apply_move`.
- **Per Game type**:
  - **Gomoku**: `Grid(9, 9, 5)`. It already stores bottom-up points with None. `NEIGHBOURS` and `search_moves` stay in Gomoku (one caller).
  - **Connect Four**: `Grid(7, 6, 4)`. The State becomes flat cells plus a point `last_move`. A Move is still a column; the landing row is the lowest empty place in that column. A column is full when its top place is taken.
  - **Tic-tac-toe**: `Grid(3, 3, 3)`. Cells run from the bottom left, which is numeric keypad order, so a Cell's number is its index + 1. `cell_number` and `cell_index` and their row flip are deleted. `EMPTY = " "` is replaced by None. The heuristic stays `0`.
- **Rendering** stays in each Game type's `render`. It reads pieces through the Grid and highlights the Line through `last_move`.

## Testing Decisions

- **The Grid's interface** (new `tests/test_grid.py`): a Line in each of the four directions; a Line longer than N; a Line along the edge of a rectangular (non-square) grid; no Line through a point that isn't part of one, or through an empty point; placing a piece leaves the original cells unchanged; the heuristic on a small grid, including mixed windows scoring 0.
- **The Game type interface** (`tests/test_game_types.py` and each Game type's suite): kept. They don't reach into the private `_find_*` helpers, so they check that the switch-over keeps behaviour. Tests that use a removed public helper (`disc_at`, `stone_at`, `WINDOWS`) switch to the Grid.
- **Rewritten**: tic-tac-toe tests that use raw top-down indices or `EMPTY`, and the `board_from` helper (it must set `last_move` on boards with a Line, or `result` won't see the Line). Any Connect Four test that checks `last_move` as a column.
- **The program as a process**: the tic-tac-toe and menu golden transcripts stay byte-identical.
- **Speed**: `test_a_mid_game_move_takes_about_a_second_or_less` (Gomoku) still passes, and Connect Four at depth 6 is no slower than before.

## Out of Scope

- Moving Gomoku's `NEIGHBOURS` into the Grid.
- Any change to `GameType`, the Game loop, the computer search or Player I/O.
- Board sizes, Ns or Game types beyond the three that exist.
- "Exactly N" wins, renju or other overline rules.

## Further Notes

- The design came out of an architecture review and a grilling session, and is recorded in ADR 0003 and the glossary (Line).
- Tickets 02-04 are each blocked only by 01, but they touch shared test helpers, so implement them one at a time in order.
