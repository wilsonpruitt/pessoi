"""
search_open.py  —  Competent opening play (Priority-stack #5, part A).

Every agent so far places with the cheap central-cluster heuristic — "opening a
chess game by always pushing the d-pawn" (HANDOFF #5). That leaves two things
unmeasured: opening quality, and the one un-closed door on the blockade verdict
(maybe blockade needs an opening none of the blind agents set up).

This agent gives the placement phase a real 1-ply policy: score each candidate
drop by the blockade-aware eval (evaluation_v2_bb) of the resulting position from
the placer's perspective, and take the best (with eps for variety). That eval
rewards support/azux (connected, mutually-defending chains) and penalises lone,
vulnerable pieces — exactly the structure the sources tie to blockade — so an
opening built to maximise it is the fairest test of "does a good opening enable
blockade?". Movement play is unchanged (the v2 blockade-aware negamax).

If blockade share stays ~0 even with this opening, the door is closed: blockade
is unreachable under the canonical rules, opening intelligence included.
"""
from __future__ import annotations

from search_v2_bb import NegamaxAgentV2BB, evaluation_v2_bb


class NegamaxV2SmartOpen(NegamaxAgentV2BB):
    """v2 blockade-aware movement search + 1-ply blockade-aware placement."""

    def __init__(self, rng, depth=2, node_budget=6000, eps=0.03, open_eps=0.10):
        super().__init__(rng, depth=depth, node_budget=node_budget, eps=eps)
        self.open_eps = open_eps

    def _place(self, g, moves):
        if self.rng.random() < self.open_eps:
            return self.rng.choice(moves)
        side = g.to_move
        best, best_val = [], -1e18
        for m in moves:
            c = g.clone()
            c.apply(m)
            v = evaluation_v2_bb(c, side)
            if v > best_val + 1e-9:
                best_val, best = v, [m]
            elif abs(v - best_val) <= 1e-9:
                best.append(m)
        return self.rng.choice(best)


def smart_open_factory(depth=2, node_budget=6000, open_eps=0.10):
    def make(rng):
        return NegamaxV2SmartOpen(rng, depth=depth, node_budget=node_budget,
                                  open_eps=open_eps)
    return make
