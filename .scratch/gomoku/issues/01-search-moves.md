# 01: The computer searches a Game type's search Moves

Status: ready-for-agent

**What to build:** the optional `search_moves(state)` on the `GameType` protocol (ADR 0002). The shared search in `games/framework.py` considers `search_moves` where it now considers `legal_moves`, and falls back to `legal_moves` when a Game type doesn't define it. No visible behaviour changes.

**Blocked by:** none.

- [ ] `GameType` documents `search_moves`: the Moves the computer considers, in search order, a subset of the legal Moves; when it isn't defined, it is `legal_moves`.
- [ ] `best_move` and `_score` use it at every level of the search.
- [ ] Test (in `tests/test_computer_search.py`, using its toy Game type): a Game type whose `search_moves` leaves out the winning Move makes the computer play another Move, and without `search_moves` the computer finds the win.
- [ ] All existing tests and both golden transcripts pass unchanged.
