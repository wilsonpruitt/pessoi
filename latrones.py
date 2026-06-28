"""
latrones.py  —  An engine for testing reconstructed rulesets of
Ludus Latrunculorum and Petteia / Polis.

Design goal: every rule that the ancient sources DO NOT fix (the [D] tags in
the reconstruction document) is a pluggable flag on RuleSet. The sources fix
custodial capture and a grid board; everything else we sweep and let
playability decide.

Conventions
-----------
Board is a flat list of length W*H. Cell values: 0 empty, 1 player one,
2 player two. Players are 1 and 2. "Frozen" (incitus) pieces still occupy a
cell but are inert; tracked in `frozen` mapping cell -> capturer.
"""

from __future__ import annotations
from dataclasses import dataclass, field, replace
from collections import Counter
import math
import random

ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))


# --------------------------------------------------------------------------- #
#  Rule configuration                                                         #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RuleSet:
    name: str = "custom"
    width: int = 7               # 7×7 canonical default: attested, not the
    height: int = 7              # 8×8 chessboard nor a Go grid (see D4)
    pieces: int = 12             # per player (~half the 49-cell board)

    # setup: "placement" (empty board, alternate drops = Roman vagi phase)
    #        "array"     (opposed rows, no placement phase = our Greek default)
    setup: str = "placement"

    # movement: "step" (one orthogonal cell) or "slide" (rook-like)
    movement: str = "slide"
    leap: bool = False            # may a step/slide jump one friendly piece?

    corner_capture: bool = True   # can a corner piece be bracketed on its 2 sides?
    freeing: bool = False         # incitus delayed-removal + rescue (Roman only)
    anti_shuffle: bool = True     # forbid immediately reversing your own last move

    # victory: "annihilate" (reduce foe to <=1), "blockade" (foe has no move),
    #          "both" (either)
    victory: str = "blockade"
    min_pieces: int = 1           # annihilation threshold (foe count <= this -> loss)

    move_cap: int = 200           # ply cap -> draw
    cap_rule: str = "material"    # canonical: capped game decided by pieces standing
    no_second_rescue: bool = False  # a freed incitus, if re-trapped, dies at once

    def cells(self):
        return self.width * self.height


