# Latrones — Design Decisions & Evidential Standing

*A companion apparatus to* Reconstructing Petteia / Polis (the Greek game, with Ludus Latrunculorum as its Roman reception). *The project reconstructs **one** canonical game; where that document states the rules, this one exposes the seams: every structured decision, what the ancient evidence does and does not say, and how confident we are — separating what is attested from what we chose.*

---

## 0. How to read this

Two things are easy to conflate in a reconstruction: *what the sources compel* and *what we decided because something had to be decided*. The whole value of the project depends on keeping them apart. Every rule below therefore carries an explicit grade, and the rationale says plainly whether the decision was forced by a text, inferred from one, or chosen on other grounds.

The governing principle: **the ancient constraints are hard walls; playability chooses among whatever is left standing.** Where a source fixes a rule, self-play results cannot overrule it. Where the sources are silent or ambiguous, and only there, we let measurable game-health decide — and we say so.

A note on sourcing, consistent with the project's standing preference: **primary texts carry the weight.** Varro, Ovid, Martial, Seneca, the *Laus Pisonis*, Isidore, Plato, Aristotle, Polybius, Pollux, Homer, and Plautus are the evidence; modern reconstructors (Wayte, Austin, Murray, Bell, Schädler, Parlett, Crist–Browne) are read as interpreters of that evidence, cited but never treated as the evidence itself.

### The grades

| Tag | Meaning |
|-----|---------|
| **[A] Attested** | A primary source states or all-but-states the rule. Not open to revision on playability grounds. |
| **[I] Inferred** | No source states the rule, but one or more imply or strongly suggest it. Revisable, but with evidential resistance. |
| **[D] Design choice** | The sources are silent or merely permissive. Decided on coherence + playability, and freely revisable. |

A secondary axis — **Strong / Moderate / Weak** — records how firmly the evidence (or, for [D], the playability case) holds.

---

## 1. The decision register

### D1 · A latticed grid board — **[A], Strong**
**Sources.** Varro, *De Lingua Latina* X.22, compares the playing surface to the ruled grid used for setting out declensions — the earliest Roman reference, and decisive for a gridded board. Pollux, *Onomasticon* IX.97–98, gives the Greek board the name *polis* ("city") and the pieces two colours.
**Decision.** Orthogonal grid, play on the cells. No tradition we reconstruct uses diagonal lines.
**Note.** Archaeology shows the *size* was never fixed (see D4); the *grid* itself is not in doubt for the games we are reconstructing. (The rectangular, possibly un-latticed Stanway-type boards are treated separately under D2 / §3.)

### D2 · Two equal armies; **no Dux / leader piece** — **[A] for "equal," Strong; rejection of Dux is [I], Strong**
**Sources.** Pollux names the pieces simply "dogs" (*kynes*), two colours, with no hint of rank. Martial XIV.17 calls them *latrones* (soldier-pieces) without differentiation. The Perugia hoard (816 glass counters) and British Museum sets are uniform discs distinguished by colour, not by class.
**Decision.** All pieces identical; both sides symmetric.
**Why no Dux.** The leader-piece ("Dux"/"Aquila") originates not in any text but in modern readings of the *arrangement* of counters in the Stanway "Doctor's burial," raised as a possibility by Parlett and built into a playable rule by Bell. Schädler's objection is decisive on the evidence: there is no sign of any piece other than the *latrones* / *pessoi* in **any** Greek or Roman source, and the Stanway board is rectangular (~2:3), possibly un-latticed, and may not be latrunculi at all but a native British game (*fidchell* / *gwyddbwyll*). A single contested grave-arrangement cannot license a rule that every textual source omits. (Full treatment: §3.)
**Live minority view, noted and set aside.** Wayte (*CR* 1892), reading Isidore, proposed that the *inciti* were a *third class* of immovable pieces (a "camp"), citing the three-colour Perugia find. We record this as a genuine alternative but do not adopt it: it rests on one interpretation of one source against the silence of all others.

### D3 · Piece count — **[D], Moderate**
**Sources.** None gives a number. Reconstructions land at 16–24 per side depending on board.
**Decision.** Player-agreed, with **12 per side on 7×7** as the default (roughly half the board occupied across both armies after placement — dense enough for contact, open enough to manoeuvre).
**Decided by.** Coherence with the placement opening and self-play density; nothing historical forbids other counts.

