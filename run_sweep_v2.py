"""
run_sweep_v2.py  —  Resumable sweep with the negamax agent + confidence
intervals. Appends each finished config to sweep_v2.jsonl so it can be run
in chunks (re-run until it prints the final table).

Config knobs: GAMES games/config, depth-2 search, NODE_BUDGET nodes/move,
move_cap counted in MOVEMENT plies.
"""
import json, os, sys, csv
from latrones import RuleSet, evaluate
from search import negamax_factory

GAMES = 12
SEED = 7
DEPTH = 2
NODE_BUDGET = 400
CAP = 120
STORE = "sweep_v2.jsonl"


def R(name, **kw):
    base = dict(width=8, height=8, pieces=16, move_cap=CAP)
    base.update(kw)
    return RuleSet(name=name, **base)


CONFIGS = [
    # --- LATRVNCVLI (Roman) ---
    R("L0 anchor (Piso)",   setup="placement", movement="slide", corner_capture=True,  freeing=False, victory="both"),
    R("L1 Seneca (freeing)",setup="placement", movement="slide", corner_capture=True,  freeing=True,  victory="both"),
    R("L2 step move",       setup="placement", movement="step",  corner_capture=True,  freeing=False, victory="both"),
    R("L3 corners safe",    setup="placement", movement="slide", corner_capture=False, freeing=False, victory="both"),
    R("L4 annihilate only", setup="placement", movement="slide", corner_capture=True,  freeing=False, victory="annihilate"),
    R("L5 7x8 board",       setup="placement", movement="slide", corner_capture=True,  freeing=False, victory="both", width=8, height=7, pieces=14),
    # --- PETTEIA / POLIS (Greek) ---
    R("P0 anchor (blockade)",setup="array",    movement="slide", corner_capture=True,  freeing=False, victory="blockade"),
    R("P1 both win-conds",  setup="array",     movement="slide", corner_capture=True,  freeing=False, victory="both"),
    R("P2 step move",       setup="array",     movement="step",  corner_capture=True,  freeing=False, victory="blockade"),
    R("P3 placement setup", setup="placement", movement="slide", corner_capture=True,  freeing=False, victory="blockade"),
    R("P4 9x9 board",       setup="array",     movement="slide", corner_capture=True,  freeing=False, victory="blockade", width=9, height=9, pieces=18),
]


def done_names():
    if not os.path.exists(STORE):
        return set()
    return {json.loads(l)["name"] for l in open(STORE) if l.strip()}


def run_one():
    done = done_names()
    for c in CONFIGS:
        if c.name in done:
            continue
        r = evaluate(c, games=GAMES, seed=SEED,
                     agent_factory=negamax_factory(DEPTH, NODE_BUDGET))
        with open(STORE, "a") as f:
            f.write(json.dumps(r) + "\n")
        print(f"done: {c.name}", flush=True)
        return True   # one per invocation keeps each call short & safe
    return False


def render():
    rows = [json.loads(l) for l in open(STORE) if l.strip()]
    order = {c.name: i for i, c in enumerate(CONFIGS)}
    rows.sort(key=lambda r: order.get(r["name"], 99))

    def hw(ci):
        lo, hi = ci
        return (hi - lo) / 2 if lo == lo else float("nan")  # nan-safe

    hdr = f"{'ruleset':<22}{'draw':>11}{'dec':>6}{'p1_win':>12}{'plies':>11}{'branch':>8}{'open_H':>8}{'n':>4}"
    print("\n" + hdr)
    print("-" * len(hdr))
    grp = None
    for r in rows:
        g = "Roman" if r["name"].startswith("L") else "Greek"
        if g != grp:
            print(f"--- {g} ---")
            grp = g
        draw = f"{r['draw_rate']:.2f}±{hw(r['draw_ci']):.2f}"
        p1 = (f"{r['p1_winrate']:.2f}±{hw(r['p1_ci']):.2f}"
              if r['p1_winrate'] == r['p1_winrate'] else "  --  ")
        pl = f"{r['mean_plies']:.0f}±{hw(r['plies_ci']):.0f}"
        print(f"{r['name']:<22}{draw:>11}{r['decisiveness']:>6.2f}{p1:>12}"
              f"{pl:>11}{r['mean_branching']:>8.1f}{r['opening_entropy']:>8.2f}"
              f"{r['distinct_openings']:>4}")
    with open("sweep_v2_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("\nAgent: alpha-beta negamax depth", DEPTH, "| budget", NODE_BUDGET,
          "nodes/move |", GAMES, "games/config | 95% CIs shown as value±halfwidth")


if __name__ == "__main__":
    if "--render" in sys.argv:
        render()
    else:
        progressed = run_one()
        remaining = len(CONFIGS) - len(done_names())
        if remaining == 0:
            render()
        else:
            print(f"[{len(done_names())}/{len(CONFIGS)} configs complete; "
                  f"{remaining} remaining — run again]", flush=True)
