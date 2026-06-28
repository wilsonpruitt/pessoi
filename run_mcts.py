"""
run_mcts.py  —  MCTS-UCT self-play on the canonical preset (Priority #6).

The question: does an eval-free MCTS agent ever win by BLOCKADE, or does it too
return ~0% — making the verdict agent-invariant across heuristic + alpha-beta +
MCTS?

  pypy3 run_mcts.py [games] [iterations] [seed]
"""
from __future__ import annotations
import sys
import random
from collections import Counter

from latrones import RuleSet, wilson, mean_ci
from bitboard import BitGame
from instrument_termination import classify
from search_mcts import mcts_factory


def play_classified(rules, factory, rng):
    g = BitGame(rules, rng)
    agents = {1: factory(rng), 2: factory(rng)}
    while g.result is None:
        moves = g.legal_moves()
        if not moves:
            g.result = 3 - g.to_move
            break
        g.apply(agents[g.to_move].choose(g, moves))
    return classify(g), g.result, g.move_plies


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rollout_cap = int(sys.argv[4]) if len(sys.argv) > 4 else None
    rollout = sys.argv[5] if len(sys.argv) > 5 else "capture"

    rules = RuleSet(name="canon-both", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)
    factory = mcts_factory(iterations=iters, rollout_cap=rollout_cap,
                           rollout=rollout)
    print(f"rollout={rollout} rollout_cap={rollout_cap} iters={iters}\n", flush=True)

    rng = random.Random(seed)
    reasons = Counter()
    plies, decided, p1wins = [], 0, 0
    for i in range(games):
        reason, result, mp = play_classified(rules, factory, rng)
        reasons[reason] += 1
        plies.append(mp)
        if result in (1, 2):
            decided += 1
            if result == 1:
                p1wins += 1
        print(f"  game {i+1}/{games}: {reason} (result={result}, {mp} plies)",
              flush=True)

    blk = reasons.get("blockade", 0)
    ann = reasons.get("annihilation", 0)
    cap_w = reasons.get("cap_material", 0)
    draws = reasons.get("cap_draw", 0) + reasons.get("draw_other", 0)
    pl_m, pl_lo, pl_hi = mean_ci(plies)
    print(f"\n=== MCTS-UCT self-play, {iters} iters/move, {games} games ===")
    print(f"  mean_plies   = {pl_m:.0f} (95% CI {pl_lo:.0f}-{pl_hi:.0f})")
    print(f"  draw_rate    = {draws/games:.1%}")
    print(f"  decisiveness = {decided/games:.1%}")
    if decided:
        print(f"  p1_winrate   = {p1wins/decided:.1%} (Wilson {wilson(p1wins, decided)[0]:.1%}-{wilson(p1wins, decided)[1]:.1%})")
        lo, hi = wilson(blk, decided)
        print(f"  BLOCKADE / decided     = {blk}/{decided} = {blk/decided:.1%} (Wilson {lo:.1%}-{hi:.1%})")
        print(f"  annihilation / decided = {ann}/{decided} = {ann/decided:.1%}")
        print(f"  material-cap / decided = {cap_w}/{decided} = {cap_w/decided:.1%}")
    print(f"  breakdown: {dict(reasons)}")


if __name__ == "__main__":
    main()
