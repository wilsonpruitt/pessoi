"""
probe_weights.py  —  Does an AGGRESSIVE blockade-seeking weight set move the
blockade share off 0% at depth-2, or is the horizon the real blocker?

Cranks mobility-denial and drops the vulnerability penalty (so the agent will
close in on the enemy to encircle, accepting exposure). If blockades appear,
the v2 default weights were too timid; if not, depth-2 simply can't plan the
multi-move encirclement and #2's payoff is gated on deeper search (#3) or an
eval-free MCTS (#6).
"""
from __future__ import annotations
import sys

import search_v2 as sv2
from latrones import RuleSet
from instrument_termination import run, report


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    # aggressive encirclement profile
    sv2.W_MOBDENY = 14.0   # was 4
    sv2.W_VULN = 1.0       # was 8  (tolerate exposure to close in)
    sv2.W_MAT = 8.0        # was 20 (care even less about hoarding)
    sv2.W_SUPPORT = 3.0    # was 2

    rules = RuleSet(name="canon-both", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)

    print(f"AGGRESSIVE v2 weights — W_MOBDENY={sv2.W_MOBDENY} W_VULN={sv2.W_VULN} "
          f"W_MAT={sv2.W_MAT}; depth={depth}, {games} games, seed={seed}\n")
    r, d, p = run(rules, sv2.negamax_v2_factory(depth=depth, node_budget=6000),
                  games, seed)
    report("v2 AGGRESSIVE (encircle-at-all-costs)", rules, r, d, p, games)


if __name__ == "__main__":
    main()
