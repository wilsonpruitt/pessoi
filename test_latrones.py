"""Unit tests for the latrones capture, freeing, and termination logic."""
import unittest
from latrones import Game, RuleSet


def blank(W=8, H=8, **flags):
    """A cleared board in movement phase, for hand-built positions."""
    rs = RuleSet(setup="array", width=W, height=H, pieces=1, **flags)
    g = Game(rs)
    g.board = [0] * g.r.cells()
    g.frozen = {}
    g.phase = 1
    g.to_place = {1: 0, 2: 0}
    g.last_move = {1: None, 2: None}
    g.result = None
    g.move_plies = 0
    return g


def I(g, x, y):
    return g.idx(x, y)


class CaptureTests(unittest.TestCase):
    def test_line_capture(self):
        g = blank(victory="blockade")
        g.board[I(g, 2, 3)] = 1          # friendly flanker (left)
        g.board[I(g, 3, 3)] = 2          # foe to be taken
        g.board[I(g, 4, 3)] = 1          # mover just arrived (right)
        g._capture_from(I(g, 4, 3), 1)
        self.assertEqual(g.board[I(g, 3, 3)], 0)

    def test_no_suicide(self):
        g = blank(victory="blockade")
        g.board[I(g, 2, 3)] = 2          # foe
        g.board[I(g, 4, 3)] = 2          # foe
        g.board[I(g, 3, 3)] = 1          # mover steps INTO the gap
        g._capture_from(I(g, 3, 3), 1)
        self.assertEqual(g.board[I(g, 3, 3)], 1)   # mover survives

    def test_multi_capture(self):
        g = blank(victory="blockade")
        # vertical bracket
        g.board[I(g, 3, 1)] = 1
        g.board[I(g, 3, 2)] = 2
        # horizontal bracket
        g.board[I(g, 1, 3)] = 1
        g.board[I(g, 2, 3)] = 2
        g.board[I(g, 3, 3)] = 1          # mover closes both
        g._capture_from(I(g, 3, 3), 1)
        self.assertEqual(g.board[I(g, 3, 2)], 0)
        self.assertEqual(g.board[I(g, 2, 3)], 0)

    def test_corner_capture_on(self):
        g = blank(corner_capture=True, victory="blockade")
        g.board[I(g, 0, 0)] = 2          # foe in corner
        g.board[I(g, 0, 1)] = 1          # flanker
        g.board[I(g, 1, 0)] = 1          # mover arrives
        g._capture_from(I(g, 1, 0), 1)
        self.assertEqual(g.board[I(g, 0, 0)], 0)

    def test_corner_capture_off(self):
        g = blank(corner_capture=False, victory="blockade")
        g.board[I(g, 0, 0)] = 2
        g.board[I(g, 0, 1)] = 1
        g.board[I(g, 1, 0)] = 1
        g._capture_from(I(g, 1, 0), 1)
        self.assertEqual(g.board[I(g, 0, 0)], 2)   # corner survives


