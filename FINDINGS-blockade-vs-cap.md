# Finding — Blockade vs. Cap win share (Priority-stack #1)

*The one number the HANDOFF asked for first: under self-play, how often is a
game actually decided by **blockade** (the canonical victory condition) versus
ground out to the **material cap**? Produced by `instrument_termination.py`,
which reclassifies each finished game by termination reason from final state
(the engine sets `result` but never records *why* — `latrones.py:_check_end`).*

## Result

Canonical preset: `placement / slide / victory=both / cap_rule=material`,
8×8, 16 pieces, move_cap=160. Seed 1.

| Agent | Games | Mean plies | **Blockade** | Annihilation | Material-cap win | Draw |
|---|---|---|---|---|---|---|
| Weak — HeuristicAgent (1-ply greedy) | 120 | 58 | **0% (0/120)** | 100% | 0% | 0% |
| Strong — NegamaxAgent depth-2 (budget 6000) | 16 | 160 (=cap) | **0% (0/11 decided)** | 0% | 100% of decided | 31% |

95% Wilson CI on the weak-agent blockade share: **0.0%–3.1%** (n=120).

## Reading

**Blockade fires 0% of the time under *both* agent architectures.** This meets
the project's own bar for a robust result (HANDOFF §"MCTS as a second witness":
treat a finding as robust only when ≥2 architectures agree). The canonical
victory condition is, under all current play, **decorative** — it never decides
a game.

The two agents fail in **opposite** ways, which is the substantive insight:

- **Weak play → annihilation.** The capture-greedy heuristic trades the board
  down to a lone piece in ~58 plies. Bloody, fast, never a blockade.
- **Strong play → the cap.** The depth-2 negamax (eval `W_MATERIAL=100` vs
  `W_MOBILITY=1`, `search.py:18-20`) hoards material, declines contact, and runs
  to the exact 160-ply cap in *every* game (16/16), where the material
  tie-break decides it. This is precisely the failure the HANDOFF predicted:
  a material-maximizer is incentivized to hoard and run out the clock rather
  than blockade.

Note the inversion: the **stronger** agent blockades no more than the weak one,
and resolves *later* (160 vs 58 plies) — strength, as currently defined, moves
play *away* from the canonical win, not toward it.

## Caveat

0% blockade does **not** prove blockade is unreachable — only that neither
current eval *pursues* it (neither rewards immobilizing the opponent). Whether
the canonical condition is achievable at all under competent, blockade-seeking
play is exactly what Priority #2 (a mobility-denial / support / terminal-
blockade eval) is built to test. This finding is the *motivation* for #2, and
the baseline against which #2 must be measured: a successful new eval should
move the blockade share materially above 0%.

## Reproduce

```
cd ~/Downloads/files-2
python3.11 -u instrument_termination.py 16 1 2 120   # neg_games seed depth heur_games
```

Depth-2 negamax is ~40s/game; the 16-game strong run takes ~11 min. The weak
run (120 games) finishes in seconds.
