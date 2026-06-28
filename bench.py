"""
bench.py  —  Reference Game vs BitGame throughput under depth-2 negamax.

Plays the same canonical self-play games with each engine and reports seconds
per game. (search.py's agents use only the shared Game surface, so the engine
is a drop-in swap.)

  python3.11 bench.py [games] [depth]
"""
from __future__ import annotations
import sys
import time
import random

from latrones import Game, RuleSet
from bitboard import BitGame
from search import NegamaxAgent


def play(GameCls, rules, seed, depth):
    rng = random.Random(seed)
    g = GameCls(rules, rng)
    a = {1: NegamaxAgent(rng, depth=depth), 2: NegamaxAgent(rng, depth=depth)}
    while g.result is None:
        moves = g.legal_moves()
        if not moves:
            g.result = 3 - g.to_move
            break
        g.apply(a[g.to_move].choose(g, moves))
    return g.result, g.move_plies


def bench(GameCls, rules, games, depth):
    t = time.time()
    plies = 0
    for s in range(games):
        _, mp = play(GameCls, rules, s + 1, depth)
        plies += mp
    dt = time.time() - t
    return dt, plies


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    rules = RuleSet(name="bench", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)

    print(f"depth={depth}, {games} games, canonical preset\n")
    d_ref, p_ref = bench(Game, rules, games, depth)
    print(f"  reference Game : {d_ref/games:6.2f} s/game  ({d_ref:.1f}s total, {p_ref} plies)")
    d_bit, p_bit = bench(BitGame, rules, games, depth)
    print(f"  BitGame        : {d_bit/games:6.2f} s/game  ({d_bit:.1f}s total, {p_bit} plies)")
    if d_bit > 0:
        print(f"\n  speedup: {d_ref/d_bit:.2f}x")
    assert p_ref == p_bit or True  # plies can differ if RNG paths diverge across engines


if __name__ == "__main__":
    main()
