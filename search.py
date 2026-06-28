"""
search.py  —  Stronger agent for latrones: alpha-beta negamax with a
mobility/blockade/vulnerability-aware evaluation, optimised for sweep use.

Tractability measures:
  * placement (vagi) phase uses cheap heuristic placement, not search
    (searching 64-wide placement trees is the dominant cost);
  * neighbour/axis index tables are precomputed per board size;
  * each move decision has a hard node budget; beyond it the search
    degrades gracefully to the static evaluation.
"""
from __future__ import annotations
import random
from latrones import Game, ORTHO

WIN = 1_000_000.0
W_MATERIAL = 100.0
W_MOBILITY = 1.0
W_VULN = 8.0
W_THREAT = 6.0
W_CENTRE = 0.15

_NEIGH = {}
_AXES = {}
_CDIST = {}


def _geom(W, H):
    key = (W, H)
    if key in _NEIGH:
        return _NEIGH[key], _AXES[key], _CDIST[key]
    neigh, axes, cdist = [], [], []
    cx, cy = (W - 1) / 2, (H - 1) / 2
    for i in range(W * H):
        x, y = i % W, i // W
        ns = []
        for dx, dy in ORTHO:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                ns.append(ny * W + nx)
        neigh.append(ns)
        ax = []
        for dx, dy in ((1, 0), (0, 1)):
            ax_, ay_ = x + dx, y + dy
            bx_, by_ = x - dx, y - dy
            if 0 <= ax_ < W and 0 <= ay_ < H and 0 <= bx_ < W and 0 <= by_ < H:
                ax.append((ay_ * W + ax_, by_ * W + bx_))
        axes.append(ax)
        cdist.append(abs(x - cx) + abs(y - cy))
    _NEIGH[key], _AXES[key], _CDIST[key] = neigh, axes, cdist
    return neigh, axes, cdist


def evaluation(g, side):
    b = g.board
    foe = 3 - side
    neigh, axes, cdist = _geom(g.W, g.H)
    mat = mob = vuln = threat = 0.0
    centre = 0.0
    for i in range(len(b)):
        v = b[i]
        if v == 0:
            continue
        has_space = any(b[n] == 0 for n in neigh[i])
        want = foe if v == side else side
        hb = False
        for a, c in axes[i]:
            if (b[a] == want and b[c] == 0) or (b[c] == want and b[a] == 0):
                hb = True
                break
        if v == side:
            mat += 1
            mob += 1 if has_space else 0
            vuln += 1 if hb else 0
            centre -= cdist[i]
        else:
            mat -= 1
            mob -= 1 if has_space else 0
            threat += 1 if hb else 0
            centre += cdist[i]
    return (W_MATERIAL * mat + W_MOBILITY * mob
            - W_VULN * vuln + W_THREAT * threat + W_CENTRE * centre)


def _capture_count(g, frm, to, p):
    b = g.board
    of, ot = b[frm], b[to]
    b[frm], b[to] = 0, p
    n, foe = 0, 3 - p
    x, y = to % g.W, to // g.W
    for dx, dy in ORTHO:
        ex, ey, bx, by = x + dx, y + dy, x + 2 * dx, y + 2 * dy
        if 0 <= ex < g.W and 0 <= ey < g.H and 0 <= bx < g.W and 0 <= by < g.H:
            e, bb = ey * g.W + ex, by * g.W + bx
            if b[e] == foe and b[bb] == p and bb not in g.frozen:
                n += 1
    b[frm], b[to] = of, ot
    return n


def _order(g, moves):
    p = g.to_move
    return sorted(
        moves,
        key=lambda m: _capture_count(g, m[1], m[2], p) if m[0] == "move" else 0,
        reverse=True,
    )


class Searcher:
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
            return evaluation(g, g.to_move)
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


class NegamaxAgent:
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
        s = Searcher(self.node_budget)
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


def negamax_factory(depth=2, node_budget=6000):
    def make(rng):
        return NegamaxAgent(rng, depth=depth, node_budget=node_budget)
    return make


if __name__ == "__main__":
    import time
    from latrones import RuleSet, evaluate
    rs = RuleSet(name="bench", setup="array", movement="slide",
                 victory="blockade", width=8, height=8, pieces=16, move_cap=160)
    t = time.time()
    r = evaluate(rs, games=4, seed=1, agent_factory=negamax_factory(2))
    print(f"{(time.time()-t)/4:.2f}s/game  draw={r['draw_rate']:.2f} "
          f"dec={r['decisiveness']:.2f} plies={r['mean_plies']:.0f}")
