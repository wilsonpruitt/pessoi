"""
bench2.py  —  (1) verify evaluation_bb == search.evaluation numerically, then
(2) time reference negamax (list engine) vs bitboard-native negamax.

  python3.11 bench2.py [games] [depth]
"""
from __future__ import annotations
import sys
import time
import random

from latrones import Game, RuleSet
from bitboard import BitGame
from search import NegamaxAgent, evaluation as eval_ref
from search_bb import NegamaxAgentBB, evaluation_bb


def eval_parity(trials=4000, seed=7):
    rng = random.Random(seed)
    W, H = 8, 8
    N = W * H
    ref = Game(RuleSet(setup="array", width=W, height=H, pieces=1), random.Random(0))
    bit = BitGame(RuleSet(setup="array", width=W, height=H, pieces=1), random.Random(0))
    worst = 0.0
    for _ in range(trials):
        cells = list(range(N))
        rng.shuffle(cells)
        k = rng.randint(2, N)
        board = [0] * N
        for c in cells[:k]:
            board[c] = rng.choice((1, 2))
        ref.board = board
        bit.board = board
        for side in (1, 2):
            a = eval_ref(ref, side)
            b = evaluation_bb(bit, side)
            worst = max(worst, abs(a - b))
            if abs(a - b) > 1e-6:
                return False, worst, (board, side, a, b)
    return True, worst, None


def play(GameCls, AgentCls, rules, seed, depth):
    rng = random.Random(seed)
    g = GameCls(rules, rng)
    a = {1: AgentCls(rng, depth=depth), 2: AgentCls(rng, depth=depth)}
    while g.result is None:
        moves = g.legal_moves()
        if not moves:
            g.result = 3 - g.to_move
            break
        g.apply(a[g.to_move].choose(g, moves))
    return g.move_plies


def bench(GameCls, AgentCls, rules, games, depth):
    t = time.time()
    plies = 0
    for s in range(games):
        plies += play(GameCls, AgentCls, rules, s + 1, depth)
    return time.time() - t, plies


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    ok, worst, detail = eval_parity()
    print(f"eval parity: {'OK' if ok else 'FAIL'}  (max abs diff {worst:.2e})")
    if not ok:
        print(f"  divergence: {detail}")
        sys.exit(1)

    rules = RuleSet(name="bench", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)
    print(f"\ndepth={depth}, {games} games, canonical preset\n")
    d_ref, p_ref = bench(Game, NegamaxAgent, rules, games, depth)
    print(f"  reference (list)   : {d_ref/games:6.2f} s/game  ({d_ref:.1f}s, {p_ref} plies)")
    d_bb, p_bb = bench(BitGame, NegamaxAgentBB, rules, games, depth)
    print(f"  bitboard-native    : {d_bb/games:6.2f} s/game  ({d_bb:.1f}s, {p_bb} plies)")
    if d_bb > 0:
        print(f"\n  speedup: {d_ref/d_bb:.2f}x")


if __name__ == "__main__":
    main()
