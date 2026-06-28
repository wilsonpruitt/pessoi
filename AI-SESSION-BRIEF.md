# Next session — Building the Pessoi AI (and a bot-vs-bot people want to watch)

**North star (Wilson's directive):** with Hoshi, the single thing that pulled people *into* the game was **bot-vs-bot** — watching two AIs play. So the goal here is not just "a stronger sparring partner." It's a **watchable spectacle** that's the on-ramp to the game, backed by genuinely distinct, balanced bot personalities.

Treat the strong-opponent work as the *engine* and the **watch experience as the product.**

---

## What Pessoi's bot is today  (`web/play.html`, the "House")
- **Ladder:** Novice (random) · Raider (1-ply greedy) · Adept (αβ depth-2) · Master (αβ depth-3). Negamax + alpha-beta with a node budget; `evaluate()` is a weighted sum.
- **Two styles** as `PERSONA` weight vectors over `{mat, mob, mobdeny, ownlib, support, vuln, threat, centre}`:
  - `aggressive` — material + threat (bloody, fun)
  - `positional` — mobility-denial / blockade-aware (build support, deny foe liberty)
- **House plays Pale (side 2) only.** Human-vs-bot. `houseMove(g)` dispatches on level+style; live-tunable mid-game.
- **Gaps vs Hoshi:** no computer-vs-computer mode, no "Watch" entry point, no pacing tuned for spectating, styles not balanced against each other, the mined **opening book is not baked into the JS client**.

## Assets to draw on (already built, in this repo)
- Python engine + search lab: `latrones.py`, `bitboard.py` (~4× faster, parity-verified), `search.py`/`search_v2*.py`/`search_bb.py`, `search_mcts.py` (MCTS-UCT), `search_open.py`.
- **Opening book** mined by self-play (`run_opening.py`, `FINDINGS-opening.md`): center-first, four central squares ≈ 90% of opening moves — not yet in the client.
- Self-play harness + sweeps (`run_sweep*.py`, `run_mcts.py`) — reuse to **coevolve/tune personalities** offline, then bake the resulting weight vectors into the JS.
- Findings that shape watchability: **capture decides, blockade almost never fires** under strong play (FINDINGS-*). Watchable games likely want *balanced, mid-strength, distinct-style* bots, not two Masters grinding to a material cap.

---

## What made Hoshi's watch mode work  (pattern to reuse — `~/wrootgames/hoshi/web/hoshi.html`)
1. **A "Watch the AI" CTA on the landing** (`#ctaWatch`) → drops you straight into cpu-vs-cpu. This is the on-ramp.
2. **Mode selector:** "vs Computer" **and** "Watch: Computer vs Computer" (`mode=cpucpu`).
3. **Balanced "style" personalities for watching** — a *coevolved, cyclic set each ~50% vs the others* (Hoshi: Territorial / Expansionist / Hunter), kept **separate** from the raw difficulty ladder. Balance is the point: lopsided games aren't fun to watch.
4. **Two independent side selectors** (Blue strength, Red strength) with **colored dots** marking which selector drives which color — so you can stage matchups or mismatches.
5. **Watch-speed control** (Normal / Fast / Turbo), shown only when neither watched bot is the heavy tier.
6. **Watchable pacing** (`botMinThink`, ~650ms ambient) so moves don't blur past.
7. **Ambient autoplay + music** (`gymnopedie.mp3`, `preload=none`, starts on first user gesture per autoplay policy) — a game quietly playing behind the landing.

---

## Proposed scope (prioritized)
**P0 — the watch experience (the actual draw):**
- Add **"Watch: the House vs the House"** mode to `play.html`: both seats driven by `houseMove`, a self-chaining loop with `botMinThink` pacing.
- Add a **"Watch the AI"** CTA to the **landing** (`web/index.html`) that deep-links into watch mode.
- Two side selectors (Obsidian bot / Pale bot: pick strength + style each) with side-colored dots; watch-speed Normal/Fast/Turbo.
- Lean into Pessoi's *unique* visual hooks: **custodial captures** (pieces vanish in pairs — flash them), the **placement draft** as opening drama, and the **blockade noose** tightening (a "trapped" warning when a side's legal moves get low). These are things Go/Hoshi can't show.

**P1 — personalities worth watching:**
- Replace the 2 ad-hoc styles with a **small coevolved cyclic set** (≈3–4) tuned offline via the self-play harness so each is ~50% vs the others and *plays visibly differently*. Bake the weight vectors into the JS.
- **Name them from the scholarship** (a unique, on-brand hook no chess-knockoff has): e.g. **Hamilcar** = the blockader who "hems in and wins without a battle" (Polybius 1.84, our own find this project) · a **Raider** (aggressive, material) · a **Polis-builder** (positional/territorial) · maybe a **Conservator** (cautious). Ties the AI directly to the reconstruction.

**P2 — polish that makes watching legible:**
- Bake in the **opening book** so watched games open varied + competent (not samey/weak).
- Optional **eval bar** / capture + threat ticker / light "commentary" line ("Pale is closing the file…").
- Ambient autoplay behind the landing + optional music toggle (Hoshi-style).

**P3 — a genuinely stronger engine (optional, for the top tier):**
- Port **MCTS-UCT** (`search_mcts.py`) to JS for a "Grandmaster" watch tier, or deepen αβ with the opening book + better eval. The early research wanted a **Go-style influence/territory term** in the eval (the Hoshi bridge — encirclement is spatial); that term is still unbuilt and is the most promising eval upgrade.

---

## Technical approach
- Keep it **client-side JS in `play.html`** (the family pattern — Hoshi's bot is in-page; no server). The existing `negamax`/`evaluate`/`houseMove` is the base.
- **Tune offline, ship weights:** use the Python self-play sweeps to coevolve the personality weight vectors and validate ~50% cross-play, then hard-code the vectors in `PERSONA`. Don't try to coevolve in the browser.
- **Port the opening book** (`opening-book.json` equivalent) — mirror how Hoshi ships `opening-book.json` + `build_opening_book.js`.
- Watch-mode pacing/speed: copy Hoshi's `botMinThink` + watch-speed gating (slow only the light tiers; the heavy tier paces itself).

## Open decisions for Wilson (start of session)
1. **Personality names** — lean into the Greek/Roman scholarship (Hamilcar, Polis-builder, Raider…)? (Recommended — it's the anti-chess-knockoff identity made playable.)
2. **How many styles** in the watch set (3 vs 4)?
3. **Music** for ambient watch — yes/no, and what (Hoshi uses Satie's *Gymnopédie*; Pessoi might want something that reads ancient/Mediterranean without being kitsch).
4. **Top "Grandmaster" tier** — worth the MCTS-in-JS port, or is depth-3 + opening book + a territory eval term enough?

## First moves when the session opens
1. Re-read this brief + `FINDINGS-opening.md` + the `PERSONA`/`houseMove` block in `web/play.html`.
2. Prototype the **cpu-vs-cpu loop + pacing** in `play.html` (smallest thing that proves the draw).
3. Wire the **landing "Watch the AI" CTA**.
4. *Then* invest in coevolving the named personalities offline.

**Deploy reminder:** CLI deploys, not git-connected — ship with `cd ~/wrootgames/pessoi/web && npx vercel --prod --yes`. Repo: `github.com/wilsonpruitt/pessoi` (private, branch `main`).
