"""
search_v2_bb.py  —  Bitboard-native port of the blockade-aware eval (search_v2),
so the v2 agent runs fast enough for a depth-3 sweep.

evaluation_v2_bb computes search_v2.evaluation_v2 with bitboard ops:
  * material            = popcount(own) - popcount(foe)
  * own/foe liberty     = sum of empty orthogonal exits per piece, via
                          popcount(side & shift(empty)) over the 4 directions
                          (shift identity: a piece has an empty neighbour in
                          direction d iff it lies in the back-shift of empty)
  * support (azux)      = (+1 supported / -1 lone) for own, mirror for foe,
                          via popcount(side & neighbours-of-side)
  * vuln / threat       = one-move-from-bracketed masks (as in evaluation_bb)
  * centre              = sum of centre distances (bit iteration)

Terminal scoring mirrors search_v2._terminal_value (blockade win preferred).
Parity vs the list eval is asserted in bench_v2.py.
"""
from __future__ import annotations
import random

from latrones import ORTHO
import search_v2 as _v2
from search_bb import _cdist, _bits

WIN = 1_000_000.0


def evaluation_v2_bb(g, side):
    p1, p2 = g.p1, g.p2
    own = p1 if side == 1 else p2
    foe = p2 if side == 1 else p1
    empty = g.FULL & ~(p1 | p2)
    own_n = own.bit_count()
    foe_n = foe.bit_count()

    mat = own_n - foe_n

    e_emp, w_emp = g._east(empty), g._west(empty)
    s_emp, n_emp = g._south(empty), g._north(empty)
    # sum of empty orthogonal exits per piece (degree-of-freedom proxy)
    own_mob = ((own & e_emp).bit_count() + (own & w_emp).bit_count()
               + (own & s_emp).bit_count() + (own & n_emp).bit_count())
    foe_mob = ((foe & e_emp).bit_count() + (foe & w_emp).bit_count()
               + (foe & s_emp).bit_count() + (foe & n_emp).bit_count())

    # support: own pieces with >=1 friendly orthogonal neighbour
    noo = g._north(own) | g._south(own) | g._east(own) | g._west(own)
    own_supp = (own & noo).bit_count()
    nof = g._north(foe) | g._south(foe) | g._east(foe) | g._west(foe)
    foe_supp = (foe & nof).bit_count()
    # own: +1 supported / -1 lone = 2*supp - total; foe mirrored = total - 2*supp
    support = (2 * own_supp - own_n) + (foe_n - 2 * foe_supp)

    e_foe, w_foe = g._east(foe), g._west(foe)
    s_foe, n_foe = g._south(foe), g._north(foe)
    vuln_mask = (e_foe & w_emp) | (w_foe & e_emp) | (s_foe & n_emp) | (n_foe & s_emp)
    vuln = (own & vuln_mask).bit_count()

    e_own, w_own = g._east(own), g._west(own)
    s_own, n_own = g._south(own), g._north(own)
    threat_mask = (e_own & w_emp) | (w_own & e_emp) | (s_own & n_emp) | (n_own & s_emp)
    threat = (foe & threat_mask).bit_count()

    cd = _cdist(g.W, g.H)
    centre = 0.0
    for i in _bits(own):
        centre -= cd[i]
    for i in _bits(foe):
        centre += cd[i]

    return (_v2.W_MAT * mat
            - _v2.W_MOBDENY * foe_mob
            + _v2.W_OWNMOB * own_mob
            + _v2.W_SUPPORT * support
            - _v2.W_VULN * vuln + _v2.W_THREAT * threat
            + _v2.W_CENTRE * centre)


def _terminal_value(g):
    if g.result == 0:
        return 0.0
    win_for_to_move = (g.result == g.to_move)
    loser = 3 - g.result
    by_blockade = (g.move_plies < g.r.move_cap
                   and g.count(loser) > g.r.min_pieces)
    val = WIN + (_v2.BLOCKADE_BONUS if by_blockade else 0.0)
    return val if win_for_to_move else -val


def _capture_count_bb(g, frm, to, p):
    own = (g.p1 if p == 1 else g.p2)
    own = (own & ~(1 << frm)) | (1 << to)
    foe = g.p2 if p == 1 else g.p1
    W, H = g.W, g.H
    x, y = to % W, to // W
    n = 0
    for dx, dy in ORTHO:
        ex, ey = x + dx, y + dy
        bx, by = x + 2 * dx, y + 2 * dy
        if 0 <= ex < W and 0 <= ey < H and 0 <= bx < W and 0 <= by < H:
            if (foe >> (ey * W + ex)) & 1 and (own >> (by * W + bx)) & 1:
                n += 1
    return n


def _order(g, moves):
    p = g.to_move
    return sorted(
        moves,
        key=lambda m: _capture_count_bb(g, m[1], m[2], p) if m[0] == "move" else 0,
        reverse=True,
    )


class SearcherV2BB:
    def __init__(self, limit=6000):
        self.limit = limit
        self.nodes = 0

    def negamax(self, g, depth, alpha, beta):
        if g.result is not None:
            return _terminal_value(g)
        self.nodes += 1
        if depth == 0 or self.nodes > self.limit:
            return evaluation_v2_bb(g, g.to_move)
        moves = g.legal_moves()
        if not moves:
            return -WIN
        best = -1e18
        for m in _order(g, moves):
            s = g.snapshot()
            g.apply(m)
            val = -self.negamax(g, depth - 1, -beta, -alpha)
            g.restore(s)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best


class NegamaxAgentV2BB:
    def __init__(self, rng, depth=2, node_budget=6000, eps=0.03):
        self.rng = rng
        self.depth = depth
        self.node_budget = node_budget
        self.eps = eps

    def _place(self, g, moves):
        cd = _cdist(g.W, g.H)
        best, bs = [], 1e18
        for m in moves:
            d = cd[m[1]]
            if d < bs:
                bs, best = d, [m]
            elif d == bs:
                best.append(m)
        return self.rng.choice(best)

    def choose(self, g, moves):
        if g.phase == 0:
            return self._place(g, moves)
        if self.rng.random() < self.eps:
            return self.rng.choice(moves)
        searcher = SearcherV2BB(self.node_budget)
        best, best_val = [], -1e18
        for m in _order(g, moves):
            snap = g.snapshot()
            g.apply(m)
            val = -searcher.negamax(g, self.depth - 1, -1e18, 1e18)
            g.restore(snap)
            if val > best_val + 1e-9:
                best_val, best = val, [m]
            elif abs(val - best_val) <= 1e-9:
                best.append(m)
        return self.rng.choice(best)


def negamax_v2_bb_factory(depth=2, node_budget=6000):
    def make(rng):
        return NegamaxAgentV2BB(rng, depth=depth, node_budget=node_budget)
    return make
