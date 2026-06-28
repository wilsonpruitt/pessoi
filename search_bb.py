"""
search_bb.py  —  Bitboard-native negamax (Priority-stack #3, the actual win).

A drop-in BitGame swap under the list-based search.py is only ~1.08x, because
evaluation() and the capture-ordering rebuild a board list from the bitboards at
every node. This module reimplements both hot paths to read the p1/p2 integers
directly:

  * evaluation_bb — material / mobility / vuln / threat / centre computed with
    bitboard shifts and popcounts (numerically equal to search.evaluation, so
    this is an apples-to-apples speed comparison, not a different player);
  * capture-count move ordering — O(1) per move from the four directions around
    the destination, no board list;
  * negamax over BitGame.clone() (cheap int copy).

The eval mirrors search.py's weights exactly (W_MATERIAL=100 ...). For the
blockade-aware weights, point evaluation_bb at search_v2's constants instead;
the speed scaffolding here is what unlocks depth-3 and MCTS volume regardless.
"""
from __future__ import annotations
import random

from latrones import ORTHO
from search import (W_MATERIAL, W_MOBILITY, W_VULN, W_THREAT, W_CENTRE)

WIN = 1_000_000.0

_CDIST = {}     # (W,H) -> tuple of |x-cx|+|y-cy| per cell


def _cdist(W, H):
    key = (W, H)
    c = _CDIST.get(key)
    if c is None:
        cx, cy = (W - 1) / 2, (H - 1) / 2
        c = tuple(abs(i % W - cx) + abs(i // W - cy) for i in range(W * H))
        _CDIST[key] = c
    return c


def _bits(bb):
    while bb:
        low = bb & -bb
        yield low.bit_length() - 1
        bb ^= low


def evaluation_bb(g, side):
    p1, p2 = g.p1, g.p2
    own = p1 if side == 1 else p2
    foe = p2 if side == 1 else p1
    full = g.FULL
    empty = full & ~(p1 | p2)

    mat = own.bit_count() - foe.bit_count()

    # mobility: pieces with at least one empty orthogonal neighbour
    noe = g._north(empty) | g._south(empty) | g._east(empty) | g._west(empty)
    mob = (own & noe).bit_count() - (foe & noe).bit_count()

    # one-move-from-bracketed, per axis. For an OWN piece "want" is foe; a piece
    # is at risk if a `want` sits on one side and the opposite side is empty so a
    # `want` could move in. Shift identities:
    #   _east(X)  = cells whose WEST neighbour is in X
    #   _west(X)  = cells whose EAST neighbour is in X
    #   _south(X) = cells whose NORTH neighbour is in X
    #   _north(X) = cells whose SOUTH neighbour is in X
    e_foe, w_foe = g._east(foe), g._west(foe)
    s_foe, n_foe = g._south(foe), g._north(foe)
    e_emp, w_emp = g._east(empty), g._west(empty)
    s_emp, n_emp = g._south(empty), g._north(empty)
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

    return (W_MATERIAL * mat + W_MOBILITY * mob
            - W_VULN * vuln + W_THREAT * threat + W_CENTRE * centre)


def _capture_count_bb(g, frm, to, p):
    """Captures created by p moving frm->to, counted in O(1) from the four
    directions around `to` (line captures only — matches search._capture_count,
    which ignores corners for ordering)."""
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


class SearcherBB:
    def __init__(self, limit=6000):
        self.limit = limit
        self.nodes = 0

    def negamax(self, g, depth, alpha, beta):
        if g.result is not None:
            if g.result == 0:
                return 0.0
            return WIN if g.result == g.to_move else -WIN
        self.nodes += 1
        if depth == 0 or self.nodes > self.limit:
            return evaluation_bb(g, g.to_move)
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


class NegamaxAgentBB:
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
        searcher = SearcherBB(self.node_budget)
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


def negamax_bb_factory(depth=2, node_budget=6000):
    def make(rng):
        return NegamaxAgentBB(rng, depth=depth, node_budget=node_budget)
    return make
