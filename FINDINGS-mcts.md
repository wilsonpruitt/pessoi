# Finding — MCTS witness (Priority-stack #6) + the agent-invariant verdict

*The decisive third architecture. Alpha-beta needs a good static eval and
blockade is exactly what is hard to evaluate statically; MCTS-UCT needs no eval,
only rollouts, so it is the HANDOFF's pick for a positional siege and an
architecturally-independent witness on the blockade question. `search_mcts.py`,
`run_mcts.py`, canonical preset.*

## Setup

- MCTS-UCT on the bitboard engine, `iterations` as the strength dial.
- **Phase-0 placement held fixed** (the same central-cluster heuristic as every
  other agent), so the only variable is the movement-phase search architecture.
- **Rollout policy.** Pure-random rollouts at low budget play *passively* — they
  rarely resolve, so the value signal is noise and games drift to the cap as
  draws (2/2 draws at 300 iters). A standard **heavy (capture-biased) playout**
  fixes this: rollouts prefer capturing moves and so resolve decisively. This is
  a move *preference*, not a static board evaluation — MCTS still shares no
  evaluation function with the negamax agents, so it remains an independent
  witness. Results below use the heavy playout (bias 0.8, rollout cap 40).

## Result (30 games, 400 iters/move, capture rollout)

| Metric | value |
|---|---|
| mean plies | 156 |
| draw rate | 10% |
| decisiveness | 90% |
| p1 win-rate (of decided) | 55.6% (CI 37.3–72.4, includes 50%) |
| **blockade / decided** | **0 / 27 (CI 0–12.5%)** |
| annihilation / decided | 18.5% |
| material-cap / decided | 81.5% |

MCTS plays cautiously — like the depth-2 negamax it mostly grinds to the
material cap (81.5%), occasionally annihilates (18.5%), and **never blockades**.

## The agent-invariant verdict

Blockade share, every configuration this session:

| Architecture | Configuration | Decided games | Blockade |
|---|---|---|---|
| Heuristic | 1-ply greedy | 120 | 0% |
| Alpha-beta | depth-2, material-first | ~11 | 0% |
| Alpha-beta | depth-2, blockade-aware | ~12 | 0% |
| Alpha-beta | depth-2, aggressive encircle | 6 | 0% |
| Alpha-beta | depth-3, material-first | 98 | 0% (CI 0–3.8%) |
| Alpha-beta | depth-3, blockade-aware | 99 | 0% (CI 0–3.7%) |
| **MCTS-UCT** | **400 iters, heavy rollout** | **27** | **0% (CI 0–12.5%)** |

Three independent architectures — a non-search heuristic, alpha-beta at two
depths with two evaluation philosophies (including one built specifically to
seek blockade), and an eval-free MCTS — agree across ~370 decided games:
**blockade essentially never decides a game under the canonical rules** (slide
movement + custodial capture, open 8×8). The HANDOFF's standard ("robust = ≥2
architectures agree") is met decisively.

## What this means for the reconstruction

The reconstruction foregrounds **blockade as the *primary* victory condition** —
the *cornering* of Plato, the blockade of Polybius — promoting it over
Schädler/Murray's reduction-to-one (petteia-reconstruction.md §3, §5.2;
design-decisions D10). That is a sound reading of the *texts*. But the engine
program was explicitly meant to let measurable game-health adjudicate the [D]
choices, and it now says: **under every kind of competent play we can generate,
the canonical game is decided by capture (annihilation or the material cap), not
by immobilisation.** Blockade is attested as the *ideal* of victory and is real
as a *rule*, but it is not how the game actually resolves.

Two honest responses, neither free:

1. **Revise the prose.** Keep blockade as the attested, evocative victory image
   but stop claiming it is how strong play wins; present the material tie-break
   (already adopted for decisiveness) as the *de facto* decider and say so. This
   preserves the source fidelity while removing a claim the engine contradicts.
2. **Revisit a [D] rule.** The most likely culprit is **slide movement** (D6):
   long-range slides give trapped pieces an escape, so total immobilisation is
   extraordinarily hard on an open board — whereas single-step movement (which
   the engine rejected as *degenerate*) would make blockade far easier. That is a
   genuine tension: the movement rule that makes the game *resolve* is the one
   that makes its *canonical victory* unreachable. Board size (D4) is a second
   lever — blockade is easier on smaller/edge-dense boards. The HANDOFF
   anticipated exactly this: a surviving 0% "reopens [D] choices (movement,
   board size)."

This is a scholarly decision, not an engineering one — flagged for Wilson.

## Caveats

- The opening is still played blind (#5); competent placement *could* in
  principle set up blockades none of these agents reach. This is the one
  un-closed door — worth #5 before any prose revision is finalised.
- MCTS here is moderate strength (400 iters, heavy rollout). A much larger MCTS
  might differ, but the consistency across architectures makes that unlikely.
