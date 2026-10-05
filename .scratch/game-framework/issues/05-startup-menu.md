# 05: Startup menu

**What to build:** Running `python3 -m games` without `--game` shows a menu of the registered Game types and plays the one chosen. "Play again" plays the same Game type. `--game` still skips the menu, and `python3 tictactoe.py` still goes straight into tic-tac-toe.

**Blocked by:** 03 (Both Game types play through one Game loop).

**Status:** ready-for-agent

- [ ] The menu lists every Game type in the registry; invalid choices are re-prompted, and Ctrl+C or Ctrl+D quits.
- [ ] "Play again" keeps the chosen Game type.
- [ ] A process-level test pipes a scripted session through the menu path and compares it with a new, deliberately recorded golden transcript.
- [ ] The existing tic-tac-toe golden transcript, run through `python3 tictactoe.py`, is unchanged.
- [ ] `--help` and the README describe the menu.
