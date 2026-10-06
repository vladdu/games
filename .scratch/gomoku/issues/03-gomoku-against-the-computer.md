# 03: Gomoku against the computer

Status: ready-for-agent

**What to build:** a usable Gomoku computer. Gomoku defines `search_moves` (the empty Points within distance 1 of any stone, nearest to the centre first, or just e5 on an empty board), the window-of-five heuristic weighted `{1: 1, 2: 10, 3: 100, 4: 1000}`, and a measured default Difficulty.

**Blocked by:** 01 (search Moves), 02 (Gomoku between two humans).

- [ ] `search_moves` as above, deterministic in order.
- [ ] The heuristic stays well inside ±`WIN_SCORE / 2` on any reachable board.
- [ ] Default Difficulty is the deepest depth that keeps a mid-game computer Move under about one second; record the measurement in the ticket's Comments.
- [ ] `unbeatable` is always False, so the intro says "you vs. the computer".
- [ ] Tests: from set-up positions, the computer completes a five in one Move and blocks the opponent's five-in-one (a four with one open end); a whole computer-vs-computer Game ends with a Result.

## Comments

**Default Difficulty measurement (implementation).** Timed `best_move` on a
computer-vs-computer Game, one line per Move as `stones on the board:
seconds` (WSL2, CPython via `uv run`):

- Depth 3, whole Game (White won after 20 stones): 0:0.00 1:0.02 2:0.02
  3:0.03 4:0.04 5:0.07 6:0.20 7:0.31 8:0.10 9:0.31 10:0.13 11:0.27 12:1.14
  13:0.66 14:0.38 15:0.81 16:0.35 17:0.20 18:1.37 19:0.17. Mid-game Moves
  take 0.1-1.4 s, about 0.5 s on average.
- Depth 3 on positions at 8, 12, 16, 20, 24 and 28 stones from a depth-2
  Game: 0.11, 0.19, 0.41, 0.51, 0.91, 1.23 s.
- Depth 4, same opening: 0:0.02 ... 9:0.66 10:0.36 11:2.71 12:2.24
  13:8.10 (stopped there): several seconds a Move by the tenth Move.
- Depth 2: at most 0.04 s.

So the default Difficulty is 3. The test suite's mid-game timing position
(`MID_GAME` in `tests/test_gomoku.py`, 20 stones) takes about 0.64 s at
depth 3; the test allows 1.5 s so it isn't flaky on a slow machine.
