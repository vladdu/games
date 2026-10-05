# One shared alpha-beta search plays the computer side of every Game type

Full minimax made the tic-tac-toe computer unbeatable, but it is far too slow for larger Game types such as Connect Four. We chose a single depth-limited alpha-beta search shared by all Game types: each Game type supplies a heuristic score for positions the search does not play to the end, and Difficulty is the search depth. Tic-tac-toe searches with unlimited depth, so it stays unbeatable, but being unbeatable is now a property of tic-tac-toe at full Difficulty, not something the framework promises. Ties are still broken deterministically, so tests stay reproducible.

## Considered Options

- **Monte Carlo tree search**: needs no heuristic, but it is random and weaker at blocking short-term threats, and its deterministic tests are harder to write.
- **A hand-written AI per Game type**: each Game type would duplicate the search and its tests.
