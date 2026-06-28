# Finding — Competent opening + opening book (Priority-stack #5)

*Every prior agent placed with the central-cluster heuristic ("always pushing the
d-pawn"), leaving two things open: opening quality, and the one un-closed door on
the blockade verdict (maybe blockade needs an opening the blind agents never set
up). This gives placement a real 1-ply policy — score each candidate drop by the
blockade-aware eval (which rewards azux/support, the structure tied to blockade)
— and mines the resulting placements into a first opening book. `search_open.py`,
`run_opening.py`. 80 games, depth-3, canonical preset.*

## 1. The door is closed — a competent opening does NOT enable blockade

| Metric | naive opening (depth-3, prior) | **smart opening (depth-3)** |
|---|---|---|
| mean plies | 102–108 | 112 |
| decisiveness | 98–99% | 95% |
| **blockade / decided** | 0% (CI 0–3.8%) | **0 / 76 (CI 0–4.8%)** |
| annihilation | 81–86% | 82.9% |
| material-cap | 14–19% | 17.1% |

Even with placement specifically optimised for the support/azux structure the
sources tie to blockade, **blockade share stays at zero**. This was the last
plausible escape hatch for the canonical victory condition, and it is closed. The
verdict is now unconditional:

> Across three architectures (heuristic, alpha-beta at two depths and three eval
> philosophies, eval-free MCTS) **and** a competent opening, blockade essentially
> never decides a game under the canonical rules (slide + custodial capture, open
> 8×8). The game is won by capture — annihilation under decisive play, the
> material tie-break otherwise.

## 2. The first-player edge dissolves

The depth-3 sweep with the *naive* opening + material-first eval showed a
significant first-mover edge (62.2%, CI 52.4–71.2, excluded 50%). With the
competent opening + blockade-aware eval it is **57.9% (CI 46.7–68.4, includes
50%)** — no longer significant. So that edge was substantially an artifact of
the blind opening and the material-first eval, not a property of the game. It
qualifies the depth-3 §3 caveat (FINDINGS-depth3-sweep.md): the placement opening
is fair under competent play, consistent with the reconstruction's "placement is
fairest" claim (D5).

## 3. A first petteia opening book

No one has had an opening book for a reconstructed ancient game; it falls out of
the engine once the agent plays the opening competently. Placement-frequency
heatmap (0–9 = round(9 × occupancy frequency over 80 games), y increasing
upward; player 1 fills from the bottom):

```
Player 1                         Player 2
1 1 2 2 1 1 1 1                  1 1 1 1 1 1 1 1
1 2 4 2 2 3 2 0                  1 1 2 4 4 1 1 1
1 3 3 3 4 6 4 1                  0 2 4 6 5 3 2 1
1 2 3 6 6 3 2 2                  1 3 5 3 3 5 5 1
1 2 4 6 6 3 2 2                  1 3 4 3 3 5 4 1
1 2 5 3 4 5 4 1                  1 2 3 5 5 3 1 1
1 1 2 2 2 4 2 0                  1 1 2 4 4 1 1 1
1 1 1 1 1 1 1 1                  1 1 1 2 1 1 1 0
```

Most common first drop:
- **Player 1:** e5 31%, e4 21%, d5 20%, d4 18% — the four central squares take
  ~90% of opening moves.
- **Player 2:** d5 26%, e5 26%, e4 21%, d4 16% — likewise central.

**Read.** Petteia opening theory, as this engine plays it: *open in the centre
and build a connected central mass* — the four central squares dominate the first
move, the central core (d4–e5) is occupied 6–7× more often than the edges, and
play radiates outward into supported chains. The edges and corners are filled
late and rarely contested early. (A mild rightward/f-file lean appears in the
heatmap — plausibly an artifact of move-ordering / tie-break asymmetry rather
than a real positional asymmetry; worth confirming before reading anything into
it.)

## Status

This closes the only caveat on the blockade verdict. The research arc the HANDOFF
laid out is essentially complete: the canonical victory condition has been shown
unreachable under all competent play, the engine has been made fast (bitboards +
PyPy), and a first opening book exists. The remaining priority item is #7
(analyst vs. sparring split + difficulty ladder), which is largely packaging —
the MCTS `iterations` knob and the eval/depth choices already provide the dial.
The substantive open question is now scholarly, not computational: how to reflect
the blockade verdict in the reconstruction (revise the prose, or revisit the
slide-movement / board-size [D] choices). See FINDINGS-mcts.md §"What this means".
