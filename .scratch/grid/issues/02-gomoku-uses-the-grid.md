# 02: Gomoku uses the Grid

Status: ready-for-agent

**What to build:** Gomoku reads, places, finds its Winning five and scores positions through `Grid(9, 9, 5)`. It already stores bottom-up points with None, so its State doesn't change. No visible behaviour changes.

**Blocked by:** 01.

- [ ] `_find_five`, `windows`, `WINDOWS`, `index` and the counting loop in `heuristic` are gone; `result`, `apply_move`, `heuristic` and `board_table` use the Grid. `WINDOW_SCORES` stays as Gomoku's score table.
- [ ] `NEIGHBOURS`, `POINT_ORDER` and `search_moves` stay in Gomoku.
- [ ] Tests that used `stone_at` or `WINDOWS` use the Grid (or the Game type interface) instead. `test_heuristic_stays_well_inside_the_win_score` still bounds the score by the number of windows times the largest score.
- [ ] All tests pass, including the mid-game "about a second or less" timing test.
