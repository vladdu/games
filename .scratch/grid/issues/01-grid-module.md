# 01: The Grid module

Status: ready-for-agent

**What to build:** `games/grid.py` with `Grid(width, height, n)` as described in the spec and ADR 0003. It isn't used by any Game type yet. No visible behaviour changes.

**Blocked by:** none.

- [ ] `Grid(width, height, n)` is an immutable value that computes its windows of `n`, and the windows through each point, once, when it is built.
- [ ] Operations on a flat bottom-left tuple of cells (None = empty): the piece at a point; the cells after placing a piece; the Line through a point (the whole run of `n` or more, from one end, or None); the window heuristic for a Side from a `{count: score}` table.
- [ ] The module docstring states the cell layout, the "N or more" rule, and that the Grid stays out of the Game type interface (ADR 0003).
- [ ] `tests/test_grid.py`, through the Grid's interface only: a Line in each direction; a Line longer than N; a Line along the edge of a 7x6 grid; no Line through a point outside one or through an empty point; placing leaves the original cells unchanged; the heuristic on a small grid, with mixed windows scoring 0.
- [ ] All existing tests and both golden transcripts pass unchanged.
