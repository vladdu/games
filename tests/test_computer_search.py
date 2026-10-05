"""The shared computer search, played against a toy Game type that has no
search of its own: a game tree written out by hand, so every score the
search should find is known from the tree itself."""

import unittest

from games.framework import DRAW, Computer, Human, Moved, play_game
from tests.support import ScriptedIO

A, B = "A", "B"


class TreeGame:
    """A Game type whose whole game tree is a nested dict. A node is a dict
    of Moves (in legal-Move order) to child nodes, or a leaf: the Result.
    A, then B, then A... move. ``scores`` gives the heuristic score, from
    A's point of view, of a node in progress, keyed by its path."""

    name = "tree"
    title = "Tree"
    sides = (A, B)
    default_depth = None

    def __init__(self, tree, scores=None):
        self.tree = tree
        self.scores = scores or {}

    def _node(self, state):
        node = self.tree
        for move in state:
            node = node[move]
        return node

    def initial_state(self):
        return ()

    def to_move(self, state):
        return self.sides[len(state) % 2]

    def legal_moves(self, state):
        node = self._node(state)
        return list(node) if isinstance(node, dict) else []

    def move_problem(self, state, move):
        return None if move in self.legal_moves(state) else "no such move"

    def apply_move(self, state, move):
        if self.move_problem(state, move) is not None:
            raise ValueError(move)
        return state + (move,)

    def result(self, state):
        node = self._node(state)
        return None if isinstance(node, dict) else node

    def heuristic(self, state, side):
        score = self.scores.get(state, 0)
        return score if side == A else -score

    def unbeatable(self, depth):
        return False

    def parse_move(self, text):
        return text.strip(), None

    def move_text(self, move):
        return move


def computer_move(game_type, depth=None, state=()):
    return Computer(depth).choose_move(game_type, state, None)


class SharedSearchTests(unittest.TestCase):
    def test_plays_any_game_type_to_a_win(self):
        # Only "good" wins for A; B's reply to "bad" wins for B.
        game = TreeGame({"bad": {"x": B, "y": A},
                         "good": {"x": A, "y": A}})
        self.assertEqual(computer_move(game), "good")

    def test_prefers_a_faster_win(self):
        game = TreeGame({"slow": {"x": {"y": A}}, "fast": A})
        self.assertEqual(computer_move(game), "fast")

    def test_prefers_a_slower_loss(self):
        game = TreeGame({"quick": {"x": B},
                         "late": {"x": {"y": {"z": B}}}})
        self.assertEqual(computer_move(game), "late")

    def test_prefers_a_draw_to_a_loss(self):
        game = TreeGame({"lose": {"x": B}, "draw": {"x": DRAW}})
        self.assertEqual(computer_move(game), "draw")

    def test_ties_go_to_the_first_legal_move(self):
        self.assertEqual(computer_move(TreeGame({"p": A, "q": A})), "p")
        self.assertEqual(computer_move(TreeGame({"q": A, "p": A})), "q")

    def test_plays_for_the_side_to_move(self):
        # B to move after A's "a": "b1" lets A win, "b2" wins for B.
        game = TreeGame({"a": {"b1": {"x": A}, "b2": {"x": B}}})
        self.assertEqual(computer_move(game, state=("a",)), "b2")

    def test_difficulty_is_how_many_moves_ahead_it_looks(self):
        # Looking one Move ahead, "trap" scores better; looking to the end,
        # "trap" loses and "safe" draws.
        tree = {"safe": {"x": DRAW}, "trap": {"x": B}}
        game = TreeGame(tree, scores={("safe",): 1, ("trap",): 9})
        self.assertEqual(computer_move(game, depth=1), "trap")
        self.assertEqual(computer_move(game, depth=2), "safe")
        self.assertEqual(computer_move(game, depth=None), "safe")

    def test_heuristic_is_taken_from_the_searching_sides_view(self):
        # B to move, looking one Move ahead: A's scores favour "b1", so B
        # prefers "b2".
        tree = {"a": {"b1": {"x": DRAW}, "b2": {"x": DRAW}}}
        game = TreeGame(tree, scores={("a", "b1"): 5, ("a", "b2"): -5})
        self.assertEqual(computer_move(game, depth=1, state=("a",)), "b2")

    def test_computer_plays_a_whole_game(self):
        game = TreeGame({"bad": {"x": B}, "good": {"x": A, "y": A}})
        scripted = ScriptedIO(["x"])
        result = play_game(game, (Computer(), Human()), scripted)
        self.assertEqual(result, A)
        moves = [(e.side, e.move) for e in scripted.of_type(Moved)]
        self.assertEqual(moves, [(A, "good"), (B, "x")])


if __name__ == "__main__":
    unittest.main()