# --------------------------------------------------------------------------- #
#  Game state                                                                 #
# --------------------------------------------------------------------------- #
class Game:
    def __init__(self, rules: RuleSet, rng: random.Random | None = None):
        self.r = rules
        self.rng = rng or random.Random()
        self.W, self.H = rules.width, rules.height
        self.board = [0] * rules.cells()
        self.ids = [0] * rules.cells()         # stable per-piece identity
        self._next_id = 1
        self.rescued = set()                   # ids freed once already
        self.frozen = {}                       # cell -> capturer player
        self.to_move = 1
        self.ply = 0
        self.move_plies = 0
        self.last_move = {1: None, 2: None}    # player -> (from, to)
        self.to_place = {1: 0, 2: 0}           # remaining pieces to place
        self.phase = 1                         # 1 = movement (default)
        self.first_movement_move = None        # opening signature for metrics
        self.result = None                     # None | 1 | 2 | 0 (draw)
        self._setup()

    # -- coordinate helpers -------------------------------------------------- #
    def idx(self, x, y):  return y * self.W + x
    def xy(self, i):      return (i % self.W, i // self.W)
    def on(self, x, y):   return 0 <= x < self.W and 0 <= y < self.H

    def _new_id(self):
        i = self._next_id
        self._next_id += 1
        return i

    def count(self, p):
        return sum(1 for v in self.board if v == p)

    def clone(self):
        g = Game.__new__(Game)
        g.r = self.r
        g.rng = self.rng
        g.W, g.H = self.W, self.H
        g.board = self.board[:]
        g.ids = self.ids[:]
        g._next_id = self._next_id
        g.rescued = set(self.rescued)
        g.frozen = dict(self.frozen)
        g.to_move = self.to_move
        g.ply = self.ply
        g.move_plies = self.move_plies
        g.last_move = dict(self.last_move)
        g.to_place = dict(self.to_place)
        g.phase = self.phase
        g.first_movement_move = self.first_movement_move
        g.result = self.result
        return g

    # -- setup --------------------------------------------------------------- #
    def _setup(self):
        if self.r.setup == "placement":
            self.phase = 0
            self.to_place = {1: self.r.pieces, 2: self.r.pieces}
        else:  # opposed array
            self.phase = 1
            self._fill_array()

    def _fill_array(self):
        n = self.r.pieces
        # player 1 fills from the bottom rows up; player 2 from the top down
        p1 = []
        for y in range(self.H):
            for x in range(self.W):
                p1.append(self.idx(x, y))
                if len(p1) >= n:
                    break
            if len(p1) >= n:
                break
        p2 = []
        for y in range(self.H - 1, -1, -1):
            for x in range(self.W - 1, -1, -1):
                p2.append(self.idx(x, y))
                if len(p2) >= n:
                    break
            if len(p2) >= n:
                break
        for i in p1:
            self.board[i] = 1
            self.ids[i] = self._new_id()
        for i in p2:
            self.board[i] = 2
            self.ids[i] = self._new_id()

    # -- move generation ----------------------------------------------------- #
    def legal_moves(self):
        """Return a list of actions for self.to_move.
        Placement action: ("place", cell)
        Movement action:  ("move", frm, to)
        """
        p = self.to_move
        if self.phase == 0:
            return [("place", i) for i, v in enumerate(self.board) if v == 0]

        moves = []
        forbidden = None
        if self.r.anti_shuffle and self.last_move[p]:
            frm, to = self.last_move[p]
            forbidden = (to, frm)            # reverse of own last move

        for i, v in enumerate(self.board):
            if v != p or i in self.frozen:
                continue
            x, y = self.xy(i)
            for dx, dy in ORTHO:
                if self.r.movement == "step":
                    nx, ny = x + dx, y + dy
                    if self.on(nx, ny):
                        j = self.idx(nx, ny)
                        if self.board[j] == 0:
                            self._add(moves, i, j, forbidden)
                        elif self.r.leap and self.board[j] == p:
                            lx, ly = nx + dx, ny + dy
                            if self.on(lx, ly) and self.board[self.idx(lx, ly)] == 0:
                                self._add(moves, i, self.idx(lx, ly), forbidden)
                else:  # slide
                    nx, ny = x + dx, y + dy
                    leapt = False
                    while self.on(nx, ny):
                        j = self.idx(nx, ny)
                        if self.board[j] == 0:
                            self._add(moves, i, j, forbidden)
                        elif self.r.leap and self.board[j] == p and not leapt:
                            leapt = True   # jump a single friendly, keep sliding
                        else:
                            break
                        nx, ny = nx + dx, ny + dy
        return moves

    def _add(self, moves, frm, to, forbidden):
        if forbidden is not None and (frm, to) == forbidden:
            return
        moves.append(("move", frm, to))

    # -- applying an action -------------------------------------------------- #
    def apply(self, action):
        p = self.to_move
        if self.r.freeing:
            self._resolve_frozen(p)          # collect captures pending from last turn

        if action[0] == "place":
            _, cell = action
            self.board[cell] = p
            self.ids[cell] = self._new_id()
            self.to_place[p] -= 1
            # no captures during the vagi phase
            if self.to_place[1] == 0 and self.to_place[2] == 0:
                self.phase = 1
        else:
            _, frm, to = action
            self.board[frm] = 0
            self.board[to] = p
            self.ids[to] = self.ids[frm]
            self.ids[frm] = 0
            self.last_move[p] = (frm, to)
            if self.first_movement_move is None:
                self.first_movement_move = (frm, to)
            self._capture_from(to, p)
            self.move_plies += 1

        self.ply += 1
        self.to_move = 3 - p
        self._check_end()
        return self.result

    # -- custodial capture --------------------------------------------------- #
    def _is_flanker(self, cell, p):
        """A cell counts as a flanker for player p if it holds p's piece and
        is not itself frozen (an incitus cannot help capture)."""
        return self.board[cell] == p and cell not in self.frozen

    def _capture_from(self, to, p):
        """Resolve captures created by p's piece arriving at `to`."""
        foe = 3 - p
        x, y = self.xy(to)
        captured = []
        # line captures: enemy adjacent, friendly beyond
        for dx, dy in ORTHO:
            ex, ey = x + dx, y + dy
            bx, by = x + 2 * dx, y + 2 * dy
            if self.on(ex, ey) and self.on(bx, by):
                e = self.idx(ex, ey)
                b = self.idx(bx, by)
                if self.board[e] == foe and self._is_flanker(b, p):
                    captured.append(e)
        # corner captures: a corner enemy bracketed on its two orthogonal sides
        if self.r.corner_capture:
            for c in self._corners():
                if self.board[c] == foe:
                    cx, cy = self.xy(c)
                    nbrs = [self.idx(cx + dx, cy + dy)
                            for dx, dy in ORTHO if self.on(cx + dx, cy + dy)]
                    if len(nbrs) == 2 and all(self._is_flanker(n, p) for n in nbrs):
                        # only trigger if this move was one of the two flankers
                        if to in nbrs:
                            captured.append(c)
        for e in captured:
            if self.r.freeing and not (
                    self.r.no_second_rescue and self.ids[e] in self.rescued):
                self.frozen[e] = p            # mark incitus, remove next turn
            else:
                self.board[e] = 0             # immediate removal
                self.ids[e] = 0

    def _corners(self):
        W, H = self.W, self.H
        return [self.idx(0, 0), self.idx(W - 1, 0),
                self.idx(0, H - 1), self.idx(W - 1, H - 1)]

    def _resolve_frozen(self, p):
        """At the start of capturer p's turn: remove still-trapped inciti,
        or release any that have been rescued (a flanker gone or itself frozen)."""
        done = []
        for cell, capturer in list(self.frozen.items()):
            if capturer != p:
                continue
            cx, cy = self.xy(cell)
            # rebuild the bracketing test in all 4 axes
            still_trapped = False
            for dx, dy in ((1, 0), (0, 1)):
                ax, ay = cx + dx, cy + dy
                bx, by = cx - dx, cy - dy
                if self.on(ax, ay) and self.on(bx, by):
                    a, b = self.idx(ax, ay), self.idx(bx, by)
                    if self._is_flanker(a, p) and self._is_flanker(b, p):
                        still_trapped = True
            if not still_trapped and cell in self._corners():
                cnbrs = [self.idx(cx + dx, cy + dy)
                         for dx, dy in ORTHO if self.on(cx + dx, cy + dy)]
                if self.r.corner_capture and len(cnbrs) == 2 \
                        and all(self._is_flanker(n, p) for n in cnbrs):
                    still_trapped = True
            if still_trapped:
                self.board[cell] = 0          # remove the incitus
                self.ids[cell] = 0
            else:
                self.rescued.add(self.ids[cell])  # freed once; no second life
            done.append(cell)                 # resolved either way
        for cell in done:
            self.frozen.pop(cell, None)        # release survivors back to play

    # -- termination --------------------------------------------------------- #
    def _check_end(self):
        if self.move_plies >= self.r.move_cap:
            if self.r.cap_rule == "material":
                c1, c2 = self.count(1), self.count(2)
                self.result = 1 if c1 > c2 else (2 if c2 > c1 else 0)
            else:
                self.result = 0
            return
        if self.phase == 0:
            return                       # no victory during the vagi/placement phase
        c1, c2 = self.count(1), self.count(2)
        vic = self.r.victory
        if vic in ("annihilate", "both"):
            if c2 <= self.r.min_pieces:
                self.result = 1; return
            if c1 <= self.r.min_pieces:
                self.result = 2; return
        # blockade: the player to move has no legal action
        if self.phase == 1 and not self.legal_moves():
            if vic in ("blockade", "both"):
                self.result = 3 - self.to_move
            else:
                self.result = 0
            return


# --------------------------------------------------------------------------- #
#  Agents                                                                      #
# --------------------------------------------------------------------------- #
class RandomAgent:
    def __init__(self, rng): self.rng = rng
    def choose(self, g, moves): return self.rng.choice(moves)


class HeuristicAgent:
    """1-ply greedy: prefer moves that capture now, sit near the centre, and
    (cheaply) avoid walking into a closed bracket. Epsilon-random for variety."""
    def __init__(self, rng, eps=0.08): self.rng, self.eps = rng, eps

    def _captures_if(self, g, frm, to, p):
        # count captures created by moving frm->to without mutating long-term
        b = g.board
        ofrm, oto = b[frm], b[to]
        b[frm], b[to] = 0, p
        n = 0
        foe = 3 - p
        x, y = g.xy(to)
        for dx, dy in ORTHO:
            ex, ey = x + dx, y + dy
            bx, by = x + 2 * dx, y + 2 * dy
            if g.on(ex, ey) and g.on(bx, by):
                if b[g.idx(ex, ey)] == foe and g._is_flanker(g.idx(bx, by), p):
                    n += 1
        b[frm], b[to] = ofrm, oto
        return n

    def choose(self, g, moves):
        if self.rng.random() < self.eps:
            return self.rng.choice(moves)
        p = g.to_move
        cx, cy = (g.W - 1) / 2, (g.H - 1) / 2
        best, best_score = [], -1e9
        for m in moves:
            if m[0] == "place":
                _, cell = m
                x, y = g.xy(cell)
                s = -(abs(x - cx) + abs(y - cy)) * 0.1   # cluster centrally
            else:
                _, frm, to = m
                x, y = g.xy(to)
                s = 10 * self._captures_if(g, frm, to, p) \
                    - (abs(x - cx) + abs(y - cy)) * 0.05
            if s > best_score:
                best_score, best = s, [m]
            elif s == best_score:
                best.append(m)
        return self.rng.choice(best)


# --------------------------------------------------------------------------- #
#  Play + metrics                                                             #
# --------------------------------------------------------------------------- #
def play_game(rules, agent1, agent2, rng):
    g = Game(rules, rng)
    agents = {1: agent1, 2: agent2}
    branching = []
    while g.result is None:
        moves = g.legal_moves()
        if not moves:
            # safety net (should be caught by _check_end)
            g.result = 3 - g.to_move
            break
        if g.phase == 1:
            branching.append(len(moves))
        g.apply(agents[g.to_move].choose(g, moves))
    margin = g.count(1) - g.count(2)
    return {
        "result": g.result,
        "plies": g.move_plies,
        "branching": sum(branching) / len(branching) if branching else 0.0,
        "opening": g.first_movement_move,
        "margin": margin,
    }


def wilson(k, n, z=1.96):
    """Wilson score interval for a binomial proportion k/n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def mean_ci(xs, z=1.96):
    n = len(xs)
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    m = sum(xs) / n
    if n < 2:
        return (m, m, m)
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    sem = math.sqrt(var / n)
    return (m, m - z * sem, m + z * sem)


def default_agent(rng):
    return HeuristicAgent(rng)


def evaluate(rules, games=40, seed=0, agent_factory=None):
    """Play `games` self-play games and return health metrics with 95% CIs.
    agent_factory(rng) -> agent. Defaults to the capture-greedy heuristic."""
    if agent_factory is None:
        agent_factory = default_agent
    rng = random.Random(seed)
    res = Counter()
    plies, branch, openings = [], [], Counter()
    first_player_wins, decided = 0, 0
    for _ in range(games):
        a = agent_factory(rng)
        b = agent_factory(rng)
        out = play_game(rules, a, b, rng)
        res[out["result"]] += 1
        plies.append(out["plies"])
        branch.append(out["branching"])
        if out["opening"]:
            openings[out["opening"]] += 1
        if out["result"] in (1, 2):
            decided += 1
            if out["result"] == 1:
                first_player_wins += 1
    n = games
    total = sum(openings.values())
    ent = 0.0
    if total:
        for c in openings.values():
            pr = c / total
            ent -= pr * math.log(pr)
        ent /= math.log(len(openings)) if len(openings) > 1 else 1.0
    pl_m, pl_lo, pl_hi = mean_ci(plies)
    br_m, _, _ = mean_ci(branch)
    return {
        "name": rules.name,
        "games": n,
        "draw_rate": res[0] / n,
        "draw_ci": wilson(res[0], n),
        "decisiveness": decided / n,
        "p1_winrate": (first_player_wins / decided) if decided else float("nan"),
        "p1_ci": wilson(first_player_wins, decided),
        "mean_plies": pl_m,
        "plies_ci": (pl_lo, pl_hi),
        "mean_branching": br_m,
        "opening_entropy": ent,
        "distinct_openings": len(openings),
    }


if __name__ == "__main__":
    # smoke test
    rs = RuleSet(name="smoke", width=7, height=7, pieces=10, move_cap=120)
    print(evaluate(rs, games=10, seed=1))
