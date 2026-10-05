Status: resolved

# Spec: a framework for turn-based board games

## Problem Statement

The program plays exactly one Game type: tic-tac-toe, one human against an unbeatable computer. Everything assumes it: a 9-Cell board, the X and O marks, the eight winning lines, keypad numbering, a full minimax search, and a fixed human-vs-computer setup in which the only choice is whether to go first. To play anything else (Connect Four, say) means copying the whole program and changing every part of it. The human also can't play against another person, watch the computer play itself, or make the computer weaker.

## Solution

The program becomes a framework for two-Sided, turn-based board games with no hidden information and no chance. Tic-tac-toe is one Game type in it, and Connect Four is the second. At startup the human picks a Game type from a menu, or names it on the command line. Each Side is played by a human or by the computer, and the computer's strength is set by a Difficulty. Tic-tac-toe looks and plays exactly as it does today, and the computer is still unbeatable at full Difficulty. Connect Four plays on a 7×6 board: the human drops discs by typing a column number, and the computer answers within about a second.

## User Stories

1. As a player, I want to choose which Game type to play from a menu at startup, so that I can play more than tic-tac-toe.
2. As a player, I want to name the Game type on the command line, so that I can skip the menu when I already know what I want.
3. As a player, I want `python3 tictactoe.py` to keep starting tic-tac-toe directly, so that my habits and scripts keep working.
4. As a player, I want to play Connect Four against the computer, so that I have a game where the computer is beatable and the game is longer.
5. As a player, I want to play tic-tac-toe exactly as before, with the same board, keypad numbering, colors, prompts and messages, so that the change costs me nothing.
6. As a player, I want the tic-tac-toe computer to stay unbeatable at full Difficulty, so that the game keeps its character.
7. As a player, I want to be asked whether I want to go first when I play against the computer, so that I can choose my Side the way I do today.
8. As a player, I want to play against another person at the same terminal (hot-seat), so that two people can play each other.
9. As a player, I want to watch the computer play itself, so that I can see how a Game type plays out or demo the program.
10. As a player, I want to set the computer's Difficulty, so that I can play a computer I can beat.
11. As a player, I want a sensible default Difficulty for each Game type, so that I don't need to know about search depth to start playing.
12. As a Connect Four player, I want to drop a disc by typing a column number from 1 to 7, so that a Move is one keystroke plus Enter.
13. As a Connect Four player, I want the column numbers shown above the board, so that I don't have to count columns.
14. As a Connect Four player, I want a Move into a full column to be rejected with a clear message and to be asked again, so that a slip doesn't cost me the Game.
15. As a Connect Four player, I want a column number outside 1-7, or input that isn't a number, to be rejected and to be asked again, so that typos are harmless.
16. As a Connect Four player, I want Red and Yellow shown in distinct colors, so that I can read the board at a glance.
17. As a Connect Four player, I want Red to move first, so that the game follows the usual convention.
18. As a Connect Four player, I want the four winning discs highlighted when someone wins, so that I can see how the Game was won.
19. As a Connect Four player, I want a full board with no four-in-a-row to end in a draw, so that every Game has a Result.
20. As a Connect Four player, I want the computer to take a win when one is available, so that it plays like a real opponent.
21. As a Connect Four player, I want the computer to block my win when I threaten one, so that it isn't trivially beaten.
22. As a Connect Four player, I want each computer Move to arrive in about a second or less at the default Difficulty, so that the Game doesn't drag.
23. As a player of any Game type, I want the most recent Move highlighted on the board, so that I can see what just changed, especially in hot-seat and computer-vs-computer Games.
24. As a player of any Game type, I want the board drawn before each human Move, so that I always decide from the current state.
25. As a player against the computer, I want the end-of-game message to address me ("You win!", "The computer wins!", "It's a draw!"), so that it reads naturally.
26. As a player in hot-seat or computer-vs-computer Games, I want the end-of-game message to name the winning Side ("Red wins!"), so that it is clear who won when "you" is ambiguous.
27. As a player, I want the opening line of each Game to say which Player plays each Side, so that I know who I am and who moves first.
28. As a player, I want "Play again" to start a new Game of the same Game type with the same Players, so that I can play several Games without reconfiguring.
29. As a player, I want Ctrl+C or Ctrl+D to quit at any point, in any Game type, so that I can always get out.
30. As a player, I want `--help` to describe the Game types, how to choose Players and how to set Difficulty, so that I can learn the options without reading code.
31. As a player, I want an unknown Game type name on the command line to give a clear error that lists the valid names, so that I can correct myself.
32. As a player scripting the program, I want every prompt to read from stdin, so that I can pipe a whole session through it.
33. As a developer, I want to add a new Game type by writing one module and adding it to one registry, so that the framework doesn't need to change for each Game type.
34. As a developer, I want a Game type to define its own Moves, Sides, rules, input parsing, rendering and heuristic score, so that games with different shapes (columns, cells, heaps) fit the same framework.
35. As a developer, I want the Game type to decide which Side moves next from the game state, so that games with passes or extra turns can be added later without changing the Game loop.
36. As a developer, I want one shared computer-opponent search for every Game type, so that each Game type only needs to supply a heuristic score.
37. As a developer, I want a shared test suite that every registered Game type must pass, so that a new Game type is checked against the framework's expectations automatically.
38. As a developer, I want to play whole Games in-process with scripted humans and real computers on each Side, so that I can test Game behaviour without a terminal.
39. As a developer, I want Game events to be the same for every Game type, so that Player I/O and tests don't depend on a particular Game type.
40. As a developer, I want the tic-tac-toe golden transcript to stay byte-identical through the refactor, so that I know the visible behaviour didn't change.
41. As a developer, I want the computer's choice of Move to be deterministic, so that tests and transcripts are reproducible.

