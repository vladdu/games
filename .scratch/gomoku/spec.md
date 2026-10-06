Status: resolved

# Spec: Gomoku on a 9×9 board

## Problem Statement

The program plays two Game types, Tic-tac-toe and Connect Four. Neither is a large-board placement game. Gomoku (five in a row) is a familiar game that fits the framework, two Sides with no hidden information and no chance, but it has up to 81 legal Moves per turn. The shared computer search (ADR 0001) cannot look usefully far ahead when it has to try all of them.

## Solution

Add Gomoku as the third Game type: a 9×9 board, Black and White, Black moving first, free placement with no opening restrictions, and five or more in a row winning (freestyle). The human names a Point such as `e5`. The framework gains one small extension (ADR 0002): a Game type may give the computer fewer Moves to search than are legal. Gomoku uses this to search only the empty Points next to a stone, so the computer answers in about a second.

## User Stories

1. As a player, I want Gomoku in the startup menu and as `--game gomoku`, so that I can play it like the other Game types.
2. As a Gomoku player, I want to place a stone by typing a Point such as `e5` (columns a-i from the left, rows 1-9 from the bottom), so that every Point is quick to name.
3. As a Gomoku player, I want `E5` and `e 5` to work too, so that case and spacing don't matter.
4. As a Gomoku player, I want text that isn't shaped like a Point to be re-prompted with an example, so that typos are harmless.
5. As a Gomoku player, I want a Point off the board or already taken to be a Rejected move with a clear message, after which I'm asked again, so that a slip doesn't cost me the Game.
6. As a Gomoku player, I want five or more of my stones in an unbroken row, column or diagonal to win, so that the game follows the freestyle rule.
7. As a Gomoku player, I want a full board with no Winning five to be a draw, so that every Game has a Result.
8. As a Gomoku player, I want Black to move first, so that the game follows the usual convention.
9. As a Gomoku player, I want column letters and row numbers on every edge of the board, so that I can name a Point without counting.
10. As a Gomoku player, I want Black and White stones to differ in shape as well as color, so that I can read the board on any terminal theme.
11. As a Gomoku player, I want the most recent Move and the Winning five highlighted, as in Connect Four, so that I can see what changed and how the Game was won.
12. As a Gomoku player, I want the computer to take a five when it can, and to block my five when I threaten one, so that it plays like a real opponent.
13. As a Gomoku player, I want each computer Move to take about a second or less at the default Difficulty, so that the Game doesn't drag.
14. As a developer, I want a Game type to be able to give the computer fewer Moves to search than are legal, without changing what "legal" means, so that large-board Game types can have a usable computer.

## Implementation Decisions

- **Vocabulary.** Point and Winning five are Gomoku terms in the glossary. Black and White are Gomoku's Sides.
- **Framework: search Moves** (ADR 0002). The `GameType` protocol gains an optional `search_moves(state)`: the Moves the computer considers, in search order. When a Game type doesn't define it, it is `legal_moves`. The shared search uses it everywhere it now uses `legal_moves`. Tic-tac-toe and Connect Four don't change. `legal_moves` and `move_problem` keep agreeing.
- **Gomoku rules.**
  - A 9×9 board. Black moves first, and Sides alternate.
  - A Move places the Side's stone on any empty Point.
  - Five or more in a row, column or diagonal wins (freestyle). A full board with no Winning five is a draw.
  - No opening restrictions: no renju forbidden moves, no swap.
- **Typing Moves.** Parsing only checks the shape: one letter followed by a whole number, case-insensitive, with spaces allowed. Text of any other shape gets "Please enter a point such as e5 (got 'xyz')." A parsed Move that is off the board (`j3`, `a10`, `a0`) or on a taken Point is rejected with a reason:
  - off the board: "j3 is off the board; columns are a-i and rows 1-9."
  - taken: "e5 is taken; pick an empty point."
  `move_text` gives the lower-case form, e.g. `e5`, and `describe_move` gives e.g. "point [bold]e5[/]".
- **Rendering.** A 9×9 grid in the heavy-lined style Connect Four uses. Column letters a-i run along the top and bottom, and row numbers 9 down to 1 run down both sides. Black is `●` (bold), White is `○` (bold bright_white). The most recent Move is shown in reverse video and the Winning five on a green background.
- **Computer.**
  - Search Moves: the empty Points within distance 1 (counting diagonals) of any stone, nearest to the centre first. On an empty board the only search Move is e5.
  - Heuristic: every window of five Points holding stones of only one Side counts for that Side, weighted `{1: 1, 2: 10, 3: 100, 4: 1000}`. It must stay well inside ±`WIN_SCORE / 2`.
  - Default Difficulty: the deepest depth that keeps a mid-game computer Move under about one second. Measure it during implementation; 3 or 4 is expected.
  - `unbeatable` is always False.
- **Registration.** `name = "gomoku"`, `title = "Gomoku"`, summary "Gomoku on a 9x9 board; enter a point such as e5, Black moves first". Third in the registry and the startup menu.

## Testing Decisions

The seams are the same as in the game-framework spec.

- **Seam 1 (playing a Game in-process):** whole Gomoku Games with a scripted Player I/O, covering Rejected moves (off the board, taken), unparseable text, a win along each direction, a win by a line of six, and a draw on a full board. From set-up positions, the computer takes a five in one Move and blocks the opponent's five-in-one (a four with one open end).
- **Seam 2 (the Game type interface):** the shared suite runs on Gomoku. Its `TYPED` sample texts must include Point-shaped text, such as `e5`, `j3`, `a10` and `a0`, so that Gomoku also has Moves that are refused. Renderer tests cover the edge labels, stone glyphs and styles, the most-recent-Move highlight and the Winning-five highlight. A framework test checks that the search only considers `search_moves` when a Game type defines it.
- **Seam 3 (the program as a process):** the menu golden transcript is re-recorded with Gomoku as entry 3. `--game gomoku` and `--help` mention Gomoku. The tic-tac-toe golden transcript stays byte-identical.

## Out of Scope

- Standard gomoku (exactly five), renju, swap openings and any other opening rule.
- Board sizes other than 9×9, or a configurable size.
- Pattern-based threat detection (open three, open four) in the heuristic, threat-space search, and opening books.

## Further Notes

- The design decisions came out of a grilling session and are recorded in the glossary (Gomoku section) and ADR 0002.
- The README lists Gomoku once it lands.
