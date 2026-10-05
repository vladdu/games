# 03: Both Game types play through one Game loop

**What to build:** Tic-tac-toe and Connect Four play through one shared Game loop, behind a Game type interface. The behaviour players see is unchanged, except that the board now highlights the most recent Move, whichever Side made it. Each Game type still uses its own computer search for now; ticket 04 replaces them.

**Blocked by:** 02 (Connect Four against the computer).

**Status:** resolved

- [x] A Game type interface, as described in the spec: name, Sides with display names and styles, initial state, Side to move (worked out from the state), legal Moves, rejection reason, state after a Move, Result, heuristic score, parsing typed text into a Move, rejection messages, terminal renderer, default Difficulty.
- [x] A Game type registry; `--game` and its error message use it.
- [x] Human and Computer Players fill the Sides. The Game loop asks the Side to move for a Move, emits Move rejected and asks again for a Rejected move, and emits Moved, then Game over.
- [x] Game events are the same for every Game type: Started (which kind of Player plays each Side), Moved (Side, Move, new state), Move rejected (Move, reason), Game over (Result, final state). Moved no longer carries the computer's last Move, and Game over no longer carries the winning line.
- [x] Player I/O only asks for text and shows Game events. Asking "Do you want to go first?" moves to session setup.
- [x] Renderers work out the most-recent-Move and winning-line highlights from the state.
- [x] A shared test suite runs against every registered Game type: random playouts end with a Result; legal Moves are accepted; Rejected moves are refused with a reason; typed Moves are parsed back to the same Move; the Side to move is always one of the Game type's Sides.
- [x] The tests of tic-tac-toe helpers move up to the Game type interface or to whole-Game tests.
- [x] The tic-tac-toe golden transcript is byte-identical, and all tests pass.
