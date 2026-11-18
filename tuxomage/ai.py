"""Computer opponent: one-ply simulation with a heuristic position score.

For every legal action the AI simulates the outcome on a copy of the two
players (it never peeks at the draw pile or the opponent's hand), scores the
resulting position from its own point of view and picks the best one.
"Play again" cards are evaluated together with the best follow-up card still in
hand.  Difficulty changes how well it plays:

* easy   – noisy evaluation, sometimes a random legal move, no follow-ups;
* normal – full evaluation with a little noise, one follow-up;
* hard   – no noise, two follow-ups and threat-aware weights.
"""
from __future__ import annotations

import copy
import math
import random

from .cards import BY_ID, STOCKS, Card
from .engine import Action, Game, Player, play_card_effect

DIFFICULTIES = ("easy", "normal", "hard")

PARAMS = {
    "easy": {"noise": 9.0, "random": 0.25, "depth": 0, "threat": 0.3},
    "normal": {"noise": 2.0, "random": 0.0, "depth": 1, "threat": 0.8},
    "hard": {"noise": 0.0, "random": 0.0, "depth": 2, "threat": 1.0,
             # tuned by AI-vs-AI self-play (wins ~58 % against "normal", ~80 % against "easy")
             "w": {"tower": 3.0, "prod": 18.0, "colony": 16.0, "stock": 1.3, "wall": 2.6}},
}
WIN = 100000.0


def _tower_value(t: int, target: int) -> float:
    frac = min(1.0, t / max(1, target))
    return 3.0 * t + 70.0 * frac ** 3 - 45.0 / (t + 1)


def _wall_value(w: int, threat: float) -> float:
    cap = 15 + 25 * threat          # walls above the expected incoming damage are worth less
    return 1.8 * min(w, cap) + 0.5 * max(0, w - cap)


DEFAULT_W = {"tower": 3.0, "prod": 9.0, "colony": 10.0, "stock": 0.55, "wall": 1.8, "lookahead": 0}


def evaluate(me: Player, foe: Player, preset, threat_w: float = 1.0, w: dict | None = None) -> float:
    """Score a position from ``me``'s point of view (higher is better).

    With ``w["lookahead"]`` the enemy's coming production is added first, so the
    score reflects the position the enemy will actually play from.
    """
    w = w or DEFAULT_W
    pr = preset
    if w.get("lookahead"):
        foe = copy.copy(foe)
        foe.code += foe.compiler
        foe.bytes += foe.kernel
        foe.penguins += foe.colony
    # victory / defeat (checked like Game._check_victory: mine first, simultaneous = 0)
    mine = me.tower >= pr.win_tower or foe.tower <= 0 or any(me.get(s) >= pr.win_resource for s in STOCKS)
    theirs = foe.tower >= pr.win_tower or me.tower <= 0 or any(foe.get(s) >= pr.win_resource for s in STOCKS)
    if mine and theirs:
        return 0.0
    if mine:
        return WIN
    if theirs:
        return -WIN
    v = 0.0
    for sign, a, b in ((1, me, foe), (-1, foe, me)):
        # how much damage the other side can throw next turn (penguins fuel attack cards)
        threat = threat_w * min(1.0, (b.penguins + b.colony * 2) / 25.0)
        s = w["tower"] / 3.0 * _tower_value(a.tower, pr.win_tower) + w["wall"] / 1.8 * _wall_value(a.wall, threat)
        s += w["prod"] * (a.compiler + a.kernel) + w["colony"] * a.colony
        for st in STOCKS:
            amount = a.get(st)
            s += w["stock"] * min(amount, 40) + 0.15 * max(0, amount - 40)
            s += 60.0 * (amount / pr.win_resource) ** 4
        v += sign * s
    return v


def _simulate(c: Card, me: Player, foe: Player) -> tuple[Player, Player]:
    m, f = copy.copy(me), copy.copy(foe)
    play_card_effect(c, m, f)
    return m, f


class AI:
    def __init__(self, difficulty: str = "normal", seed: int | None = None):
        self.difficulty = difficulty if difficulty in PARAMS else "normal"
        self.p = PARAMS[self.difficulty]
        self.rng = random.Random(seed)
        self.w = {**DEFAULT_W, **self.p.get("w", {})}

    def _eval(self, me, foe, preset) -> float:
        return evaluate(me, foe, preset, self.p["threat"], self.w)

    # ------------------------------------------------------------------
    def _best_follow_up(self, me, foe, hand: list[str], preset, depth: int) -> float:
        """Value of the best continuation after a 'play again' card (draws are unknown)."""
        best = self._eval(me, foe, preset)
        if depth <= 0 or best in (WIN, -WIN):
            return best
        for i, cid in enumerate(hand):
            c = BY_ID[cid]
            if me.get(c.resource) < c.cost:
                continue
            m, f = _simulate(c, me, foe)
            rest = hand[:i] + hand[i + 1:]
            if c.play_again or c.draw_discard:
                val = self._best_follow_up(m, f, rest, preset, depth - 1)
            else:
                val = self._eval(m, f, preset)
            best = max(best, val)
        return best

    def _card_potential(self, c: Card, me: Player, foe: Player, preset) -> float:
        """How useful a card in hand is (used to pick what to discard)."""
        m, f = copy.copy(me), copy.copy(foe)
        m.add(c.resource, max(0, c.cost - m.get(c.resource)))     # pretend we could afford it
        before = self._eval(m, f, preset)
        play_card_effect(c, m, f)
        gain = self._eval(m, f, preset) - before
        missing = max(0, c.cost - me.get(c.resource))
        rate = max(1, me.get({"code": "compiler", "bytes": "kernel", "penguins": "colony"}[c.resource]))
        wait = missing / rate
        return gain / (1.0 + 0.35 * wait) + (6.0 if c.play_again or c.draw_discard else 0.0)

    def score_actions(self, game: Game) -> list[tuple[float, Action]]:
        me, foe, pr = game.me, game.foe, game.preset
        hand = me.hand
        base = self._eval(me, foe, pr)
        out = []
        for act in game.legal_actions():
            c = BY_ID[hand[act.index]]
            if act.kind == "play":
                m, f = _simulate(c, me, foe)
                rest = hand[:act.index] + hand[act.index + 1:]
                if (c.play_again or c.draw_discard) and self.p["depth"] > 0:
                    val = self._best_follow_up(m, f, rest, pr, self.p["depth"])
                    if val >= WIN:
                        val = WIN - 1.0           # a win right now beats a win after a follow-up
                    else:
                        val += 4.0 if c.draw_discard else 0.0
                else:
                    val = self._eval(m, f, pr)
                    if c.play_again or c.draw_discard:
                        val += 6.0
            else:
                # discarding keeps the position; prefer throwing away the least useful card
                val = base - 1.5 - 0.25 * max(-40.0, self._card_potential(c, me, foe, pr))
            if self.p["noise"] and abs(val) < WIN - 10:      # never blur a win or a loss
                val += self.rng.gauss(0, self.p["noise"])
            out.append((val, act))
        return out

    def choose(self, game: Game) -> Action:
        legal = game.legal_actions()
        if not legal:
            raise ValueError("no legal action (game over?)")
        if self.p["random"] and self.rng.random() < self.p["random"]:
            plays = [a for a in legal if a.kind == "play"]
            return self.rng.choice(plays or legal)
        scored = self.score_actions(game)
        best = max(v for v, _ in scored)
        cands = [a for v, a in scored if v >= best - 1e-9]
        return cands[0]
