"""
run_sweep_depth3.py  —  Priority #4 (the depth-3 sweep) + the #2 follow-up.

Two questions in one run, now tractable on the bitboard engine:
  #4  Tighten the strong-play health metrics at depth-3 (draw rate, p1 bias,
      decisiveness, plies) with CIs.
  #2  Does deeper search finally produce BLOCKADES? Run BOTH the material-first
      (v1) and the blockade-aware (v2) evals at depth-3 and compare the
      termination breakdown against the 0% depth-2 baseline.

Runs on BitGame; depth and game count are CLI args. Use PyPy for the full run:
    pypy3 run_sweep_depth3.py 100 3 1
CPython works too but is ~10x slower at depth-3.
"""
from __future__ import annotations
import sys
import random
from collections import Counter

from latrones import RuleSet, wilson, mean_ci
from bitboard import BitGame
from instrument_termination import classify
from search_bb import negamax_bb_factory, evaluation_bb
from search_v2_bb import negamax_v2_bb_factory, evaluation_v2_bb


def eval_v2_parity(trials=3000, seed=11):
    """Confirm the bitboard v2 eval matches the list v2 eval before trusting it."""
    from latrones import Game
    import search_v2
    rng = random.Random(seed)
    W = H = 8
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
            a = search_v2.evaluation_v2(ref, side)
            b = evaluation_v2_bb(bit, side)
            worst = max(worst, abs(a - b))
            if abs(a - b) > 1e-6:
                return False, worst
    return True, worst


def play_classified(rules, factory, rng):
    g = BitGame(rules, rng)
    agents = {1: factory(rng), 2: factory(rng)}
    while g.result is None:
        moves = g.legal_moves()
        if not moves:
            g.result = 3 - g.to_move
            break
        g.apply(agents[g.to_move].choose(g, moves))
    return classify(g), g.result, g.count(1) - g.count(2), g.move_plies


def run(rules, factory, games, seed):
    rng = random.Random(seed)
    reasons = Counter()
    plies, decided, p1wins = [], 0, 0
    for _ in range(games):
        reason, result, margin, mp = play_classified(rules, factory, rng)
        reasons[reason] += 1
        plies.append(mp)
        if result in (1, 2):
            decided += 1
            if result == 1:
                p1wins += 1
    return reasons, decided, p1wins, plies


def report(title, reasons, decided, p1wins, plies, games):
    blk = reasons.get("blockade", 0)
    ann = reasons.get("annihilation", 0)
    cap_w = reasons.get("cap_material", 0)
    draws = reasons.get("cap_draw", 0) + reasons.get("draw_other", 0)
    pl_m, pl_lo, pl_hi = mean_ci(plies)
    print(f"\n=== {title} ===")
    print(f"  games={games}  mean_plies={pl_m:.0f} (95% CI {pl_lo:.0f}-{pl_hi:.0f})")
    print(f"  draw_rate    = {draws/games:.1%}  (Wilson {wilson(draws, games)[0]:.1%}-{wilson(draws, games)[1]:.1%})")
    print(f"  decisiveness = {decided/games:.1%}")
    if decided:
        print(f"  p1_winrate   = {p1wins/decided:.1%}  (Wilson {wilson(p1wins, decided)[0]:.1%}-{wilson(p1wins, decided)[1]:.1%})")
    if decided:
        lo, hi = wilson(blk, decided)
        print(f"  BLOCKADE / decided    = {blk}/{decided} = {blk/decided:.1%}  (Wilson {lo:.1%}-{hi:.1%})")
        print(f"  annihilation / decided= {ann}/{decided} = {ann/decided:.1%}")
        print(f"  material-cap / decided= {cap_w}/{decided} = {cap_w/decided:.1%}")
    print(f"  breakdown: {dict(reasons)}")


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    ok, worst = eval_v2_parity()
    print(f"v2 eval parity: {'OK' if ok else 'FAIL'} (max abs diff {worst:.2e})")
    if not ok:
        sys.exit(1)

    rules = RuleSet(name="canon-both", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)
    print(f"\nDepth-{depth} sweep, {games} games/agent, seed={seed}, canonical preset")
    print("Baseline (depth-2): blockade 0% for both agents.")

    r, d, w, p = run(rules, negamax_bb_factory(depth=depth), games, seed)
    report(f"v1 material-first, depth-{depth}", r, d, w, p, games)

    r, d, w, p = run(rules, negamax_v2_bb_factory(depth=depth), games, seed)
    report(f"v2 blockade-aware, depth-{depth}", r, d, w, p, games)


if __name__ == "__main__":
    main()
