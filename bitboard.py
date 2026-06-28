"""
bitboard.py  —  Fast bitboard engine for latrones (Priority-stack #3).

The reference engine (latrones.py) stores the board as a length-N Python list
and `clone()`s the whole list at every search node — the throughput wall the
HANDOFF flags. This module reimplements the canonical + research rule-space with
the board held as two integers (one bit per cell per player), so:

  * clone() copies a handful of ints, not a list of N;
  * count() is int.bit_count() (popcount);
  * occupancy / empties / blockade pre-checks are single bit ops.

SCOPE. This engine covers the canonical game and everything the research sweeps
and agents exercise: setup placement|array, movement slide|step (+ optional
leap), corner_capture, anti_shuffle, victory blockade|annihilate|both, and the
material/draw cap rule. It deliberately does NOT implement the freeing/incitus
variant (weakly attested, off by default, and demonstrably combat-suppressing —
§4 of the reconstruction); construct those games on latrones.Game instead.
`BitGame` raises if asked for freeing, so a wrong call fails loudly.

Correctness is established by PARITY against latrones.Game over random games
(test_parity.py), the same discipline used for the verified JS client port.
The external surface matches latrones.Game where the agents touch it
(legal_moves / apply / clone / result / count / to_move / phase / board / ...),
so search.py and search_v2.py run on BitGame unchanged.
"""
from __future__ import annotations
import random

from latrones import RuleSet, ORTHO


def _bits(bb):
    """Yield the set-bit indices of bitboard bb, low to high."""
    while bb:
        low = bb & -bb
        yield low.bit_length() - 1
        bb ^= low


