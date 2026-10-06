# The computer searches a Game type's search Moves, which may be fewer than its legal Moves

Gomoku has up to 81 legal Moves per turn, which makes the shared alpha-beta search (ADR 0001) far too slow at any useful Difficulty. Game types may now list the Moves the computer considers separately from the Moves that are legal: an optional `search_moves` that defaults to `legal_moves`. Gomoku only searches the empty Points near a stone. A human may still play any empty Point, so "legal" keeps its meaning: `move_problem` and `legal_moves` agree.

## Considered Options

- **Narrow `legal_moves` itself**: needs no framework change, but then a Move can pass `move_problem` without being in `legal_moves`, and "legal" no longer means one thing.
- **Keep the framework and search all 81 Points**: the computer could only look one or two Moves ahead and would play badly.
