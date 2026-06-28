# Finding — Eval rebuild (Priority-stack #2)

*Built a blockade-aware evaluation (`search_v2.py`) per HANDOFF §2 — heavy
mobility-denial, an azux/support term, a terminal-blockade preference, demoted
material — and measured it against the v1 material-first baseline with
`compare_evals.py` and `probe_weights.py`. The test #2 had to pass: move the
blockade share off the 0% baseline (FINDINGS-blockade-vs-cap.md). It did not —
and the reason is structural, not a weight-tuning miss.*

## What was built

- `search_v2.py` — `evaluation_v2` + `NegamaxAgentV2`. Mobility-denial uses the
  *exact* distance-to-blockade metric: under slide movement a piece is immobile
  **iff all its orthogonal neighbours are occupied** (a blocked adjacent cell
  blocks the whole ray), so "sum of empty orthogonal exits over foe pieces" is
  zero precisely at a full blockade. Plus an azux/support term, a terminal
  blockade bonus, and demoted material (W_MAT 100→20).
- `compare_evals.py` — A/B v1 vs v2 on identical seeds.
- `probe_weights.py` — an "encircle-at-all-costs" weight profile to separate a
  weights problem from a horizon problem.

## Results (canonical preset, depth-2, seed 1)

| Profile | Mean plies | Blockade | Annihilation | Material-cap | Draw |
|---|---|---|---|---|---|
| v1 material-first | 160 (=cap) | 0% | 0% | 100% of decided | 25–50% |
| v2 blockade-aware (default weights) | 160 (=cap) | **0%** | 0% | 100% of decided | 25% |
| v2 AGGRESSIVE (W_MOBDENY 14, W_VULN 1, W_MAT 8) | 89 | **0%** | 83% | 17% | 0% |

The aggressive profile *radically* changed play (mean plies 160→89, every game
decided, combative) — proving the eval levers work — yet produced **zero
blockades**. It simply captured its way to **annihilation** instead.

## The structural reading

**Blockade and capture are in tension.** Immobilising an enemy piece means
surrounding it, but surrounding it via custodial geometry tends to *capture* it
(or trip a bracket) first. A true blockade requires keeping enemy pieces *alive
but trapped* — a delicate, global, multi-move plan. The two reward signals each
route *around* blockade:

- reward material/safety → hoard, decline contact, grind to the cap;
- reward mobility-denial/engagement → close in, capture, win by annihilation.

A depth-2 search (effective horizon ≈ one move per side) cannot plan the
encirclement that threads between these. So a static eval, however weighted,
cannot manufacture blockades at this depth.

## Consequence for the priority stack

#2's payoff is **gated on search horizon**, not eval design:

- **#3 (bitboards → depth-3+).** Deeper search may begin to plan encirclement;
  the cheap proxy eval here is likely already adequate once the horizon is long
  enough. This is the engineering unlock.
- **#6 (MCTS-UCT, eval-free).** The HANDOFF's argument lands hard here:
  alpha-beta needs a good static eval and blockade is exactly what's hard to
  evaluate statically; MCTS needs only rollouts, so it is the architecture best
  suited to a positional siege — and the natural second witness.

## Open structural question (scholarly stakes)

Is a full blockade even *reachable* under slide movement + custodial capture on
an open 8×8 between competent players, or is the canonical victory condition
essentially unreachable in practice? If the latter survives deeper search and
MCTS, it reopens [D] choices in the reconstruction (movement, board size) and
qualifies the central claim that "blockade is the soul of the game." Worth a
direct probe (e.g. construct/seek near-blockade endgames) independent of agent
strength.
