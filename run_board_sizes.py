"""
run_board_sizes.py  —  D4 experiment: does board size make BLOCKADE reachable?

The blockade verdict (FINDINGS-mcts.md, FINDINGS-opening.md) is unconditional on
the 8x8 canonical board. Hypothesis: blockade is a function of board geometry —
fewer escape squares and more wall/corner contact on a smaller or edge-denser
board should make total immobilisation easier. If a well-attested smaller board
(7x7, or 6x6/5x5) lifts the blockade share off zero, that is a principled,
source-licensed way to make the canonical victory condition real — and, as a
bonus, moves the board off the 8x8 chessboard.

Uses the blockade-AWARE agent (search_v2_bb) at depth-3 — the player that
actually tries to immobilise — so this is the most favourable test for blockade.
Density held ~constant (~50% of cells filled after placement).

  pypy3 run_board_sizes.py [games] [depth] [seed]
"""
from __future__ import annotations
import sys
import random
from collections import Counter

from latrones import RuleSet, wilson, mean_ci
from bitboard import BitGame
from instrument_termination import classify
from search_v2_bb import negamax_v2_bb_factory

# (W, H, pieces-per-side). Two axes: board SIZE (attested cluster 7x7..9x9 plus
# two smaller boards) and DENSITY (~50% fill vs a crowded ~72% fill, since
# blockade needs the loser pinned without a capturable bracket — crowding helps).
CONFIGS = [
    # ~50% fill
    (5, 5, 6), (6, 6, 9), (7, 7, 12), (7, 8, 14), (8, 8, 16), (9, 9, 20),
    # ~70%+ fill (crowded) — the edge-density probe
    (5, 5, 9), (6, 6, 13), (7, 7, 18),
]


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
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    factory = negamax_v2_bb_factory(depth=depth)

    print(f"D4 board-size sweep — blockade-aware agent depth-{depth}, "
          f"{games} games/size, seed={seed}\n")
    print(f"{'board':>7} {'pcs':>4} {'plies':>6} {'dec':>5} {'p1':>6} "
          f"{'BLOCKADE':>16} {'annih':>6} {'cap':>6}")
    for (W, H, pieces) in CONFIGS:
        rules = RuleSet(name=f"{W}x{H}", setup="placement", movement="slide",
                        victory="both", cap_rule="material",
                        width=W, height=H, pieces=pieces, move_cap=160)
        rng = random.Random(seed)
        reasons = Counter()
        plies, decided, p1wins = [], 0, 0
        for _ in range(games):
            reason, result, mp = play_classified(rules, factory, rng)
            reasons[reason] += 1
            plies.append(mp)
            if result in (1, 2):
                decided += 1
                if result == 1:
                    p1wins += 1
        blk = reasons.get("blockade", 0)
        ann = reasons.get("annihilation", 0)
        cap = reasons.get("cap_material", 0)
        pl = mean_ci(plies)[0]
        dec = decided / games
        p1 = (p1wins / decided) if decided else float("nan")
        blo, bhi = (wilson(blk, decided) if decided else (0, 0))
        print(f"{W}x{H:>2} {pieces:>4} {pl:>6.0f} {dec:>5.0%} {p1:>6.0%} "
              f"{blk:>3}/{decided:<3} {blk/decided if decided else 0:>5.0%}"
              f" ({blo:.0%}-{bhi:.0%}) {ann/decided if decided else 0:>5.0%}"
              f" {cap/decided if decided else 0:>5.0%}", flush=True)


if __name__ == "__main__":
    main()
