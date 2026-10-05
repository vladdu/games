# 06: Choosing Players and Difficulty

**What to build:** Each Side can be played by a human or the computer, and the computer's Difficulty can be set. This allows hot-seat Games between two people at the same terminal, computer-vs-computer Games, and a weaker computer to play against. Intro and end-of-game messages read naturally for every pairing of Players.

**Blocked by:** 04 (One shared computer search).

**Status:** resolved

- [x] `--first human|computer` and `--second human|computer` choose the Player for each Side. Without them, the default is one human against the computer, decided by the "Do you want to go first?" prompt as today.
- [x] `--depth N` sets the computer's Difficulty, overriding the Game type's default.
- [x] With exactly one human Player, the intro and end messages keep today's wording ("You are X, the computer is O. X moves first.", "You win!", "The computer wins!", "It's a draw!"). "(This should not happen...)" is kept only for tic-tac-toe at full Difficulty.
- [x] Otherwise, the intro names the Player kind for each Side (for example "X: human, O: computer (depth 4)"), and the end message names the winning Side ("Red wins!").
- [x] "Play again" keeps the same Game type and Players.
- [x] Whole-Game tests cover hot-seat and computer-vs-computer Games; process-level tests cover the flags, invalid flag values and `--help`.
- [x] The tic-tac-toe golden transcript, run with default settings, is unchanged.
- [x] `--help` and the README describe the flags.
