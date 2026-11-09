# Coding standards

Judgement calls for review. `just check` (ruff and the tests) covers everything mechanical.

- **Glossary terms.** Names, docstrings and comments use the terms in `GLOSSARY.md`, and honour every _Avoid_ line (a Line is never a "run"; Cell is tic-tac-toe's word, Point everyone else's).
- **Immutable values** are `@dataclass(frozen=True)`, like every State and `Grid`.
- **Docstrings.** Every function and class has one, at least one line.
