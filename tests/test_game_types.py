"""The shared suite every registered Game type must pass (seam 2: the Game
type interface)."""

import random
import unittest

from games.registry import GAME_TYPES

# Text a human might type; any of it that parses to a Move that is not
# legal must be refused with a reason.
TYPED = [str(n) for n in range(-2, 12)] + ["99", "-50"]
TYPED += ["e5", "a1", "i9", "j3", "a10", "a0", "z1", "e99"]
PLAYOUTS = 30
MAX_MOVES = 1000


def playouts(game_type, seed=0):
    """Yield every state of ``PLAYOUTS`` random Games of ``game_type``,
    each Game's states in order."""
    rng = random.Random(seed)
    for _ in range(PLAYOUTS):
        state = game_type.initial_state()
        yield state
        for _ in range(MAX_MOVES):
            moves = game_type.legal_moves(state)
            if not moves:
                break
            state = game_type.apply_move(state, rng.choice(moves))
            yield state


class SharedGameTypeTests(unittest.TestCase):
    def test_registry_is_not_empty_and_keyed_by_name(self):
        self.assertIn("tictactoe", GAME_TYPES)
        self.assertIn("connect-four", GAME_TYPES)
        self.assertIn("gomoku", GAME_TYPES)
        for name, game_type in GAME_TYPES.items():
            self.assertEqual(game_type.name, name)

    def test_random_playouts_end_with_a_result(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                rng = random.Random(1)
                for _ in range(PLAYOUTS):
                    state = game_type.initial_state()
                    for _ in range(MAX_MOVES):
                        if game_type.result(state) is not None:
                            break
                        moves = game_type.legal_moves(state)
                        self.assertTrue(moves, "no Moves, no Result")
                        state = game_type.apply_move(state, rng.choice(moves))
                    result = game_type.result(state)
                    self.assertIsNotNone(result)
                    self.assertIn(result, list(game_type.sides) + ["draw"])
                    self.assertEqual(game_type.legal_moves(state), [])

    def test_the_side_to_move_is_one_of_the_sides(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                self.assertEqual(len(game_type.sides), 2)
                for state in playouts(game_type):
                    if game_type.result(state) is None:
                        self.assertIn(game_type.to_move(state), game_type.sides)

    def test_legal_moves_are_accepted(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                for state in playouts(game_type):
                    for move in game_type.legal_moves(state):
                        self.assertIsNone(game_type.move_problem(state, move), move)
                        after = game_type.apply_move(state, move)
                        if game_type.result(after) is None:
                            self.assertIn(game_type.to_move(after), game_type.sides)

    def test_rejected_moves_are_refused_with_a_reason(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                refused = 0
                for state in playouts(game_type):
                    if game_type.result(state) is not None:
                        continue
                    legal = game_type.legal_moves(state)
                    for text in TYPED:
                        move, error = game_type.parse_move(text)
                        if error is not None or move in legal:
                            continue
                        reason = game_type.move_problem(state, move)
                        self.assertIsNotNone(reason, text)
                        self.assertTrue(game_type.rejection_message(move, reason))
                        with self.assertRaises(ValueError):
                            game_type.apply_move(state, move)
                        refused += 1
                self.assertGreater(refused, 0)

    def test_typed_moves_parse_back_to_the_same_move(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                for state in playouts(game_type):
                    for move in game_type.legal_moves(state):
                        text = game_type.move_text(move)
                        self.assertEqual(game_type.parse_move(text), (move, None))

    def test_unparseable_text_gives_an_error_message(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                move, error = game_type.parse_move("abc")
                self.assertIsNone(move)
                self.assertTrue(error)

    def test_heuristic_scores_positions_in_progress(self):
        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                state = game_type.initial_state()
                for side in game_type.sides:
                    self.assertIsInstance(
                        game_type.heuristic(state, side), (int, float)
                    )

    def test_renders_every_state(self):
        import io

        from rich.console import Console

        for game_type in GAME_TYPES.values():
            with self.subTest(game_type.name):
                console = Console(file=io.StringIO(), width=80)
                for state in playouts(game_type):
                    console.print(game_type.render(state))


if __name__ == "__main__":
    unittest.main()
