# Latrones / Petteia — Handoff & Roadmap

*State of the project at the close of the v0.3 session, and where to point the next one. The centre of gravity here is the **strategic direction of the AI agents**, because they now serve two masters and the right moves differ depending on which one you're optimizing.*

---

## 1. Where the project stands

The project reconstructs **one** canonical game — *Petteia / Polis* — with *Ludus Latrunculorum* folded in as its **Roman reception**. Canonical rules: open-board **placement**, **slide** movement, custodial capture, **blockade** as the primary win, material as secondary, and a **material tie-break** at the move cap.

**File map (in `outputs/`):**
- `petteia-reconstruction.md` — the canonical reconstruction (v0.3). *Supersedes the retired two-game draft.*
- `latrones-design-decisions.md` — the per-rule rationale + [A]/[I]/[D] confidence grades.
- `latrones.py` — engine. Flat-array board, all rules as `RuleSet` flags, `clone()` for search, 14 passing unit tests (`test_latrones.py`). Defaults are the canonical game.
- `search.py` — `NegamaxAgent` (alpha-beta, depth-2, node-budgeted) + static `evaluation()`.
- `latrones-board.html` — playable client; Petteia default, Latrunculi-reception variant; JS engine is a verified port (13/13 parity tests).
- `run_sweep*.py`, `sweep_*` — the parameter sweeps and their results.

**Robust findings so far:** step movement is degenerate (any depth, any cap rule); the 9×9 array is first-player-skewed; placement is fairest; freeing suppresses combat (~0.7 vs ~18 captures/game); material-at-cap rescues decisiveness without distorting fairness; corner-capture is near-inert.

---

## 2. Strategic direction for the AI agents

### The one problem under everything: the bots play the wrong game

The current evaluation is **material-first** — `W_MATERIAL=100` dwarfs `W_MOBILITY=1`. But the canonical game is won by **blockade**, not by attrition. The agent is therefore optimizing a proxy (piece count) that the game only treats as a *secondary* condition and a *tiebreak*. Three consequences, and they compound:

1. **The agent is weak in the way that matters most.** It doesn't pursue immobilization; it stumbles into blockade wins or, more often, grinds to the material cap. A bot built for a capture game is refereeing a siege game.
2. **It quietly threatens the central scholarly claim.** With material-at-cap as the default finish, a material-maximizing bot is incentivized to *hoard and run out the clock* rather than blockade. So "blockade is the soul of the game" may be aesthetically true but practically hollow under strong play — the tiebreak could be doing the real work. **This needs checking, not assuming:** instrument what fraction of strong-play games actually end by blockade vs. by the material cap. If it's mostly the cap, the canonical victory condition is decorative, and either the eval or the rules need to change.
3. **It biases every game-health metric.** Draw rates, decisiveness, and opening diversity are all read off self-play; if the agent misunderstands the win condition, the map of the rule-space is drawn by a player who doesn't know how to win.

**So the highest-priority work is the evaluation, not the search.** Concretely, in rough order:

- **Re-weight toward mobility denial.** Make the opponent's total liberty (legal-move count, or pieces with no safe escape) a *major* term, not a rounding error. In a blockade game, shrinking the foe's options *is* progress toward victory.
- **Add an isolation/support term (the *azux* of Aristotle).** Reward connected, mutually-defending chains; penalize lone pieces. This is both source-faithful and exactly the structure that produces blockades.
- **Add an explicit terminal-blockade bonus** so the search *prefers a blockade win to a material win* when both are reachable. Right now a forced blockade and a +1 material edge look similar to the eval; they shouldn't.
- **Borrow an influence/territory term from Go.** This is the natural HOSHI bridge: encirclement is spatial, and a coarse region-control field (whose pieces dominate which empty zones) approximates blockade pressure better than any piece-counting term. Worth prototyping precisely because it's the term most aligned with how this game is actually won.

### The second problem: the opening is played blind

Placement is **half the game** (16 drops/side) and the agent currently just clusters toward the centroid. For a placement game that's like opening a chess game by always pushing the d-pawn. Two directions:

