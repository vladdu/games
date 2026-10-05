# 04: One shared computer search

**What to build:** Every Game type's computer opponent is the same depth-limited alpha-beta search, as decided in ADR 0001. Difficulty is the search depth, and each Game type has a default Difficulty. Tic-tac-toe searches without a depth limit, so it stays unbeatable.

**Blocked by:** 03 (Both Game types play through one Game loop).

**Status:** ready-for-agent

- [ ] One search, used by the Computer Player for every Game type. It uses depth-aware scores (faster wins and slower losses preferred), the Game type's heuristic where it stops before the end of the Game, and deterministic tie-breaking.
- [ ] Both per-Game-type searches are removed.
- [ ] Tic-tac-toe's default Difficulty is unlimited depth, and the exhaustive "the computer never loses, playing first or second" test passes.
- [ ] Connect Four's tactical tests pass, and its default Difficulty still keeps each Move to about a second or less.
- [ ] The tic-tac-toe golden transcript is byte-identical.
