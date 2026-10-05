# 01: Move tic-tac-toe into the package

**What to build:** Running the program as a module (`python3 -m games`) plays tic-tac-toe exactly as today, and `python3 tictactoe.py` keeps working as a thin shortcut to it. Only the code and its tests move; behaviour doesn't change. This prepares the ground for adding further Game types (see the spec, `.scratch/game-framework/spec.md`).

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] A package exists with a framework module (empty or near-empty for now), a tic-tac-toe module holding today's rules, renderer, Player I/O and Game loop, and a module entry point.
- [x] `python3 -m games` plays tic-tac-toe with the same intro, prompts, board and messages as today.
- [x] `python3 tictactoe.py` (including `--help`) still works, starting the same program.
- [x] All existing tests pass, re-pointed at the new locations.
- [x] The golden transcript is byte-identical, run through `python3 tictactoe.py`.
- [x] The README's run and test commands are updated.
