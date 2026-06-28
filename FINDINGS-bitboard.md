# Finding — Bitboard engine (Priority-stack #3)

*The throughput unlock. The reference engine (`latrones.py`) stores the board as
a length-N list and `clone()`s it at every search node; the HANDOFF flagged this
as the wall gating depth-3 and MCTS volume. This rebuilds the canonical +
research rule-space with the board held as two integers (one bit per cell per
player).*

## What was built

- `bitboard.py` — `BitGame`: board = `p1`/`p2` ints; `count()` = popcount;
  occupancy/empties/blockade as bit ops; `clone()` copies a handful of ints;
  `snapshot()`/`restore()` for make/undo search (no per-node allocation);
  `has_legal_move()` early-exit blockade test. Same external surface the agents
  use, so `search.py`/`search_v2.py` run on it unchanged.
- `search_bb.py` — bitboard-native negamax: `evaluation_bb` (reads `p1`/`p2`
  directly, **numerically identical** to `search.evaluation`), O(1) capture-count
  ordering, make/undo recursion.
- `test_parity.py` — lockstep parity vs `latrones.Game`.
- `bench.py`, `bench2.py` — throughput + eval-parity harnesses.

**Scope:** placement/array, slide/step (+leap), corner_capture, anti_shuffle,
blockade/annihilate/both, material/draw cap. The freeing/incitus variant is
**not** ported (weakly attested, off by default, combat-suppressing — §4 of the
reconstruction); `BitGame` raises on `freeing=True` so misuse fails loudly.

## Verification

- **2304 lockstep parity games, 0 divergences** across the full non-freeing
  rule-space (every setup × movement × victory × corner × anti × cap × leap, on
  7×7/8×8/9×9/7×8). At every ply both engines offer the identical legal-move set
  and reach identical board/result/counts.
- **Eval parity exact** — `evaluation_bb` vs `search.evaluation`, max abs diff
  `0.00e+00` over 4000 random positions.
- The reference engine's 14 unit tests are untouched and still green.

## Speed

Depth-2 canonical self-play, same games on each engine (within-run ratio; the
machine's absolute times are thermally noisy on this 8 GB Mac):

| Engine | s/game | vs reference |
|---|---|---|
| reference (list, clone-per-node) | ~20–40 | 1.0x |
| BitGame drop-in under list search | ~same | 1.08x |
| bitboard-native eval + ordering | — | 1.73x |
| + make/undo (no clone allocation) | — | 1.94x |
| + early-exit `has_legal_move` blockade test | **~5.0 s/game** | **~4.2x** |

(Confirmatory 6-game run: reference 20.99 s/game vs bitboard-native 4.97 s/game
= 4.22x, 960/960 plies identical.)

The single biggest win was the last one: profiling showed `legal_moves` was
~56% of runtime, and `_check_end` was calling it a *second* time per node just
to ask "is there any move?" — replacing that with an early-exit check roughly
quartered the bitboard time.

## Honest ceiling, and the real path to depth-3 sweeps

~4x is about what bitboards buy **in pure CPython**. After the fixes above the
dominant cost is no longer the O(N) board scans (bitboards removed those) — it
is **interpreter overhead in move generation and negamax recursion**, which
bitboards cannot touch. Depth-3 expands ~10–30x more nodes than depth-2, so 4x
does not by itself make the depth-3 / 100-game sweep cheap.

Realistic routes to the HANDOFF's 10–100x, in order of leverage-per-effort:

1. **PyPy** — this code (tight integer/loop work, no C-extension deps) is close
   to a best case for PyPy's JIT; often 10–50x with zero code change. First
   thing to try.
2. **Transposition table + iterative deepening + killer/history ordering** —
   algorithmic, cuts the node count itself (multiplies with any of the above).
3. **Cython / C extension for `legal_moves` + `negamax`** — the hot loop; large
   constant-factor win, more effort.
4. **Numpy/batched self-play** — amortize across many games at once for the
   sweep specifically.

Recommendation: with ~4x in hand, a depth-3 / ~100-game sweep is now tractable
as a single long background run; if it's still too slow, try PyPy before writing
any C.
