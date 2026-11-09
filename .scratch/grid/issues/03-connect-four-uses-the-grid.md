# 03: Connect Four uses the Grid

Status: resolved

**What to build:** Connect Four stores flat bottom-left cells and the point where the last disc landed, and reads, places, finds its Winning four and scores positions through `Grid(7, 6, 4)`. A Move is still a column 0-6, typed 1-7. The only visible change: a Line of five or more discs is highlighted in full.

**Blocked by:** 01.

- [x] `State` holds `cells` (42 places, None = empty) and `last_move`, a point `(column, row)` or None.
- [x] The landing row is the lowest empty place in the column; a column is full when its top place is taken. `move_problem`, `legal_moves` (centre first) and the Rejected move messages are unchanged.
- [x] `_find_four`, `windows`, `WINDOWS`, `WINDOWS_THROUGH`, `disc_at` and the counting loop in `heuristic` are gone; `result`, `apply_move`, `heuristic` and `board_table` use the Grid. `WINDOW_SCORES` stays as Connect Four's score table.
- [x] The most-recent-Move highlight uses the `last_move` point.
- [x] Tests that used `disc_at` or checked `last_move` as a column are updated. A new render test: a Line of five Red discs is all on green.
- [x] All tests pass, and a depth-6 computer Move is no slower than before.
