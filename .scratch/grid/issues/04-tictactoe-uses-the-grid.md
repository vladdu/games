# 04: Tic-tac-toe uses the Grid

Status: resolved

**What to build:** tic-tac-toe stores its Cells from the bottom left with None for empty, and finds its Winning line through `Grid(3, 3, 3)`. Cells from the bottom left are in numeric keypad order, so a Cell's number is its index + 1. No visible behaviour changes.

**Blocked by:** 01.

- [x] `State.cells` runs from the bottom left (index 0 = Cell 1, index 8 = Cell 9); `last_move` is the point where the last mark landed.
- [x] `EMPTY`, `WIN_LINES`, `_find_line`, `cell_number` and `cell_index` are gone; Cell number = index + 1 in `parse_move`, `move_text`, `describe_move`, `rejection_message` and the guide numbers on the board. Out-of-range numbers are still reported as typed (e.g. "10 is out of range").
- [x] `result` and `board_table` use the Grid; the heuristic stays `0` and `unbeatable` is unchanged. `MOVE_ORDER` keeps legal Moves in the old top-row-first order, so the computer breaks ties as before and the golden transcripts stay byte-identical.
- [x] The `board_from` test helper and every test using raw indices or `EMPTY` are rewritten for the new layout. `board_from` sets `last_move` on boards that hold a Line, so `result` sees it.
- [x] All tests pass, and the tic-tac-toe and menu golden transcripts are byte-identical.
