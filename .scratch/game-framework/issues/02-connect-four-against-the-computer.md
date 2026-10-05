# 02: Connect Four against the computer

**What to build:** `python3 -m games --game connect-four` lets a human play Connect Four against the computer, choosing whether to go first. The human drops discs by typing a column from 1 to 7 on a 7×6 board; Red moves first. The computer answers within about a second at its default depth. Duplicating code from tic-tac-toe (Game loop, Game events, Player I/O) is allowed here; ticket 03 removes the duplication.

**Blocked by:** 01 (Move tic-tac-toe into the package).

**Status:** resolved

- [x] Discs fall to the lowest empty row of the chosen column; four in a row horizontally, vertically or diagonally wins; a full board without one is a draw.
- [x] Input that isn't a number is re-prompted; out-of-range columns and full columns are Rejected moves with clear messages, and the human is asked again.
- [x] The board uses the heavy-lined grid style, with a column-number header, distinct colors for Red and Yellow, the computer's last Move highlighted, and the winning four on a green background.
- [x] The computer uses a depth-limited alpha-beta search with a heuristic that scores open windows of four, breaks ties deterministically, and takes about a second or less per Move at its default depth.
- [x] `--game tictactoe` and `--game connect-four` both work, and running with no `--game` still plays tic-tac-toe. An unknown name gives an error listing the valid names.
- [x] Tests: whole Connect Four Games played with a scripted Player I/O; the computer takes a win in one Move and blocks the opponent's win in one Move from set-up positions; renderer tests for the header, colors and highlights.
- [x] The tic-tac-toe golden transcript is unchanged.
- [x] `--help` and the README mention Connect Four and `--game`.