## Implementation Decisions

- **Vocabulary.** The spec uses the terms in the project glossary: Game type, Game, Side, Player, Move, Rejected move, Result, Difficulty, Player I/O, Game event. Cell and Winning line are tic-tac-toe vocabulary, not framework terms.
- **Scope of Game types.** Two Sides, turns, no hidden information and no chance. Nim is used as a thought experiment when reviewing the framework interface (no grid, a Move made of two numbers, no marks), but it is not implemented.
- **Build order.** The framework is pulled out of two real Game types, not designed up front:
  1. Move tic-tac-toe into a package unchanged, with all existing tests and the golden transcript passing.
  2. Write Connect Four as its own module, allowing duplication.
  3. Pull out what the two have in common: the Game loop, Players, the computer's search, the Game type registry.
  4. Add the startup menu and the flags for Players and Difficulty.
- **Package layout.** A package containing a framework module, one module per Game type, and an entry point run as a module. The existing top-level tic-tac-toe script stays as a thin shortcut that starts the program with tic-tac-toe chosen and goes straight into the current tic-tac-toe intro, with no menu.
- **Game type interface.** Each Game type provides:
  - a name for the menu and the command line;
  - its Sides in turn order, with display names and styles (X/O; Red/Yellow);
  - the initial state;
  - which Side is to move in a state (worked out from the state; the Game never assumes strict alternation);
  - the legal Moves in a state;
  - why a Move is rejected in a state, or nothing if it is legal;
  - the state after a Move;
  - the Result of a state, or nothing if the Game is still in progress;
  - a heuristic score of a state from one Side's point of view, for the computer's search;
  - parsing a human's text into a Move, or an error message;
  - the message for each rejection reason;
  - a terminal renderer of a state, which works out what to highlight from the state: the most recent Move, and the winning line when there is one;
  - a default Difficulty.
  States are immutable values, and Moves are values only the Game type looks inside.
- **Player.** Each Side is filled by a Player, which is asked for a Move given the state. There are two kinds of Player:
  - **Human:** asks Player I/O for text, has the Game type parse it, and re-asks on parse errors.
  - **Computer:** runs the shared search at its Difficulty.
- **Game loop.** It plays one Game of a Game type with one Player per Side and returns the Result. Each turn it asks the Side to move for a Move. If the Move is rejected, it emits a Move-rejected Game event and asks again. Otherwise it applies the Move and emits a Moved Game event. At the end it emits Game over.
- **Game events.** These are the same for every Game type:
  - **Started:** which kind of Player plays each Side.
  - **Moved:** the Side, the Move and the new state.
  - **Move rejected:** the Move and the reason.
  - **Game over:** the Result and the final state.
  Compared with today, Moved no longer carries the computer's last Move, and Game over no longer carries the winning line; the renderer works both out from the state.
- **Player I/O.** It becomes what the Game needs from human Players: asking for text and showing Game events. Choosing who goes first moves out of Player I/O into session setup.
- **Computer opponent** (ADR 0001):
  - One shared depth-limited alpha-beta search; Difficulty is the search depth.
  - The search uses depth-aware scores, so faster wins and slower losses are preferred, and it uses the Game type's heuristic where it stops before the end of the Game.
  - Ties are broken deterministically.
  - Tic-tac-toe's Difficulty is unlimited depth, so the computer stays unbeatable. Being unbeatable is a property of tic-tac-toe at full Difficulty, not a framework promise.
