# 03: Gomoku against the computer

Status: ready-for-agent

**What to build:** a usable Gomoku computer. Gomoku defines `search_moves` (the empty Points within distance 1 of any stone, nearest to the centre first, or just e5 on an empty board), the window-of-five heuristic weighted `{1: 1, 2: 10, 3: 100, 4: 1000}`, and a measured default Difficulty.

**Blocked by:** 01 (search Moves), 02 (Gomoku between two humans).

- [ ] `search_moves` as above, deterministic in order.
- [ ] The heuristic stays well inside ±`WIN_SCORE / 2` on any reachable board.
- [ ] Default Difficulty is the deepest depth that keeps a mid-game computer Move under about one second; record the measurement in the ticket's Comments.
- [ ] `unbeatable` is always False, so the intro says "you vs. the computer".
- [ ] Tests: from set-up positions, the computer completes a five in one Move and blocks the opponent's five-in-one (a four with one open end); a whole computer-vs-computer Game ends with a Result.
