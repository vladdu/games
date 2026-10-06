# 02: Gomoku between two humans

Status: ready-for-agent

**What to build:** `games/gomoku.py`, a Gomoku Game type as described in the spec (rules, typing Moves, rejections, rendering, registration). This ticket only needs to be playable hot-seat (`--game gomoku --first human --second human`). The heuristic can be the window scoring from the spec without tuning; the computer's search Moves and default Difficulty belong to ticket 03.

**Blocked by:** none.

- [ ] 9×9 board, Black first, alternating, any empty Point; five or more in a row, column or diagonal wins; a full board without one is a draw.
- [ ] Points are typed as a letter and a number (`e5`, `E5`, `e 5`); other text is re-prompted with "Please enter a point such as e5 (got '...')."; off-board and taken Points are Rejected moves with the messages in the spec.
- [ ] The board has letters a-i on the top and bottom and numbers 9 down to 1 on both sides, `●`/`○` stones in their styles, the most recent Move in reverse video and the Winning five on green.
- [ ] Registered third as `gomoku` / "Gomoku": in the startup menu, `--game`, `--help` and the README.
- [ ] The shared suite in `tests/test_game_types.py` passes for Gomoku; `TYPED` gains Point-shaped text (`e5`, `j3`, `a10`, `a0`, ...).
- [ ] Seam 1 tests: Rejected moves, unparseable text, a win in each direction, a win by six, a draw on a full board. Renderer tests as in the spec.
- [ ] The menu golden transcript is re-recorded with Gomoku as entry 3; the tic-tac-toe golden transcript is unchanged.