- Give placement its own shallow search (even 1–2 ply with the real eval), or a learned placement policy. Opening quality is currently unmeasured because no agent plays the opening well.
- **Mine strong self-play for recurring placement patterns → petteia opening theory.** No one has an opening book for a reconstructed ancient game; this is a genuinely novel scholarly artifact, and it falls out of the engine almost for free once the agent plays the opening competently.

### The engineering unlock: speed

Everything above is gated by pure-Python throughput. The agent currently `clone()`s the whole state per node, which is why depth-3 over 100 games is a "needs a dedicated session" task. Two investments, highest leverage first:

- **Bitboards.** The board is ≤81 cells — it fits in a couple of integers. Capture, mobility, and blockade tests become bit operations; expect 10–100×. This single change unlocks depth-3+, the 100-game runs, and MCTS rollout volume all at once.
- **Make/undo instead of clone-per-node**, plus a transposition table, iterative deepening, killer/history move ordering, and a short quiescence search through forced captures (so the agent stops misjudging tactics at the horizon).

### The architectural fork: two bots, not one

It's worth being explicit that the agents serve two different jobs, and conflating them is a mistake:

- **The analyst bot** (research instrument) should be **strong, consistent, reproducible** — its job is to draw a trustworthy map of the rule-space. Optimize for playing strength and determinism.
- **The sparring bot** (opponent for you and Dominic, in the client) should be **fun, fast, and tunable** — not maximally strong. A bot that always grinds to a material-tiebreak win is no fun to play. Build a difficulty ladder (random → greedy → shallow search → strong) and give the higher tiers *personality* (an aggressive/encircling style vs. a patient/positional one). Style variety is also a richness probe for the research side.

### The cross-check worth adopting: MCTS as a second witness

Add an **MCTS-UCT** agent. The argument is specific to this game: alpha-beta needs a *good static eval*, and blockade is precisely the thing that's hard to evaluate statically. MCTS needs no eval — it needs rollouts — so it's the architecture best suited to a positional siege game, and it comes with a natural strength dial (more rollouts = stronger), which doubles as the sparring-bot difficulty knob.

It also buys methodological rigor: **treat a finding as "robust" only when ≥2 agent architectures agree.** Step-degeneracy already survived weak+strong and depth-2+depth-3; an eval-free MCTS agreeing would make these results agent-invariant rather than artifacts of one evaluation function. That standard is cheap insurance for the whole research program.

---

## 3. Priority stack (if you want a single ordering)

1. **Instrument blockade-vs-cap win share** under current strong play — one number that tells you whether the canonical victory condition is real or decorative. Cheap; do it first.
2. **Rebuild the evaluation** around mobility-denial + support + a terminal-blockade bonus (+ a Go-style influence term to prototype).
3. **Bitboard the engine** — the unlock for depth, volume, and MCTS.
4. **Run the outstanding depth-3 / ~100-game sweep** once (3) makes it tractable; tighten the mid-range CIs.
5. **Smarter placement + opening-book mining** → petteia opening theory.
6. **Add MCTS-UCT**; adopt agent-invariance as the bar for "robust."
7. **Split analyst vs. sparring bots**; give the client a difficulty ladder for hand-play.

---

## 4. Non-bot threads still open

- **Stub vs. rename.** The old `latrunculi-petteia-reconstruction.md` was deleted outright, not stubbed — restore a pointer file if your git history wants one.
- **The reception caveat is a real fork, not a settled fact.** If embodied texture ever outweighs parsimony for you, the project can re-anchor in *Ludus* with petteia as background — §0/§4 of the reconstruction keep that door open on purpose.
- **Freeing is the chess-pull lever.** It's the one rule that meaningfully differentiates the Roman game; keeping it primary (against its weak attestation) is the move if you ever want the two traditions to feel distinct again. Decided off by default, reversible.
- **Background compute doesn't persist** in this container between tool calls — the depth-3 run needs a single uninterrupted session, not a nohup trick.