class BitGame:
    # -- construction -------------------------------------------------------- #
    def __init__(self, rules: RuleSet, rng: random.Random | None = None):
        if rules.freeing:
            raise NotImplementedError(
                "BitGame does not implement the freeing/incitus variant; "
                "use latrones.Game for freeing=True rulesets.")
        self.r = rules
        self.rng = rng or random.Random()
        self.W, self.H = rules.width, rules.height
        self.N = self.W * self.H
        self.FULL = (1 << self.N) - 1
        self._build_masks()
        self.p1 = 0
        self.p2 = 0
        self.to_move = 1
        self.ply = 0
        self.move_plies = 0
        self.last_move = {1: None, 2: None}
        self.to_place = {1: 0, 2: 0}
        self.phase = 1
        self.first_movement_move = None
        self.result = None
        self.frozen = {}            # always empty here; kept for API parity
        self._setup()

    def _build_masks(self):
        W, H = self.W, self.H
        self._file_first = sum(1 << (y * W) for y in range(H))          # x == 0
        self._file_last = sum(1 << (y * W + W - 1) for y in range(H))   # x == W-1
        self._corner_bits = [self.idx(0, 0), self.idx(W - 1, 0),
                             self.idx(0, H - 1), self.idx(W - 1, H - 1)]

    # -- coordinate helpers (match latrones.Game) ---------------------------- #
    def idx(self, x, y):  return y * self.W + x
    def xy(self, i):      return (i % self.W, i // self.W)
    def on(self, x, y):   return 0 <= x < self.W and 0 <= y < self.H

    def count(self, p):
        return (self.p1 if p == 1 else self.p2).bit_count()

    # -- direction shifts on the packed board -------------------------------- #
    def _east(self, bb):  return (bb & ~self._file_last) << 1
    def _west(self, bb):  return (bb & ~self._file_first) >> 1
    def _south(self, bb): return (bb << self.W) & self.FULL
    def _north(self, bb): return bb >> self.W

    def _empty(self):
        return self.FULL & ~(self.p1 | self.p2)

    # -- board view (list, like latrones.Game.board) ------------------------- #
    @property
    def board(self):
        b = [0] * self.N
        for i in _bits(self.p1):
            b[i] = 1
        for i in _bits(self.p2):
            b[i] = 2
        return b

    @board.setter
    def board(self, lst):
        p1 = p2 = 0
        for i, v in enumerate(lst):
            if v == 1:
                p1 |= 1 << i
            elif v == 2:
                p2 |= 1 << i
        self.p1, self.p2 = p1, p2

    # -- clone (the point of all this) --------------------------------------- #
    def clone(self):
        g = BitGame.__new__(BitGame)
        g.r = self.r
        g.rng = self.rng
        g.W, g.H, g.N, g.FULL = self.W, self.H, self.N, self.FULL
        g._file_first = self._file_first
        g._file_last = self._file_last
        g._corner_bits = self._corner_bits
        g.p1, g.p2 = self.p1, self.p2
        g.to_move = self.to_move
        g.ply = self.ply
        g.move_plies = self.move_plies
        g.last_move = dict(self.last_move)
        g.to_place = dict(self.to_place)
        g.phase = self.phase
        g.first_movement_move = self.first_movement_move
        g.result = self.result
        g.frozen = {}
        return g

    # -- make/undo (avoid per-node clone allocation in search) --------------- #
    def snapshot(self):
        """Capture the full mutable state as a flat tuple (cheap, no dicts)."""
        return (self.p1, self.p2, self.to_move, self.ply, self.move_plies,
                self.last_move[1], self.last_move[2],
                self.to_place[1], self.to_place[2],
                self.phase, self.first_movement_move, self.result)

    def restore(self, s):
        (self.p1, self.p2, self.to_move, self.ply, self.move_plies,
         lm1, lm2, tp1, tp2, self.phase, self.first_movement_move,
         self.result) = s
        self.last_move[1], self.last_move[2] = lm1, lm2
        self.to_place[1], self.to_place[2] = tp1, tp2

    # -- setup --------------------------------------------------------------- #
    def _setup(self):
        if self.r.setup == "placement":
            self.phase = 0
            self.to_place = {1: self.r.pieces, 2: self.r.pieces}
        else:
            self.phase = 1
            self._fill_array()

    def _fill_array(self):
        n = self.r.pieces
        W, H = self.W, self.H
        p1 = []
        for y in range(H):
            for x in range(W):
                p1.append(self.idx(x, y))
                if len(p1) >= n:
                    break
            if len(p1) >= n:
                break
        p2 = []
        for y in range(H - 1, -1, -1):
            for x in range(W - 1, -1, -1):
                p2.append(self.idx(x, y))
                if len(p2) >= n:
                    break
            if len(p2) >= n:
                break
        for i in p1:
            self.p1 |= 1 << i
        for i in p2:
            self.p2 |= 1 << i

    # -- move generation ----------------------------------------------------- #
    def legal_moves(self):
        p = self.to_move
        if self.phase == 0:
            return [("place", i) for i in _bits(self._empty())]

        own = self.p1 if p == 1 else self.p2
        occ = self.p1 | self.p2
        W, H = self.W, self.H
        forbidden = None
        if self.r.anti_shuffle and self.last_move[p]:
            frm, to = self.last_move[p]
            forbidden = (to, frm)
        leap = self.r.leap
        step = (self.r.movement == "step")
        moves = []
        ap = moves.append
        for i in _bits(own):
            x, y = i % W, i // W
            for dx, dy in ORTHO:
                if step:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        j = ny * W + nx
                        if not (occ >> j) & 1:
                            if forbidden is None or (i, j) != forbidden:
                                ap(("move", i, j))
                        elif leap and (own >> j) & 1:
                            lx, ly = nx + dx, ny + dy
                            if 0 <= lx < W and 0 <= ly < H:
                                k = ly * W + lx
                                if not (occ >> k) & 1 and (
                                        forbidden is None or (i, k) != forbidden):
                                    ap(("move", i, k))
                else:  # slide
                    nx, ny = x + dx, y + dy
                    leapt = False
                    while 0 <= nx < W and 0 <= ny < H:
                        j = ny * W + nx
                        if not (occ >> j) & 1:
                            if forbidden is None or (i, j) != forbidden:
                                ap(("move", i, j))
                        elif leap and (own >> j) & 1 and not leapt:
                            leapt = True
                        else:
                            break
                        nx, ny = nx + dx, ny + dy
        return moves

    def has_legal_move(self):
        """True iff the side to move has at least one legal move. Early-exits on
        the first move found, so it is O(1) in any non-blockaded position (~all
        of them) instead of building the full move list — the blockade test in
        _check_end runs once per search node. Matches legal_moves() exactly,
        including anti_shuffle and leap."""
        p = self.to_move
        if self.phase == 0:
            return self._empty() != 0
        own = self.p1 if p == 1 else self.p2
        occ = self.p1 | self.p2
        # Fast reject: if no own piece is adjacent to an empty cell, no slide or
        # step move can exist (a blocked adjacent cell blocks the whole ray).
        empty = self.FULL & ~occ
        noe = self._north(empty) | self._south(empty) | self._east(empty) | self._west(empty)
        if not (own & noe) and not self.r.leap:
            return False
        W, H = self.W, self.H
        forbidden = None
        if self.r.anti_shuffle and self.last_move[p]:
            frm, to = self.last_move[p]
            forbidden = (to, frm)
        leap = self.r.leap
        step = (self.r.movement == "step")
        for i in _bits(own):
            x, y = i % W, i // W
            for dx, dy in ORTHO:
                if step:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        j = ny * W + nx
                        if not (occ >> j) & 1:
                            if forbidden is None or (i, j) != forbidden:
                                return True
                        elif leap and (own >> j) & 1:
                            lx, ly = nx + dx, ny + dy
                            if 0 <= lx < W and 0 <= ly < H:
                                k = ly * W + lx
                                if not (occ >> k) & 1 and (
                                        forbidden is None or (i, k) != forbidden):
                                    return True
                else:
                    nx, ny = x + dx, y + dy
                    leapt = False
                    while 0 <= nx < W and 0 <= ny < H:
                        j = ny * W + nx
                        if not (occ >> j) & 1:
                            if forbidden is None or (i, j) != forbidden:
                                return True
                        elif leap and (own >> j) & 1 and not leapt:
                            leapt = True
                        else:
                            break
                        nx, ny = nx + dx, ny + dy
        return False

    # -- applying an action -------------------------------------------------- #
    def apply(self, action):
        p = self.to_move
        if action[0] == "place":
            _, cell = action
            if p == 1:
                self.p1 |= 1 << cell
            else:
                self.p2 |= 1 << cell
            self.to_place[p] -= 1
            if self.to_place[1] == 0 and self.to_place[2] == 0:
                self.phase = 1
        else:
            _, frm, to = action
            bit_frm, bit_to = 1 << frm, 1 << to
            if p == 1:
                self.p1 = (self.p1 & ~bit_frm) | bit_to
            else:
                self.p2 = (self.p2 & ~bit_frm) | bit_to
            self.last_move[p] = (frm, to)
            if self.first_movement_move is None:
                self.first_movement_move = (frm, to)
            self._capture_from(to, p)
            self.move_plies += 1

        self.ply += 1
        self.to_move = 3 - p
        self._check_end()
        return self.result

    def _capture_from(self, to, p):
        own = self.p1 if p == 1 else self.p2
        foe_bb = self.p2 if p == 1 else self.p1
        W, H = self.W, self.H
        x, y = to % W, to // W
        captured = 0
        for dx, dy in ORTHO:
            ex, ey = x + dx, y + dy
            bx, by = x + 2 * dx, y + 2 * dy
            if 0 <= ex < W and 0 <= ey < H and 0 <= bx < W and 0 <= by < H:
                e = ey * W + ex
                b = by * W + bx
                if (foe_bb >> e) & 1 and (own >> b) & 1:
                    captured |= 1 << e
        if self.r.corner_capture:
            for c in self._corner_bits:
                if (foe_bb >> c) & 1:
                    cx, cy = c % W, c // W
                    nbrs = [ny * W + nx
                            for dx, dy in ORTHO
                            for nx, ny in ((cx + dx, cy + dy),)
                            if 0 <= nx < W and 0 <= ny < H]
                    if len(nbrs) == 2 and all((own >> n) & 1 for n in nbrs) \
                            and to in nbrs:
                        captured |= 1 << c
        if captured:
            if p == 1:
                self.p2 &= ~captured
            else:
                self.p1 &= ~captured

    # -- termination --------------------------------------------------------- #
    def _check_end(self):
        if self.move_plies >= self.r.move_cap:
            if self.r.cap_rule == "material":
                c1, c2 = self.p1.bit_count(), self.p2.bit_count()
                self.result = 1 if c1 > c2 else (2 if c2 > c1 else 0)
            else:
                self.result = 0
            return
        if self.phase == 0:
            return
        c1, c2 = self.p1.bit_count(), self.p2.bit_count()
        vic = self.r.victory
        if vic in ("annihilate", "both"):
            if c2 <= self.r.min_pieces:
                self.result = 1; return
            if c1 <= self.r.min_pieces:
                self.result = 2; return
        if self.phase == 1 and not self.has_legal_move():
            self.result = (3 - self.to_move) if vic in ("blockade", "both") else 0
            return
