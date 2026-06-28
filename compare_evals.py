"""
compare_evals.py  —  A/B the v1 (material-first) and v2 (blockade-aware) evals.

The measurable test Priority #2 must pass: does a blockade-seeking eval move the
blockade share off the 0% baseline established in FINDINGS-blockade-vs-cap.md?

Runs both agents on the SAME canonical preset and seed and reports each one's
termination breakdown. Strong (depth-2) negamax is ~40s/game, so keep n modest.

  python3.11 -u compare_evals.py [games] [seed] [depth]
"""
from __future__ import annotations
import sys

from latrones import RuleSet
from search import negamax_factory
from search_v2 import negamax_v2_factory
from instrument_termination import run, report


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    rules = RuleSet(name="canon-both", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)

    print(f"A/B eval comparison — canonical preset, depth={depth}, "
          f"{games} games, seed={seed}\n")

    r1, d1, p1 = run(rules, negamax_factory(depth=depth, node_budget=6000),
                     games, seed)
    report("v1  material-first (baseline)", rules, r1, d1, p1, games)

    r2, d2, p2 = run(rules, negamax_v2_factory(depth=depth, node_budget=6000),
                     games, seed)
    report("v2  blockade-aware (mobility-denial + support + terminal bonus)",
           rules, r2, d2, p2, games)

    b1 = r1.get("blockade", 0)
    b2 = r2.get("blockade", 0)
    print(f"\n>>> blockade games: v1={b1}/{games}  ->  v2={b2}/{games}")


if __name__ == "__main__":
    main()
