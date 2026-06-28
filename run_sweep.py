"""
run_sweep.py  —  Sweep the underdetermined ([D]) rules of our two
reconstructions and report game-health metrics for each candidate.

The two anchors are the defaults from the reconstruction document:
  Reconstruction A (LATRVNCVLI): placement phase, slide, corner capture,
      Piso variant (immediate removal), victory = annihilate-or-blockade.
  Reconstruction B (PETTEIA):    opposed array, slide, corner capture,
      blockade foregrounded.

Each row varies ONE fork from its anchor so the effect is legible.

Run:  python3 run_sweep.py [games] [seed]
"""
import sys, csv, json
from latrones import RuleSet, evaluate

GAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 7
CAP = 200

# --- LATRVNCVLI (Roman) anchor + forks ------------------------------------- #
LATRUN = [
    RuleSet(name="L0 anchor (Piso)", setup="placement", movement="slide",
            corner_capture=True, freeing=False, victory="both",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="L1 Seneca (freeing)", setup="placement", movement="slide",
            corner_capture=True, freeing=True, victory="both",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="L2 step move", setup="placement", movement="step",
            corner_capture=True, freeing=False, victory="both",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="L3 corners safe", setup="placement", movement="slide",
            corner_capture=False, freeing=False, victory="both",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="L4 annihilate only", setup="placement", movement="slide",
            corner_capture=True, freeing=False, victory="annihilate",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="L5 7x8 board", setup="placement", movement="slide",
            corner_capture=True, freeing=False, victory="both",
            width=8, height=7, pieces=14, move_cap=CAP),
]

# --- PETTEIA / POLIS (Greek) anchor + forks -------------------------------- #
PETTEIA = [
    RuleSet(name="P0 anchor (blockade)", setup="array", movement="slide",
            corner_capture=True, freeing=False, victory="blockade",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="P1 both win-conds", setup="array", movement="slide",
            corner_capture=True, freeing=False, victory="both",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="P2 step move", setup="array", movement="step",
            corner_capture=True, freeing=False, victory="blockade",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="P3 placement setup", setup="placement", movement="slide",
            corner_capture=True, freeing=False, victory="blockade",
            width=8, height=8, pieces=16, move_cap=CAP),
    RuleSet(name="P4 9x9 board", setup="array", movement="slide",
            corner_capture=True, freeing=False, victory="blockade",
            width=9, height=9, pieces=18, move_cap=CAP),
]

HEADER = ["ruleset", "draw", "decisive", "p1_win", "plies", "branch",
          "open_H", "n_open"]


def fmt(r):
    return [r["name"], f"{r['draw_rate']:.2f}", f"{r['decisiveness']:.2f}",
            f"{r['p1_winrate']:.2f}", f"{r['mean_plies']:.0f}",
            f"{r['mean_branching']:.1f}", f"{r['opening_entropy']:.2f}",
            r["distinct_openings"]]


def run(group_name, configs, rows):
    print(f"\n=== {group_name}  ({GAMES} games/config, seed {SEED}) ===")
    print("  ".join(f"{h:>16s}" if i == 0 else f"{h:>8s}"
                     for i, h in enumerate(HEADER)))
    for c in configs:
        r = evaluate(c, games=GAMES, seed=SEED)
        rows.append(r)
        line = fmt(r)
        print("  ".join(f"{v:>16s}" if i == 0 else f"{str(v):>8s}"
                        for i, v in enumerate(line)))


if __name__ == "__main__":
    rows = []
    run("RECONSTRUCTION A — LATRVNCVLI (Roman)", LATRUN, rows)
    run("RECONSTRUCTION B — PETTEIA / POLIS (Greek)", PETTEIA, rows)

    with open("sweep_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open("sweep_results.json", "w") as f:
        json.dump(rows, f, indent=2)

    print("\nMetric guide:")
    print("  draw      lower is better (decisive game)")
    print("  p1_win    closer to 0.50 is better (no first-mover advantage)")
    print("  plies     game length in half-moves; want a 'living' middle range")
    print("  branch    avg legal moves/turn (decision complexity)")
    print("  open_H    opening-move entropy 0..1 (strategic variety; higher=richer)")
    print("\nWrote sweep_results.csv and sweep_results.json")
