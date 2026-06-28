"""
run_opening.py  —  Priority #5: competent-opening sweep + opening-book mining.

Runs self-play with the smart-opening agent (search_open) and:
  1. answers the scientific question — with a competent opening, does BLOCKADE
     finally appear, or is the door closed (verdict holds)?
  2. mines the placements into a petteia opening book — per-cell drop frequency
     heatmaps and the most common opening cells. No one has an opening book for a
     reconstructed ancient game; it falls out of the engine once the agent plays
     the opening competently.

  pypy3 run_opening.py [games] [depth] [seed]
"""
from __future__ import annotations
import sys
import random
from collections import Counter

from latrones import RuleSet, wilson, mean_ci
from bitboard import BitGame
from instrument_termination import classify
from search_open import smart_open_factory


def play_record(rules, factory, rng):
    """Play one game; record placement cells per player and classify the end."""
    g = BitGame(rules, rng)
    agents = {1: factory(rng), 2: factory(rng)}
    p_cells = {1: [], 2: []}
    while g.result is None:
        moves = g.legal_moves()
        if not moves:
            g.result = 3 - g.to_move
            break
        p = g.to_move
        action = agents[p].choose(g, moves)
        if action[0] == "place":
            p_cells[p].append(action[1])
        g.apply(action)
    return classify(g), g.result, g.move_plies, p_cells


def heatmap(counts, W, H, games):
    """ASCII heatmap, 0-9 per cell = round(9 * occupancy frequency). Printed with
    y=H-1 at top (natural orientation; player 1 fills from y=0 = bottom)."""
    lines = []
    for y in range(H - 1, -1, -1):
        row = []
        for x in range(W):
            f = counts[y * W + x] / games
            row.append(str(min(9, round(9 * f))) if f > 0 else ".")
        lines.append(" ".join(row))
    return "\n".join("    " + ln for ln in lines)


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    rules = RuleSet(name="canon-both", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)
    W, H, N = rules.width, rules.height, rules.cells()
    factory = smart_open_factory(depth=depth)

    rng = random.Random(seed)
    reasons = Counter()
    plies, decided, p1wins = [], 0, 0
    occ = {1: [0] * N, 2: [0] * N}
    first_drop = {1: Counter(), 2: Counter()}

    print(f"Smart-opening sweep: {games} games, depth-{depth}, seed={seed}\n", flush=True)
    for i in range(games):
        reason, result, mp, p_cells = play_record(rules, factory, rng)
        reasons[reason] += 1
        plies.append(mp)
        if result in (1, 2):
            decided += 1
            if result == 1:
                p1wins += 1
        for p in (1, 2):
            for c in p_cells[p]:
                occ[p][c] += 1
            if p_cells[p]:
                first_drop[p][p_cells[p][0]] += 1

    # --- scientific result ---
    blk = reasons.get("blockade", 0)
    ann = reasons.get("annihilation", 0)
    cap_w = reasons.get("cap_material", 0)
    draws = reasons.get("cap_draw", 0) + reasons.get("draw_other", 0)
    pl_m, pl_lo, pl_hi = mean_ci(plies)
    print("=== TERMINATION (does a competent opening enable blockade?) ===")
    print(f"  mean_plies   = {pl_m:.0f} (95% CI {pl_lo:.0f}-{pl_hi:.0f})")
    print(f"  draw_rate    = {draws/games:.1%}   decisiveness = {decided/games:.1%}")
    if decided:
        print(f"  p1_winrate   = {p1wins/decided:.1%} (Wilson {wilson(p1wins, decided)[0]:.1%}-{wilson(p1wins, decided)[1]:.1%})")
        lo, hi = wilson(blk, decided)
        print(f"  BLOCKADE / decided     = {blk}/{decided} = {blk/decided:.1%} (Wilson {lo:.1%}-{hi:.1%})")
        print(f"  annihilation / decided = {ann}/{decided} = {ann/decided:.1%}")
        print(f"  material-cap / decided = {cap_w}/{decided} = {cap_w/decided:.1%}")
    print(f"  breakdown: {dict(reasons)}")

    # --- opening book ---
    def cellname(c):
        return f"{chr(ord('a') + c % W)}{c // W + 1}"
    print("\n=== OPENING BOOK ===")
    print("  Player 1 placement frequency (0-9 = round(9*freq); . = never):")
    print(heatmap(occ[1], W, H, games))
    print("  Player 2 placement frequency:")
    print(heatmap(occ[2], W, H, games))
    print("  Most common FIRST drop, player 1:")
    for c, n in first_drop[1].most_common(5):
        print(f"    {cellname(c)}: {n}/{games} ({n/games:.0%})")
    print("  Most common FIRST drop, player 2:")
    for c, n in first_drop[2].most_common(5):
        print(f"    {cellname(c)}: {n}/{games} ({n/games:.0%})")


if __name__ == "__main__":
    main()
