"""
instrument_termination.py  —  Priority-stack #1.

The one number the HANDOFF asks for first: under STRONG self-play, what
fraction of games are actually decided by BLOCKADE versus run out to the
MATERIAL CAP? If it's mostly the cap, the canonical victory condition is
decorative and the eval/rules need to change.

The engine sets g.result but never records *why* (latrones.py:_check_end).
We reclassify each finished game from its final state:

  - cap_material : move cap hit, decided by pieces-standing (a tie-break win)
  - cap_draw     : move cap hit, equal material -> draw
  - blockade     : a side had no legal move before the cap
  - annihilation : a side reduced to <= min_pieces (only if victory allows it)

Run under the NegamaxAgent (depth-2, the project's "strong" agent) on the
canonical placement/slide preset. We report both victory="both" (blockade
primary + annihilation secondary, the full canonical game) and the pure
victory="blockade" preset, so the blockade share is unambiguous either way.
"""
from __future__ import annotations
import random
import sys
from collections import Counter

from latrones import Game, RuleSet, wilson
from search import negamax_factory


def classify(g: Game) -> str:
    """Reclassify a finished game by termination reason from final state."""
    r = g.r
    # Cap reached: _check_end scores by cap_rule when move_plies >= move_cap.
    if g.move_plies >= r.move_cap:
        c1, c2 = g.count(1), g.count(2)
        return "cap_draw" if c1 == c2 else "cap_material"
    if g.result == 0:
        return "draw_other"
    # A side won before the cap. Annihilation if the loser is at/under the
    # threshold AND the ruleset counts that as a win; otherwise blockade.
    loser = 3 - g.result
    if r.victory in ("annihilate", "both") and g.count(loser) <= r.min_pieces:
        return "annihilation"
    return "blockade"


def play_classified(rules, factory, rng):
    g = Game(rules, rng)
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
    decided = 0
    plies = []
    for _ in range(games):
        reason, result, margin, mp = play_classified(rules, factory, rng)
        reasons[reason] += 1
        plies.append(mp)
        if result in (1, 2):
            decided += 1
    return reasons, decided, plies


def report(title, rules, reasons, decided, plies, games):
    print(f"\n=== {title} ===")
    print(f"  preset: setup={rules.setup} movement={rules.movement} "
          f"victory={rules.victory} cap_rule={rules.cap_rule} "
          f"{rules.width}x{rules.height} pieces={rules.pieces} "
          f"move_cap={rules.move_cap}")
    print(f"  games={games}  mean_plies={sum(plies)/len(plies):.0f}")
    # The headline: blockade share among *decided* games, with a Wilson CI.
    blk = reasons.get("blockade", 0)
    cap_win = reasons.get("cap_material", 0)
    ann = reasons.get("annihilation", 0)
    if decided:
        lo, hi = wilson(blk, decided)
        print(f"  --- decided games: {decided} ---")
        print(f"  BLOCKADE share of decided : {blk}/{decided} = "
              f"{blk/decided:.1%}  (95% CI {lo:.1%}-{hi:.1%})")
        print(f"  cap-material  of decided  : {cap_win}/{decided} = {cap_win/decided:.1%}")
        print(f"  annihilation  of decided  : {ann}/{decided} = {ann/decided:.1%}")
    else:
        print("  no decided games")
    print(f"  full breakdown: {dict(reasons)}")
    verdict = ("CANONICAL VICTORY IS REAL" if decided and blk / decided >= 0.5
               else "CANONICAL VICTORY MAY BE DECORATIVE (cap is doing the work)")
    print(f"  >>> {verdict}")


def main():
    # args: [neg_games] [seed] [depth] [heur_games]
    neg_games = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    heur_games = int(sys.argv[4]) if len(sys.argv) > 4 else 100

    # The full canonical game: blockade primary, annihilation secondary,
    # material tie-break at the cap. (The pure-blockade preset gave identical
    # numbers in the smoke run, since annihilation never triggers.)
    rules = RuleSet(name="canon-both", setup="placement", movement="slide",
                    victory="both", cap_rule="material",
                    width=8, height=8, pieces=16, move_cap=160)

    from latrones import default_agent  # capture-greedy 1-ply HeuristicAgent

    print(f"Canonical preset, seed={seed}. The question: how often does a game "
          f"actually end by BLOCKADE vs. grind to the material cap?\n")

    # Weak agent — fast, high volume.
    reasons, decided, plies = run(rules, default_agent, heur_games, seed)
    report(f"WEAK self-play: HeuristicAgent (1-ply greedy), {heur_games} games",
           rules, reasons, decided, plies, heur_games)

    # Strong agent — slow (~40s/game at depth 2), so fewer games.
    factory = negamax_factory(depth=depth, node_budget=6000)
    reasons, decided, plies = run(rules, factory, neg_games, seed)
    report(f"STRONG self-play: NegamaxAgent depth={depth}, {neg_games} games",
           rules, reasons, decided, plies, neg_games)


if __name__ == "__main__":
    main()
