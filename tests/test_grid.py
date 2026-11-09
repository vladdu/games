import unittest

from games.grid import Grid

X = "X"
O = "O"


def cells_with(grid, points, piece=X, cells=None):
    """Return ``cells`` (default: empty) with ``piece`` placed at ``points``."""
    if cells is None:
        cells = (None,) * (grid.width * grid.height)
    for point in points:
        cells = grid.place(cells, point, piece)
    return cells


class LineTests(unittest.TestCase):
    grid = Grid(5, 5, 3)

    def test_a_line_along_a_row(self):
        cells = cells_with(self.grid, [(0, 1), (1, 1), (2, 1)])
        self.assertEqual(self.grid.line(cells, (1, 1)), ((0, 1), (1, 1), (2, 1)))

    def test_a_line_along_a_column(self):
        cells = cells_with(self.grid, [(3, 0), (3, 1), (3, 2)])
        self.assertEqual(self.grid.line(cells, (3, 2)), ((3, 0), (3, 1), (3, 2)))

    def test_a_line_along_a_rising_diagonal(self):
        cells = cells_with(self.grid, [(1, 1), (2, 2), (3, 3)])
        self.assertEqual(self.grid.line(cells, (2, 2)), ((1, 1), (2, 2), (3, 3)))

    def test_a_line_along_a_falling_diagonal(self):
        cells = cells_with(self.grid, [(0, 4), (1, 3), (2, 2)])
        self.assertEqual(self.grid.line(cells, (0, 4)), ((0, 4), (1, 3), (2, 2)))

    def test_a_line_longer_than_n_is_returned_whole(self):
        cells = cells_with(self.grid, [(c, 0) for c in range(5)])
        self.assertEqual(self.grid.line(cells, (4, 0)), tuple((c, 0) for c in range(5)))

    def test_a_line_along_the_edge_of_a_7x6_grid(self):
        grid = Grid(7, 6, 4)
        cells = cells_with(grid, [(6, 2), (6, 3), (6, 4), (6, 5)])
        self.assertEqual(grid.line(cells, (6, 5)), ((6, 2), (6, 3), (6, 4), (6, 5)))
        cells = cells_with(grid, [(3, 5), (4, 5), (5, 5), (6, 5)])
        self.assertEqual(grid.line(cells, (3, 5)), ((3, 5), (4, 5), (5, 5), (6, 5)))

    def test_no_line_through_a_point_outside_one(self):
        cells = cells_with(self.grid, [(0, 0), (1, 0), (2, 0), (0, 2)])
        cells = cells_with(self.grid, [(1, 1)], O, cells)
        self.assertIsNone(self.grid.line(cells, (0, 2)))
        self.assertIsNone(self.grid.line(cells, (1, 1)))

    def test_no_line_through_an_empty_point(self):
        cells = cells_with(self.grid, [(0, 0), (2, 0)])
        self.assertIsNone(self.grid.line(cells, (1, 0)))

    def test_no_line_through_no_point(self):
        cells = cells_with(self.grid, [(0, 0), (1, 0), (2, 0)])
        self.assertIsNone(self.grid.line(cells, None))

    def test_a_broken_row_is_not_a_line(self):
        cells = cells_with(self.grid, [(0, 0), (1, 0), (3, 0), (4, 0)])
        cells = cells_with(self.grid, [(2, 0)], O, cells)
        self.assertIsNone(self.grid.line(cells, (1, 0)))


class CellsTests(unittest.TestCase):
    def test_cells_run_row_by_row_from_the_bottom_left(self):
        grid = Grid(3, 2, 2)
        cells = cells_with(grid, [(2, 0)])
        cells = cells_with(grid, [(0, 1)], O, cells)
        self.assertEqual(cells, (None, None, X, O, None, None))
        self.assertEqual(grid.piece(cells, (2, 0)), X)
        self.assertEqual(grid.piece(cells, (0, 1)), O)
        self.assertIsNone(grid.piece(cells, (1, 1)))

    def test_placing_leaves_the_original_cells_unchanged(self):
        grid = Grid(3, 3, 3)
        empty = (None,) * 9
        placed = grid.place(empty, (1, 1), X)
        self.assertEqual(empty, (None,) * 9)
        self.assertEqual(grid.piece(placed, (1, 1)), X)

    def test_a_grid_is_immutable(self):
        grid = Grid(3, 3, 3)
        with self.assertRaises(AttributeError):
            grid.n = 4


class ScoreTests(unittest.TestCase):
    grid = Grid(2, 2, 2)  # 6 windows: 2 across, 2 up, 1 rising, 1 falling
    table = {1: 1, 2: 10}

    def test_an_empty_grid_scores_0(self):
        self.assertEqual(self.grid.score((None,) * 4, X, self.table), 0)

    def test_open_windows_count_for_their_side(self):
        # X at (0, 0): in 3 windows (across, up, rising), each holding 1.
        cells = cells_with(self.grid, [(0, 0)])
        self.assertEqual(self.grid.score(cells, X, self.table), 3)
        self.assertEqual(self.grid.score(cells, O, self.table), -3)

    def test_fuller_windows_score_from_the_table(self):
        # X across the bottom: that window holds 2 (10); the 2 up windows and
        # the 2 diagonals hold 1 each (4).
        cells = cells_with(self.grid, [(0, 0), (1, 0)])
        self.assertEqual(self.grid.score(cells, X, self.table), 14)

    def test_mixed_windows_score_0(self):
        # X at (0, 0), O at (1, 1): the rising window is mixed (0); X has
        # across and up (+2), O has across and up (-2).
        cells = cells_with(self.grid, [(0, 0)])
        cells = cells_with(self.grid, [(1, 1)], O, cells)
        self.assertEqual(self.grid.score(cells, X, self.table), 0)
        cells = cells_with(self.grid, [(0, 1)], X, cells)
        # Now X: up (0,0)-(0,1) = 10, falling (0,1)-(1,0) = 1, bottom across = 1;
        # O: right up = -1; top across and rising are mixed.
        self.assertEqual(self.grid.score(cells, X, self.table), 11)
