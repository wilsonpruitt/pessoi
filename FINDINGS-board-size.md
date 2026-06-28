# Finding — Board size & density (the D4 experiment)

*Tests whether changing the board (D4) rescues the blockade victory condition,
which is 0% on the 8×8 canonical board across all architectures (FINDINGS-mcts,
FINDINGS-opening). Hypothesis: fewer escape squares / more wall contact on a
smaller or crowded board makes total immobilisation easier. Blockade-aware agent
(search_v2_bb) at depth-3, the player that actually seeks blockade. ~30 games per
configuration. `run_board_sizes.py`.*

## Result

| Board | Pieces | Fill | Blockade / decided | Annihilation | Cap |
|---|---|---|---|---|---|
| 5×5 | 6 | 48% | 0/29 (0–12%) | 100% | 0% |
| 6×6 | 9 | 50% | 0/28 | 79% | 21% |
| 7×7 | 12 | 50% | 0/27 | 63% | 37% |
| 7×8 | 14 | 50% | 0/29 | 69% | 31% |
| 8×8 | 16 | 50% | 0/30 | 87% | 13% |
| 9×9 | 20 | 50% | 0/30 | 83% | 17% |
| **5×5** | **9** | **72%** | **1/30 = 3% (1–17%)** | 97% | 0% |
| **6×6** | **13** | **72%** | **2/28 = 7% (2–23%)** | 82% | 11% |
| 7×7 | 18 | 73% | 0/28 | 75% | 25% |

## Reading

1. **Board *size* is not the lever.** At ~50% fill, every board from 5×5 to 9×9
   returned 0% blockade. Shrinking the board did not help — if anything the
   smallest boards annihilate *more* (5×5 → 100%), because less space means more
   capture contact.

2. **Density is the lever — and it barely moves the needle.** Only the crowded
   ~72%-fill small boards produced any blockades: 5×5/9 → 3%, 6×6/13 → 7% (Wilson
   lower bound 2%, so a genuine non-zero effect). Even at best, capture still
   decides ~82%+. Blockade is *reachable*, never *common*.

3. **The boards that deliver blockade are unattested.** 5×5 and 6×6 are **not**
   in the archaeological record (attested: 7×7, 7×8, 8×8, 9×9, 9×10). The
   smallest *attested* board, 7×7, gave **0%** even crowded to 73% fill. So a
   board change that makes blockade meaningfully more likely requires leaving the
   attested size range *and* over-crowding — two departures from the evidence to
   buy a 3–7% blockade rate.

4. **Instrumentation validated.** The engine *does* register blockades when the
   geometry permits them (cramped boards), so the 0% on canonical boards is a
   real property, not a detection artifact.

## Consequence for the §6C fork

This was offered as the gentle lever in §6C Response B ("board size is the gentler
lever"). The experiment finds it **largely a dead end for the blockade goal**:
within attested sizes, no board produces blockade; the only boards that do are
small, unattested, and over-crowded, and even they top out at ~7%. So D4 does
**not** provide a source-licensed way to make blockade the way the game is won.
Response B via board size is therefore weak; **Response A (editorial precision)
stands as the honest resolution** of the blockade verdict.

## A separate, cost-free win: distinctiveness

Board choice still matters for a *different* reason — identity. **8×8 is the
chessboard** (the client even renders it as one), and ~9×9–19×19 is Go's
territory. Since 8×8 has no attestation advantage over 7×7 / 7×8 / 9×9 (all
equally attested; the Greek game has *no* attested size), moving the default off
8×8 costs nothing in source-fidelity and immediately signals "not chess." **7×7
is the cleanest choice:** attested, inside the computationally-supported squarer
range (Ludii 2024: the real game lived on 7×8–9×9), visibly not the chessboard,
and well clear of Go's larger boards. This is independent of the blockade
question — it is a positioning/identity decision, and a free one.

## Bottom line

- **To rescue blockade:** board geometry cannot do it within the evidence →
  adopt §6C Response A (editorial) rather than a D4 rule change.
- **To stop reading as a chess knock-off:** switch the canonical default to
  **7×7** (or 7×8) — attested, distinctive, and free. Recommended regardless of
  the blockade decision.
