"""
test_parity.py  —  Prove BitGame == latrones.Game over random self-play.

For every (non-freeing) ruleset combination, board size and seed, play one
random game stepping BOTH engines in lockstep: at each ply assert the two
engines offer the identical set of legal moves, pick the same move (canonical
sort + shared RNG index), apply to both, and assert board / result / counts /
phase agree. Any divergence is reported with the ply and the diff.

This is the bitboard engine's correctness contract (the reference engine keeps
its 14 unit tests; the fast engine earns trust by matching it move-for-move).

Run:  python3.11 test_parity.py [games_per_combo] [seed0]
"""
from __future__ import annotations
import itertools
import random
import sys

from latrones import Game, RuleSet
from bitboard import BitGame


def snapshot(g):
    return (g.board, g.result, g.to_move, g.phase,
            g.count(1), g.count(2), g.move_plies)


def play_lockstep(rules, seed):
    """Return None on success, or a (ply, kind, detail) tuple on divergence."""
    ref = Game(rules, random.Random(seed))
    bit = BitGame(rules, random.Random(seed))
    chooser = random.Random(seed ^ 0x5DEECE66)
    ply = 0
    while ref.result is None and bit.result is None:
        rm = sorted(ref.legal_moves())
        bm = sorted(bit.legal_moves())
        if rm != bm:
            only_ref = [m for m in rm if m not in set(bm)]
            only_bit = [m for m in bm if m not in set(rm)]
            return (ply, "legal_moves",
                    f"only_ref={only_ref[:5]} only_bit={only_bit[:5]}")
        if not rm:
            break
        m = rm[chooser.randrange(len(rm))]
        ref.apply(m)
        bit.apply(m)
        if snapshot(ref) != snapshot(bit):
            return (ply, "state", f"move={m}\n  ref={snapshot(ref)}\n  bit={snapshot(bit)}")
        ply += 1
    if ref.result != bit.result:
        return (ply, "result", f"ref={ref.result} bit={bit.result}")
    return None


def main():
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    setups = ["placement", "array"]
    movements = ["slide", "step"]
    victories = ["blockade", "annihilate", "both"]
    sizes = [(7, 7), (8, 8), (9, 9), (7, 8)]

    combos = list(itertools.product(
        setups, movements, victories,
        [True, False],   # corner_capture
        [True, False],   # anti_shuffle
        ["material", "draw"],
        [False, True],   # leap
    ))

    total = fails = 0
    failures = []
    for (setup, mv, vic, corner, anti, caprule, leap) in combos:
        for (W, H) in sizes:
            pieces = min(8, (W * H) // 4)
            for s in range(per):
                seed = seed0 + s + 1009 * (W + 31 * H)
                rules = RuleSet(
                    name="parity", setup=setup, movement=mv, victory=vic,
                    corner_capture=corner, anti_shuffle=anti, cap_rule=caprule,
                    leap=leap, width=W, height=H, pieces=pieces, move_cap=80)
                total += 1
                div = play_lockstep(rules, seed)
                if div is not None:
                    fails += 1
                    if len(failures) < 12:
                        failures.append((rules.name, setup, mv, vic, corner,
                                         anti, caprule, leap, (W, H), seed, div))

    print(f"parity games played: {total}")
    print(f"divergences:         {fails}")
    if failures:
        print("\nFIRST DIVERGENCES:")
        for f in failures:
            (_, setup, mv, vic, corner, anti, caprule, leap, sz, seed, div) = f
            print(f"  setup={setup} mv={mv} vic={vic} corner={corner} "
                  f"anti={anti} cap={caprule} leap={leap} size={sz} seed={seed}")
            print(f"    ply={div[0]} {div[1]}: {div[2]}")
        sys.exit(1)
    print("\nALL PARITY CHECKS PASSED — BitGame matches latrones.Game.")


if __name__ == "__main__":
    main()
