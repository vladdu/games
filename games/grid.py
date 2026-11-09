"""The Grid shared by the Line Game types (tic-tac-toe, Connect Four and
Gomoku): a ``Grid(width, height, n)`` that knows where the Lines of ``n`` can
lie, and answers questions about a board's ``cells``.

Layout: ``cells`` is a flat tuple of the board's ``width * height`` places,
row by row from the bottom left, so the point ``(column, row)`` is index
``row * width + column``. An empty place is None; any other value is a Side's
piece. The Grid never stores cells: every operation takes them.

A Line is ``n`` or more pieces of one Side in an unbroken row, column or
diagonal; one longer than ``n`` is still a Line.

The Grid stays out of the Game type interface (ADR 0003): a Game type
chooses to use it, and the framework never imports this module.
"""

from dataclasses import dataclass, field

DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1))


@dataclass(frozen=True)
class Grid:
    """An immutable ``width`` x ``height`` grid on which a Line is ``n`` or
    more pieces in a row. Its ``windows`` (each the ``n`` indexes into
    ``cells`` of one place a Line can lie), and the windows through each
    point, are worked out once when it is built."""

    width: int
    height: int
    n: int
    windows: tuple = field(init=False, repr=False, compare=False)
    _through: tuple = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        width, height, n = self.width, self.height, self.n
        windows = []
        for row in range(height):
            for column in range(width):
                for dc, dr in DIRECTIONS:
                    end_c, end_r = column + (n - 1) * dc, row + (n - 1) * dr
                    if 0 <= end_c < width and 0 <= end_r < height:
                        windows.append(
                            tuple(
                                self._index((column + i * dc, row + i * dr))
                                for i in range(n)
                            )
                        )
        through = [[] for _ in range(width * height)]
        for window in windows:
            for i in window:
                through[i].append(window)
        object.__setattr__(self, "windows", tuple(windows))
        object.__setattr__(self, "_through", tuple(map(tuple, through)))

    def _index(self, point):
        column, row = point
        return row * self.width + column

    def _on(self, column, row):
        return 0 <= column < self.width and 0 <= row < self.height

    def piece(self, cells, point):
        """The piece at ``point`` ``(column, row)``, or None if it is empty."""
        return cells[self._index(point)]

    def place(self, cells, point, piece):
        """Return new cells with ``piece`` at ``point``; ``cells`` is
        unchanged."""
        i = self._index(point)
        return cells[:i] + (piece,) + cells[i + 1 :]

    def line(self, cells, point):
        """The Line through ``point``: all of its unbroken ``n`` or more of
        one piece, as a tuple of points from one end; None if there is none,
        ``point`` is empty, or ``point`` is None."""
        if point is None:
            return None
        piece = self.piece(cells, point)
        if piece is None:
            return None
        for window in self._through[self._index(point)]:
            if all(cells[i] == piece for i in window):
                return self._whole_line(cells, point, window, piece)
        return None

    def _whole_line(self, cells, point, window, piece):
        # Walk back from the point to the Line's start, then forward to its end.
        width = self.width
        dc, dr = (window[1] % width - window[0] % width,
                  window[1] // width - window[0] // width)
        c, r = point
        while self._on(c - dc, r - dr) and self.piece(cells, (c - dc, r - dr)) == piece:
            c, r = c - dc, r - dr
        line = []
        while self._on(c, r) and self.piece(cells, (c, r)) == piece:
            line.append((c, r))
            c, r = c + dc, r + dr
        return tuple(line)

    def score(self, cells, side, window_scores):
        """The window heuristic for ``side``: each window holding only
        ``side``'s pieces adds ``window_scores[count]``, each holding only
        the other Side's subtracts it, and mixed or empty windows count 0."""
        total = 0
        for window in self.windows:
            mine = theirs = 0
            for i in window:
                piece = cells[i]
                if piece == side:
                    mine += 1
                elif piece is not None:
                    theirs += 1
            if mine and not theirs:
                total += window_scores[mine]
            elif theirs and not mine:
                total -= window_scores[theirs]
        return total
