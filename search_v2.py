"""
search_v2.py  —  Blockade-aware agent (Priority-stack #2).

Priority #1 (FINDINGS-blockade-vs-cap.md) showed the canonical victory
condition fires 0% under both the greedy heuristic and the material-first
depth-2 negamax: the eval optimizes a proxy (piece count) the game treats as
secondary. This module rebuilds the evaluation around the thing the game is
actually won by — denying the opponent the ability to move — per the four
levers in HANDOFF §2:

  1. MOBILITY-DENIAL (major term). The opponent's total liberty (here: sum of
     empty orthogonal exits over their unfrozen pieces) is a *major* negative
     term, not the rounding error it was in v1 (W_MOBILITY=1 vs W_MATERIAL=100).
     Shrinking the foe's options *is* progress toward a blockade win.
  2. SUPPORT / azux. Reward own pieces with a friendly orthogonal neighbour;
     penalize lone pieces (Aristotle's unpaired piece = vulnerable). This is
     both source-faithful and the structure that produces blockades.
  3. TERMINAL-BLOCKADE PREFERENCE. At terminal nodes a blockade win is scored
     slightly above a material/annihilation win, so when both are reachable the
     search prefers the canonical finish.
  4. Material kept but DEMOTED (W_MAT 20, was 100) — it still backs the
     tie-break and annihilation, but no longer dominates.

(A Go-style influence/territory term — the Hoshi bridge — is the next lever to
prototype; left as a hook below.)

Weights are module-level and tunable; the point of #2 is to measure whether a
blockade-seeking eval moves the blockade share off 0% (run via
instrument_termination.py with this agent factory).
"""
from __future__ import annotations
import random

from latrones import ORTHO
from search import _geom, _order   # reuse geometry tables + capture-aware ordering

WIN = 1_000_000.0
BLOCKADE_BONUS = 5_000.0   # terminal blockade win preferred over material win

# --- eval weights (tunable) ---
W_MAT = 20.0       # demoted from 100
W_MOBDENY = 4.0    # per unit of FOE liberty removed — the major term
W_OWNMOB = 1.0     # mild self-preservation (don't get blockaded yourself)
W_SUPPORT = 2.0    # azux: connected own pieces good, lone own pieces bad
W_VULN = 8.0       # own piece one move from being bracketed
W_THREAT = 6.0     # foe piece one move from being bracketed
W_CENTRE = 0.15


def _liberty(b, neigh, i):
    """Cheap proxy for a piece's mobility: count of empty orthogonal exits.
    (A true slide-mobility count is O(ray) per piece and too slow in pure
    Python at every leaf; degree-of-freedom tracks it well enough to steer.)"""
    return sum(1 for n in neigh[i] if b[n] == 0)


def evaluation_v2(g, side):
    b = g.board
    foe = 3 - side
    neigh, axes, cdist = _geom(g.W, g.H)
    mat = own_mob = foe_mob = support = vuln = threat = centre = 0.0
    frozen = g.frozen
    for i in range(len(b)):
        v = b[i]
        if v == 0:
            continue
        lib = _liberty(b, neigh, i)
        # support: at least one friendly orthogonal neighbour
        supported = any(b[n] == v for n in neigh[i])
        # one-move-from-bracketed test (same shape as v1)
        want = foe if v == side else side
        hb = False
        for a, c in axes[i]:
            if (b[a] == want and b[c] == 0) or (b[c] == want and b[a] == 0):
                hb = True
                break
        if v == side:
            mat += 1
            own_mob += lib
            support += 1 if supported else -1
            vuln += 1 if hb else 0
            centre -= cdist[i]
        else:
            mat -= 1
            foe_mob += lib                       # we want this SMALL
            support -= 1 if supported else -1     # foe connectivity is bad for us
            threat += 1 if hb else 0
            centre += cdist[i]
    return (W_MAT * mat
            - W_MOBDENY * foe_mob               # <-- the lever: deny foe liberty
            + W_OWNMOB * own_mob
            + W_SUPPORT * support
            - W_VULN * vuln + W_THREAT * threat
            + W_CENTRE * centre)


def _terminal_value(g):
    """Score a finished game from the to-move side's perspective, preferring a
    blockade win over a material/annihilation win (lever 3)."""
    if g.result == 0:
        return 0.0
    win_for_to_move = (g.result == g.to_move)
    base = WIN
    # classify the win: blockade if the loser had no move before the cap and is
    # above the annihilation threshold.
    loser = 3 - g.result
    by_blockade = (g.move_plies < g.r.move_cap
                   and g.count(loser) > g.r.min_pieces)
    val = base + (BLOCKADE_BONUS if by_blockade else 0.0)
    return val if win_for_to_move else -val


class SearcherV2:
    def __init__(self, limit=6000):
        self.limit = limit
        self.nodes = 0

    def negamax(self, g, depth, alpha, beta):
        if g.result is not None:
            return _terminal_value(g)
        self.nodes += 1
        if depth == 0 or self.nodes > self.limit:
            return evaluation_v2(g, g.to_move)
        moves = g.legal_moves()
        if not moves:
            return -WIN
        best = -1e18
        for m in _order(g, moves):
            c = g.clone()
            c.apply(m)
            val = -self.negamax(c, depth - 1, -beta, -alpha)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best


class NegamaxAgentV2:
    """Same search shell as v1's NegamaxAgent, but the blockade-aware eval and
    terminal scoring. Placement still uses the cheap central-cluster heuristic
    (opening intelligence is Priority #5)."""
    def __init__(self, rng, depth=2, node_budget=6000, eps=0.03):
        self.rng = rng
        self.depth = depth
        self.node_budget = node_budget
        self.eps = eps

    def _place(self, g, moves):
        _, _, cdist = _geom(g.W, g.H)
        best, bs = [], 1e18
        for m in moves:
            d = cdist[m[1]]
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
        s = SearcherV2(self.node_budget)
        best, best_val = [], -1e18
        for m in _order(g, moves):
            c = g.clone()
            c.apply(m)
            val = -s.negamax(c, self.depth - 1, -1e18, 1e18)
            if val > best_val + 1e-9:
                best_val, best = val, [m]
            elif abs(val - best_val) <= 1e-9:
                best.append(m)
        return self.rng.choice(best)


def negamax_v2_factory(depth=2, node_budget=6000):
    def make(rng):
        return NegamaxAgentV2(rng, depth=depth, node_budget=node_budget)
    return make
