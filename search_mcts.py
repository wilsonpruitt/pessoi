"""
search_mcts.py  —  Eval-free MCTS-UCT agent (Priority-stack #6).

The decisive remaining witness on the blockade question. Alpha-beta needs a good
static eval and blockade is exactly what's hard to evaluate statically; MCTS
needs no eval, only rollouts, so it is the architecture the HANDOFF argues is
best suited to a positional siege — and an independent third architecture. If it
ALSO returns ~0% blockade, the verdict (blockade ~unreachable under the canonical
rules) becomes agent-invariant across heuristic + alpha-beta + MCTS.

Design:
  * Pure-random rollouts to a true terminal (the game's move cap bounds them) —
    genuinely eval-free, no capture/heuristic bias in the playout.
  * UCT tree policy; `iterations` is the strength dial (and the natural sparring
    difficulty knob, #7).
  * Phase-0 placement uses the SAME central-cluster heuristic as the negamax
    agents, so the opening is held fixed across all agents and the only variable
    is the movement-phase search. MCTS runs in the movement phase only.

Runs on BitGame (clone() is a cheap int copy). Use PyPy for volume.
"""
from __future__ import annotations
import math
import random

from search_bb import _cdist, _capture_count_bb


class _Node:
    __slots__ = ("state", "parent", "move", "mover", "children",
                 "untried", "visits", "wins")

    def __init__(self, state, parent, move, mover):
        self.state = state
        self.parent = parent
        self.move = move
        self.mover = mover                     # player who moved INTO this node
        self.children = []
        self.untried = None                    # filled lazily
        self.visits = 0
        self.wins = 0.0                        # from `mover`'s perspective


class MCTSAgent:
    def __init__(self, rng, iterations=600, c=1.4, rollout_cap=None,
                 rollout="capture", capture_bias=0.8):
        self.rng = rng
        self.iterations = iterations
        self.c = c
        self.rollout_cap = rollout_cap         # optional extra ply cap on rollouts
        # rollout policy: "random" (pure, eval-free but noisy/passive at low
        # budget) or "capture" (heavy playout — bias toward capturing moves so
        # rollouts resolve decisively; still NO static board eval, only a move
        # preference, so MCTS remains an architecturally-independent witness).
        self.rollout = rollout
        self.capture_bias = capture_bias

    # -- phase-0 placement: identical to the negamax agents ------------------ #
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

    # -- rollout: pure random play to terminal ------------------------------- #
    def _rollout(self, state):
        g = state.clone()
        steps = 0
        rng = self.rng
        capture = (self.rollout == "capture")
        bias = self.capture_bias
        while g.result is None:
            moves = g.legal_moves()
            if not moves:
                g.result = 3 - g.to_move
                break
            if capture and rng.random() < bias:
                p = g.to_move
                caps = [m for m in moves
                        if m[0] == "move" and _capture_count_bb(g, m[1], m[2], p)]
                m = rng.choice(caps) if caps else moves[rng.randrange(len(moves))]
            else:
                m = moves[rng.randrange(len(moves))]
            g.apply(m)
            steps += 1
            if self.rollout_cap is not None and steps >= self.rollout_cap:
                c1, c2 = g.count(1), g.count(2)
                g.result = 1 if c1 > c2 else (2 if c2 > c1 else 0)
                break
        return g.result

    def _reward(self, result, mover):
        if result == 0:
            return 0.5
        return 1.0 if result == mover else 0.0

    def _uct_child(self, node):
        logN = math.log(node.visits)
        best, best_score = None, -1e18
        for ch in node.children:
            score = ch.wins / ch.visits + self.c * math.sqrt(logN / ch.visits)
            if score > best_score:
                best_score, best = score, ch
        return best

    def choose(self, g, moves):
        if g.phase == 0:
            return self._place(g, moves)

        root = _Node(g.clone(), None, None, None)
        root.untried = list(moves)

        for _ in range(self.iterations):
            node = root
            # --- selection ---
            while not node.untried and node.children:
                node = self._uct_child(node)
            # --- expansion ---
            if node.untried:
                m = node.untried.pop(self.rng.randrange(len(node.untried)))
                child_state = node.state.clone()
                child_state.apply(m)
                child = _Node(child_state, node, m, node.state.to_move)
                if child_state.result is None:
                    child.untried = child_state.legal_moves()
                else:
                    child.untried = []
                node.children.append(child)
                node = child
            # --- simulation ---
            result = self._rollout(node.state)
            # --- backpropagation ---
            while node is not None:
                node.visits += 1
                if node.mover is not None:
                    node.wins += self._reward(result, node.mover)
                node = node.parent

        # robust child: most-visited
        best = max(root.children, key=lambda ch: ch.visits)
        return best.move


def mcts_factory(iterations=600, c=1.4, rollout_cap=None,
                 rollout="capture", capture_bias=0.8):
    def make(rng):
        return MCTSAgent(rng, iterations=iterations, c=c, rollout_cap=rollout_cap,
                         rollout=rollout, capture_bias=capture_bias)
    return make