class FreezingTests(unittest.TestCase):
    def test_freeze_marks_not_removes(self):
        g = blank(freeing=True, victory="blockade")
        g.board[I(g, 2, 3)] = 1
        g.board[I(g, 3, 3)] = 2
        g.board[I(g, 4, 3)] = 1
        g._capture_from(I(g, 4, 3), 1)
        self.assertEqual(g.board[I(g, 3, 3)], 2)        # still on board
        self.assertIn(I(g, 3, 3), g.frozen)             # but frozen

    def test_resolve_removes_when_still_trapped(self):
        g = blank(freeing=True, victory="blockade")
        g.board[I(g, 2, 3)] = 1
        g.board[I(g, 3, 3)] = 2
        g.board[I(g, 4, 3)] = 1
        g.frozen[I(g, 3, 3)] = 1
        g._resolve_frozen(1)
        self.assertEqual(g.board[I(g, 3, 3)], 0)
        self.assertNotIn(I(g, 3, 3), g.frozen)

    def test_rescue_releases_incitus(self):
        g = blank(freeing=True, victory="blockade")
        g.board[I(g, 3, 3)] = 2            # incitus
        g.board[I(g, 4, 3)] = 1            # one flanker present
        # other flanker (2,3) is GONE -> bracket broken -> rescue
        g.frozen[I(g, 3, 3)] = 1
        g._resolve_frozen(1)
        self.assertEqual(g.board[I(g, 3, 3)], 2)        # survives
        self.assertNotIn(I(g, 3, 3), g.frozen)          # released

    def test_frozen_cannot_flank(self):
        g = blank(freeing=True, victory="blockade")
        g.board[I(g, 2, 3)] = 1
        g.frozen[I(g, 2, 3)] = 2          # this friendly is itself an incitus
        g.board[I(g, 3, 3)] = 2
        g.board[I(g, 4, 3)] = 1
        g._capture_from(I(g, 4, 3), 1)
        self.assertEqual(g.board[I(g, 3, 3)], 2)        # not captured: flanker inert


class RuleTests(unittest.TestCase):
    def test_vagi_immunity(self):
        g = blank(setup_dummy=None) if False else None
        rs = RuleSet(setup="placement", width=8, height=8, pieces=4)
        g = Game(rs)
        g.board = [0] * g.r.cells()
        g.board[I(g, 2, 3)] = 1
        g.board[I(g, 3, 3)] = 2
        g.to_place = {1: 1, 2: 0}
        g.phase = 0
        g.to_move = 1
        g.apply(("place", I(g, 4, 3)))      # would bracket the foe in movement
        self.assertEqual(g.board[I(g, 3, 3)], 2)        # but vagi are immune

    def test_blockade_detected(self):
        g = blank(W=3, H=3, victory="both")
        # p1 single piece boxed with no empty orthogonal neighbour
        g.board[I(g, 0, 0)] = 1
        g.board[I(g, 1, 0)] = 2
        g.board[I(g, 0, 1)] = 2
        g.to_move = 1
        g._check_end()
        self.assertEqual(g.result, 2)

    def test_anti_shuffle_forbids_reverse(self):
        g = blank(anti_shuffle=True, victory="blockade")
        g.board[I(g, 3, 3)] = 1
        g.last_move[1] = (I(g, 2, 3), I(g, 3, 3))   # just moved 2,3 -> 3,3
        g.to_move = 1
        moves = g.legal_moves()
        self.assertNotIn(("move", I(g, 3, 3), I(g, 2, 3)), moves)  # reverse banned
        self.assertIn(("move", I(g, 3, 3), I(g, 4, 3)), moves)     # others fine


if __name__ == "__main__":
    unittest.main(verbosity=2)


class SecondRescueTests(unittest.TestCase):
    def test_freed_piece_dies_on_retrap(self):
        g = blank(freeing=True, no_second_rescue=True, victory="blockade")
        cell = I(g, 3, 3)
        g.board[cell] = 2
        g.ids[cell] = 99
        g.rescued.add(99)                 # this piece was already freed once
        g.board[I(g, 2, 3)] = 1           # flanker
        g.board[I(g, 4, 3)] = 1           # mover arrives
        g._capture_from(I(g, 4, 3), 1)
        self.assertEqual(g.board[cell], 0)        # removed at once
        self.assertNotIn(cell, g.frozen)          # not given a second incitus

    def test_first_trap_still_freezes(self):
        g = blank(freeing=True, no_second_rescue=True, victory="blockade")
        cell = I(g, 3, 3)
        g.board[cell] = 2
        g.ids[cell] = 42                  # never rescued before
        g.board[I(g, 2, 3)] = 1
        g.board[I(g, 4, 3)] = 1
        g._capture_from(I(g, 4, 3), 1)
        self.assertIn(cell, g.frozen)             # first time: normal incitus