- **Highlighting.** The most recent Move is highlighted whichever Side made it, replacing "the computer's last Move". This matches today's display before every human prompt. It only differs on the final board, when the human made the last Move.
- **Messages.**
  - **With exactly one human Player:**
    - The intro line is "You are X, the computer is O. X moves first."
    - The end messages are "You win!", "The computer wins!" and "It's a draw!".
    - The "(This should not happen...)" suffix is kept only for tic-tac-toe at full Difficulty.
  - **Otherwise:** the intro line names the Player kind for each Side (for example "X: human, O: computer (depth 4)"), and the end message names the winning Side.
- **Session setup.**
  - Choosing the Game type: a menu at startup, or `--game NAME`.
  - Choosing Players: `--first human|computer` and `--second human|computer`. The default is one human against the computer, decided by the familiar "Do you want to go first?" prompt.
  - Choosing Difficulty: `--depth N`, which overrides the Game type's default.
  - "Play again" reuses the Game type and Players.
- **Connect Four rules.**
  - A 7×6 board, with discs falling to the lowest empty row of the chosen column.
  - Red moves first.
  - A Move is a column from 1 to 7 typed by the human.
  - Rejection reasons: out of range, and column full.
  - Four in a row horizontally, vertically or diagonally wins. A full board without one is a draw.
  - The heuristic scores open windows of four, and the default depth keeps a computer Move under about one second.
  - The rendering uses the same heavy-lined grid style as tic-tac-toe, with a column-number header, distinct colors for Red and Yellow, the most recent Move highlighted, and the winning four on a green background.

## Testing Decisions

- **What makes a good test.** It exercises behaviour through the highest seam available and asserts what can be observed there: Game events, Results, rendered output and the program's output. It does not assert helper functions or internal data shapes, so the internals can be refactored freely.
- **Seam 1: playing a Game in-process.** Play a Game of a given Game type with a scripted human (a Player I/O fed with text) and/or the computer on each Side, then check the Game events and the Result. Prior art: the existing whole-Game tests with a scripted Player I/O adapter. This covers:
  - Rejected moves and being asked again;
  - Results;
  - hot-seat and computer-vs-computer Games;
  - quitting propagating out of the Game;
  - Connect Four tactics: from a set-up position, the computer takes a win in one Move and blocks the opponent's win in one Move.
- **Seam 2: the Game type interface.**
  - A shared test suite runs against every registered Game type:
    - random playouts always end with a Result;
    - every legal Move is accepted and gives a state where the other Side, or whoever the Game type says, is to move;
    - every Move from the Game type's rejection set is refused with a reason;
    - a Move typed as text is parsed back to the same Move;
    - the Side to move is always one of the Game type's Sides.
  - Per-Game-type tests also run here:
    - Tic-tac-toe keeps its exhaustive "the computer never loses, playing first or second" test. Prior art: the existing never-loses tests.
    - Renderer tests check grid lines, mark styles, guide numbers or column headers, the most-recent-Move highlight and the winning-line highlight. Prior art: the existing rendering tests, which render to a recording console and inspect styles.
  - The existing tests of tic-tac-toe helpers (winner, Side to move, Cell numbering, parsing) move up to this seam or seam 1.
- **Seam 3: the program as a process.** Pipe a scripted session through the real program and compare its output.
  - The tic-tac-toe golden transcript, run through the existing top-level script, must stay byte-identical through steps 1-3 of the build order. Prior art: the existing golden-transcript test.
  - New process-level tests cover the startup menu, `--game` (including an unknown name), the Player flags, `--depth`, and `--help`.
  - Any deliberate re-recording of transcripts happens only after the startup menu exists.

## Out of Scope

- More than two Sides, hidden information (card games) and chance (dice).
- Implementing Nim, Othello, Gomoku, checkers, chess or any Game type other than tic-tac-toe and Connect Four.
- Front ends other than the terminal (web, GUI), and a front-end-neutral rendering abstraction.
- Plugin discovery or loading Game types from outside the project.
- Monte Carlo tree search, opening books, time-limited search and per-Game-type hand-written AIs.
- Saving and loading Games, undo, Move history and network play.

## Further Notes

- The design decisions came out of a grilling session and are recorded in the project glossary and ADR 0001 (shared alpha-beta opponent).
- Being unbeatable at tic-tac-toe depends on the shared search reaching the end of every Game when given unlimited depth. The exhaustive never-loses test is the guard for this.
- The README and the glossary's tic-tac-toe section need updating once Connect Four and the menu land.
