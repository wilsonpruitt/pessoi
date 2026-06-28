# Finding — Depth-3 sweep (Priority-stack #4) + the blockade verdict

*The outstanding depth-3 / 100-game sweep, now tractable on the bitboard engine
under PyPy (200 games at depth-3 in ~11 min). Run with both the material-first
(v1) and blockade-aware (v2) evals. `run_sweep_depth3.py`, canonical preset
(placement / slide / both / material, 8×8, 16 pieces, cap 160), seed 1.*

## Results (100 games per agent, depth-3)

| Metric | v1 material-first | v2 blockade-aware |
|---|---|---|
| mean plies | 102 (CI 95–108) | 108 (CI 101–115) |
| draw rate | 2.0% | 1.0% |
| decisiveness | 98% | 99% |
| p1 win-rate (of decided) | **62.2% (CI 52.4–71.2)** | 47.5% (CI 37.9–57.2) |
| **blockade / decided** | **0 / 98 (CI 0–3.8%)** | **0 / 99 (CI 0–3.7%)** |
| annihilation / decided | 85.7% | 80.8% |
| material-cap / decided | 14.3% | 19.2% |

## 1. Blockade is ~unreachable — now robust across five configurations

Blockade share, every agent configuration tested this session:

| Configuration | Games | Blockade |
|---|---|---|
| Weak heuristic (1-ply greedy) | 120 | 0% |
| Depth-2 negamax, v1 material-first | 16 | 0% |
| Depth-2 negamax, v2 blockade-aware | 16 | 0% |
| Depth-3 negamax, v1 material-first | 100 | 0% (CI 0–3.8%) |
| Depth-3 negamax, v2 blockade-aware | 100 | 0% (CI 0–3.7%) |

Five configurations — two search depths, two evaluation philosophies, plus a
non-search heuristic — agree: **blockade essentially never decides a game** under
the canonical rules (slide movement + custodial capture, open 8×8). This clears
the HANDOFF's bar for a robust finding (≥2 architectures agree) several times
over. The only major architecture not yet run is MCTS (#6).

**Scholarly consequence.** The reconstruction's central claim — "blockade is the
soul of the game" (Plato/Polybius/Aristotle, foregrounded as the *primary*
victory condition over Schädler/Murray's reduction-to-one) — is, under all play
we can generate, **practically hollow**: the game is decided by capture, never by
immobilisation. This is exactly the failure the HANDOFF flagged and asked to
check; it is now checked and confirmed, with the qualification in §3.

## 2. Depth-3 cures the cap-grind — by routing to annihilation, not blockade

Depth-2 strong play ran to the 160-ply material cap every game (the hoarding
pathology). Depth-3 is sharply decisive (98–99%), resolving in ~100 plies — but
by **annihilation** (~80–86%), i.e. trading the opponent down below the two
pieces needed to capture. Deeper search makes the agent a better *capturer*, not
a blockader. The two reward philosophies (hoard-safe vs deny-mobility) both
route *around* blockade, just as the depth-2 analysis predicted (FINDINGS-eval-
rebuild.md): blockade and capture are in structural tension.

## 3. New observation — a first-player edge under v1 at depth-3 (caveated)

At depth-3 the material-first agent wins **62.2%** of decided games as first
player (CI 52.4–71.2, excludes 50%) — a statistically significant first-mover
edge on the *placement* opening, which the reconstruction adopted partly because
it is "the fairest" (vs the array's ~80% p1 skew). The blockade-aware v2 eval is
balanced (47.5%, CI includes 50%).

**Caveat — do not over-read this.** Both agents open with the cheap central-
cluster placement heuristic (the opening is "played blind", HANDOFF #5), so the
edge may be an artifact of naive symmetric placement + first-move tempo rather
than a property of the game. It qualifies, but does not overturn, the "placement
is fairest" result. Confirming or dissolving it needs competent opening play
(#5). Worth noting that the *fairer* agent here is the blockade-aware one.

## 4. Engineering note

PyPy ran 200 depth-3 games in 663s (~3.3 s/game). With the bitboard engine this
makes depth-3 sweeps routine — the depth-4 sweep and high-volume MCTS are now in
reach on this machine.

## Open

- **#6 MCTS** is the decisive remaining witness: eval-free, the architecture the
  HANDOFF argues is best for a siege. If MCTS also returns ~0% blockade, the
  "blockade is unreachable under canonical rules" verdict becomes essentially
  agent-invariant and the reconstruction's primary-victory claim needs revisiting
  in prose (or the rules — board size / movement — need a second look).
- **#5 placement intelligence** would settle the §3 first-player question and
  could, in principle, be the play sophistication blockade actually requires.