### D4 · Board size — **[A] that it varies; [D] for the default, Strong**
**Sources.** Surviving boards run 7×7, 7×8, 8×8, 9×9, 9×10 and larger; Vindolanda alone yields many. Size was demonstrably not standardised.
**Decision.** **7×7 default**, size treated as a tunable parameter.
**Decided by.** The attested sizes (7×7, 7×8, 8×8, 9×9, 9×10) are not ranked by the evidence — 8×8 is the most *frequent* find but carries no authority the others lack, and the Greek game fixes no size at all. 8×8 is therefore dropped on two grounds it cannot answer: it is the **chessboard** (and ~9×9-and-up is Go's), so it makes the game read as a knock-off, while 7×7 is equally attested, sits in the computationally-supported squarer 7×8–9×9 range, and reads as neither. Self-play fairness is comparable across the small square boards (a 9×9 *array* hands the first player ~80% and collapses opening variety, but that is the array on a large board, not 7×7); and the engine's board-size sweep shows the **blockade outcome is the same on every attested board** (§6C of the reconstruction; FINDINGS-board-size.md), so nothing of substance is traded by the change. The big rectangular boards (e.g. Colchester 8×12) remain **probably not latrunculi** — they stall out computationally and match the Stanway-type rectangular group better than the latticed square boards.

### D5 · Opening: **open-board placement** (not opposed rows) — **[I], Moderate → adopted for both traditions**
**Sources.** The *Laus Pisonis* (190–208) describes play on the *open board* (*tabula … aperta*) with counters varied "in a more clever way," soldiery of glass, reserves, and the breaking of a line — language that reads naturally as pieces *entering* an open field rather than starting pre-arrayed. Against the rival "two opposed rows," Wayte (*CR* 1892) states flatly that the pawn-rank setup is *a chess analogy for which there is no authority.*
**Decision.** Both Latrunculi and Petteia open by **alternating placement onto an empty board**; captures are suspended during placement (the *vagi* are immune).
**Decided by.** Convergent lines: the open-board language of the one detailed gameplay source; the explicit absence of any ancient warrant for the array; and self-play, in which placement gives the fairest, least drawish, most varied game — decisively so for the Greek side. We previously flagged the array as "the single weakest link"; the right response was to cut it, not defend it. The cost, stated openly: with a shared placement opening the two traditions become mechanically close — consistent with the view (Schädler) that *polis* and *latrunculi* are "largely the same game."

### D6 · Movement: **slide** (rook-like), not single-step — **[I], Strong**
**Sources.** Ovid (*Ars Amatoria* III.357–360; *Tristia* II.477) describes pieces moving and capturing along lines; the *Laus Pisonis* speaks of breaking a line and of fugitive counters — imagery of range and pursuit. No source states a one-cell limit; the single-step reading is Schädler's conservative inference, not a text.
**Decision.** A piece slides orthogonally over any number of empty cells; it cannot pass through or land on an occupied cell.
**Decided by.** This is the project's firmest empirical result. **Single-step movement is degenerate** in both traditions — step-move games never resolve through play but run to the move cap, and this holds across agent strength and across search depth 2→3, regardless of how the cap is scored. Slide movement resolves cleanly. The 2024 Crist–Browne computational study reaches the same conclusion independently. Slide is both better-imaged in the sources and the only movement rule that yields a living game.

### D7 · Capture by custodial enclosure — **[A], Strong**
**Sources.** Ovid: a piece caught between two enemies is lost ("two-sided"/custodial capture). Pollux: the Greek capture is by *enclosing* an enemy between two of one's own. The mechanic is the most securely attested rule in either game.
**Decision.** After your move, an enemy piece directly flanked on opposite orthogonal sides by two of yours is captured. Two refinements follow from the texts and from coherence:
- **Closed-by-the-move.** The bracket must be *completed by the move just made* — the standard reading of an active capture.
- **No suicide.** A piece that moves *into* a pre-existing gap between two enemies is safe; capture is only ever initiated by the capturing side. (Several reconstructions add the exception that moving in is legal *if it simultaneously traps* — compatible with our engine, recorded as a permissible variant.)
One move may close several brackets; all such pieces are taken.

### D8 · Corner capture — **[D], Weak (near-inert)**
**Sources.** None addresses corners. Schädler's reconstructions allow a corner piece to be trapped by two counters across its two open sides.
**Decision.** Enabled by default (a corner enemy with both orthogonal neighbours occupied by you is taken), but offered as a toggle.
**Decided by.** Coherence with the enclosure principle. Self-play shows the rule is **near-inert** — it rarely binds and barely moves any health metric — so it is settled on grounds of tidiness, not consequence.

### D9 · Freeing the *incitus* — **[I], Weak → demoted to a variant (Roman only)**
**Sources.** The two-stage capture (a trapped piece is *alligatus* / *incitus*, turned face-down, and removed only on the captor's next turn, *unless* a flanker is itself trapped, which frees it) is **Schädler's inference from a Senecan metaphor**, not a rule any source states outright. Isidore (*Etymologiae* XVIII) supplies the vocabulary — *vagus*, *ordinarius*, *incitus* — and Plautus/Lucilius attest the idiom *ad incitas redigere* ("reduced to immobility," i.e. beaten), but neither describes a *rescue* mechanic.
**Decision.** Off by default. The **Piso (no-freeing) form is the primary Roman reconstruction**; freeing is preserved as a documented variant.
**Decided by.** Both evidence and play. The attestation is genuinely weak — an inference from a simile. And in self-play the rule does not merely slow the game; it **suppresses combat almost entirely** (~0.7 captures per game, against ~18 without it), because closing a bracket exposes the flankers to a rescuing counter-capture, so a careful player simply declines to engage. A game whose every source trades on the imagery of war should not, under skilled play, behave like mutual avoidance. (Full treatment: §4.)

### D10 · Victory — annihilation, blockade, and a material tie-break — **mixed**
- **Blockade / immobilisation — [A], Strong, and foregrounded.** Plato (*Republic* 487b–c) makes being *cornered and unable to move* the defining image; Polybius likens Scipio's cutting-off of an enemy to a skilled *petteia* player; Aristotle (*Politics* 1253a) names the isolated, *azux* piece. To leave the opponent with no legal move is a win. We restore this as a *primary* path, against reconstructions that treat reduction-to-one as the win and immobilisation as a footnote.
- **Annihilation — [A], Strong (Roman).** "A player reduced to a single piece has lost" is the standard Roman terminal condition (a lone piece can never again enclose). Kept co-equal in Latrunculi; secondary in the blockade-centred Greek game.
- **Material tie-break at a cap — [I]/[D], adopted.** Where a game stalls without resolution, it is decided by **pieces standing** (a draw only on equality). This reads *ad incitas redigere* in its plain sense — defeat *is* reduction to immobility — and in self-play it converts the austere blockade game from two-thirds drawn to fully decisive *without* distorting fairness. Adopted as the default finish.

### D11 · Anti-shuffle (no immediate move-undo) — **[D], Weak**
**Sources.** None. A standard board-game device against sterile repetition.
**Decision.** A piece may not return on the very next turn to the cell it just left.
**Decided by.** Coherence with the sources' emphasis on *decisive* play; harmless and conventional.

### D12 · Latrunculi as Roman reception, not a parallel game — **[I], Moderate**
**Decision.** We reconstruct **one** game — **Petteia / Polis** — and treat *Ludus Latrunculorum* as its **Roman reception**, not a second reconstruction. Both share grid, equal pieces, placement, slide movement, and custodial capture; once accretions are stripped, nothing distinguishes them, so positing two independent games is the *less* economical reading. The Roman vocabulary (*latrones*, *ordinarii*) and the *freeing* variant (D9) are the receiving culture's dress and one likely accretion, not a separate game's machinery.
**Decided by.** Parsimony once anachronism is bracketed out, reinforced by **drift-resistance**: the Greek game's blockade core cannot slide toward chess, whereas every attempt to *differentiate* the Roman game (Dux, leaping king, checkmate-style win) does exactly that. Direct transmission is sparsely attested; reception is held as the most economical reading, not a documented lineage. (See reconstruction §4.)

---

## 2. The three contested points, in focus

### §3 · Why there is no Dux
The leader-piece has an attractive pedigree and no evidence. It enters the literature through the Stanway "Doctor's burial" (Camulodunum, mid-1st c. CE): a hinged maple board with metal corners and handles, glass counters of two colours found *arranged* on it. Parlett floated the possibility that the arrangement implied a special piece; Bell turned it into a playable "Dux" with leaping powers; popular rule-sheets inherited the "king bead" from Bell. But three facts cut against it. First, the board is **rectangular** (~2:3) and, in Schädler's assessment, of a British type that was probably **not latticed** — grouping with Baldock and King Harry Lane as a distinct insular tradition, plausibly a Celtic game rather than latrunculi. Second, **no Greek or Roman text** mentions any piece beyond the undifferentiated soldiers/dogs. Third, the physical pieces everywhere — Perugia, the British Museum — are **uniform**, separated only by colour. A reading of one grave's layout cannot outweigh the unbroken silence of the texts. Verdict: **all pieces equal.**

### §4 · Why freeing is a variant, not the rule
What is actually attested is the *vocabulary* of immobility (Isidore's *incitus*; the idiom *ad incitas redigere*) and a *metaphor* in Seneca that Schädler reads as implying delayed removal. The full apparatus — face-down marking, removal next turn, rescue when a flanker is trapped — is reconstruction built on a simile. It may well be right; it is not, on the evidence, *secure*. And it carries a cost that only self-play exposed: against a competent opponent it nearly **abolishes capture**, because every bracket you close can be undone by trapping one of your flankers, so neither side risks contact. The result is a near-bloodless drift to the cap — the opposite of the combative game the sources describe. We therefore keep the simpler **Piso** form primary and document freeing as the historically-interesting, weakly-attested, and demonstrably pacifying variant it is.

### §5 · Why placement, not opposed rows
The only detailed gameplay source, the *Laus Pisonis*, sets the action on the **open board** and speaks of varying the counters cleverly, of reserves, and of breaking a line — the texture of pieces brought onto an empty field, not of two pre-set ranks. The opposed-rows setup, by contrast, has a named and damning verdict against it: Wayte (1892) calls the pawn-rank **a chess analogy for which there is no authority.** Self-play then breaks the tie hard in the same direction — placement is the fairest, least drawish, most varied opening, and the array is actively pathological on larger boards. Evidence and playability point the same way, so we follow them, while noting the price (D12): the two traditions converge.

---

## 3. Summary table

| # | Decision | Choice | Grade | Decided by |
|---|----------|--------|-------|-----------|
| D1 | Board geometry | Latticed orthogonal grid | **[A]** Strong | Varro; Pollux |
| D2 | Pieces / Dux | Equal pieces; **no Dux** | **[A]/[I]** Strong | Pollux, Martial, finds; Stanway rejected |
| D3 | Piece count | Player-agreed; 12 on 7×7 | **[D]** Mod. | Coherence + density |
| D4 | Board size | 7×7 default, tunable | **[A]/[D]** Strong | Attested; off the chessboard (§6C) |
| D5 | Opening | **Open-board placement** | **[I]** Mod. | Laus Pisonis; Wayte; self-play |
| D6 | Movement | **Slide** (rook-like) | **[I]** Strong | Ovid imagery; step is degenerate |
| D7 | Capture | Custodial enclosure, no suicide | **[A]** Strong | Ovid; Pollux |
| D8 | Corner capture | On (toggle) | **[D]** Weak | Coherence; near-inert in play |
| D9 | Freeing (*incitus*) | **Variant only** (Roman) | **[I]** Weak | Seneca inference; suppresses combat |
| D10 | Victory | Blockade + annihilation + material cap | **[A]/[I]** | Plato, Polybius, Aristotle; play |
| D11 | Anti-shuffle | On | **[D]** Weak | Convention |
| D12 | Latrunculi's status | **Roman reception** of one Greek game | **[I]** Mod. | Parsimony + drift-resistance |

---

## 4. Sources, keyed to decisions

**Primary — Greek.** Homer, *Odyssey* 1.107 (*pessoi*) · Plato, *Republic* 487b–c (cornering decides — D10), *Phaedrus* 274c–d (Egyptian origin) · Aristotle, *Politics* 1253a (the *azux* piece — D10) · Polybius (Scipio "like a clever *petteia*-player" — D10) · Pollux, *Onomasticon* IX.97–98 (board = *polis*, pieces = "dogs," two colours, capture by enclosing — D1, D2, D7).

**Primary — Roman.** Varro, *De Lingua Latina* X.22 (grid — D1) · Ovid, *Ars Amatoria* III.357–360 & *Tristia* II.477 (custodial capture, movement — D6, D7) · Martial, *Epigrams* XIV.17 (*latrones* pieces — D2) · Seneca (metaphor read as delayed removal — D9) · *Laus Pisonis* 190–208 (open-board play, glass soldiers, reserves, breaking the line — D5, D6) · Isidore, *Etymologiae* XVIII (the terms *vagus / ordinarius / incitus* — D9) · Plautus, *Poenulus* 905 & Lucilius (*ad incitas redigere* = beaten — D10).

**Secondary (interpreters).** Wayte, *Classical Review* VI (1892) — against the pawn-rank; the *inciti*-as-class minority view · Austin, "Roman Board Games" (1934–35) · Murray, *A History of Board-Games Other Than Chess* (1952) · Bell, *Board and Table Games* (the Dux) · Schädler, *Latrunculi* (1994) and "The Doctor's Game" (2007) — the standard modern reconstruction, the Seneca/freeing inference, and the Stanway analysis · Parlett, *Oxford History of Board Games* (1999) · Crist, Piette, Soemers, Stephenson & Browne (2024), computational study via Ludii — independent support for slide movement and against oversized boards.

---

*Grades are claims about evidence, not about certainty of play. A **[D]** rule may make the better game; a **[A]** rule may make a worse one. The point of separating them is that we are never free to revise the **[A]** rules for the sake of the **[D]** ones — only the reverse.*
