"""TuxoMage rules engine: players, presets, turn flow, effects and victory.

Pure Python, no pygame, fully deterministic for a given seed.

Turn structure (as in Arcomage):
  1. at the start of a turn the current player's producers add to the stocks;
  2. the player plays an affordable card (pays its cost) *or* discards a card;
  3. the hand is refilled to its size; a "play again" card keeps the turn,
     a "draw / discard" card draws one extra card, forces a discard and then
     keeps the turn;
  4. otherwise the other player's turn starts.
Damage hits the Firewall first, the rest the Tower.  A game is won by building
the Tower to the target, by bringing the enemy Tower to 0, or by collecting the
target amount of any single stock.  If both players meet a condition at the
same moment the game is a draw.
"""
from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass, field

from .cards import ATTRS, BY_ID, DECK, PRODUCERS, STOCKS, Card

MIN_PRODUCER = 1


@dataclass(frozen=True)
class Preset:
    key: str
    tower: int
    wall: int
    producer: int
    stock: int
    win_tower: int
    win_resource: int
    hand_size: int = 6


PRESETS: dict[str, Preset] = {
    "classic": Preset("classic", tower=20, wall=5, producer=2, stock=5, win_tower=50, win_resource=150),
    "quick": Preset("quick", tower=15, wall=5, producer=3, stock=10, win_tower=40, win_resource=100),
    "fortress": Preset("fortress", tower=25, wall=20, producer=2, stock=10, win_tower=75, win_resource=200),
    "marathon": Preset("marathon", tower=30, wall=10, producer=3, stock=15, win_tower=100, win_resource=300),
}
DEFAULT_PRESET = "classic"


@dataclass
class Player:
    tower: int = 20
    wall: int = 5
    compiler: int = 2
    kernel: int = 2
    colony: int = 2
    code: int = 5
    bytes: int = 5
    penguins: int = 5
    hand: list = field(default_factory=list)

    def get(self, attr: str) -> int:
        return getattr(self, attr)

    def set(self, attr: str, value: int) -> None:
        low = MIN_PRODUCER if attr in PRODUCERS else 0
        setattr(self, attr, max(low, int(value)))

    def add(self, attr: str, n: int) -> None:
        self.set(attr, self.get(attr) + n)

    def damage(self, n: int) -> None:
        """Damage hits the wall first, the remainder the tower."""
        if n <= 0:
            return
        absorbed = min(self.wall, n)
        self.wall -= absorbed
        self.tower = max(0, self.tower - (n - absorbed))

    def stats(self) -> dict:
        return {a: self.get(a) for a in ATTRS}

    def can_afford(self, c: Card) -> bool:
        return self.get(c.resource) >= c.cost


@dataclass
class Action:
    kind: str          # "play" | "discard"
    index: int         # hand index

    def __iter__(self):
        return iter((self.kind, self.index))


@dataclass
class Event:
    """What happened in one action (consumed by the UI and the log)."""
    player: int
    kind: str
    card: str
    turn: int
    before: tuple
    after: tuple
    again: bool = False
    production: tuple | None = None


def _cmp(a: int, op: str, b: int) -> bool:
    return a < b if op == "<" else a > b if op == ">" else a == b


def _val(term, me: Player, foe: Player) -> int:
    if isinstance(term, int):
        return term
    who, attr = term
    return (me if who == "self" else foe).get(attr)


def _targets(who: str, me: Player, foe: Player):
    return (me,) if who in ("self", "it") else (foe,) if who == "enemy" else (me, foe)


def apply_ops(ops, me: Player, foe: Player) -> None:
    """Execute card operations; ``me`` is the player who plays the card."""
    for op in ops:
        kind = op[0]
        if kind == "add":
            _, who, attr, n = op
            for p in _targets(who, me, foe):
                p.add(attr, n)
        elif kind == "dmg":
            for p in _targets(op[1], me, foe):
                p.damage(op[2])
        elif kind == "tdmg":
            for p in _targets(op[1], me, foe):
                p.set("tower", p.tower - op[2])
        elif kind == "if":
            _, (lhs, cmp, rhs), then, other = op
            apply_ops(then if _cmp(_val(lhs, me, foe), cmp, _val(rhs, me, foe)) else other, me, foe)
        elif kind == "max":
            hi = max(me.get(op[1]), foe.get(op[1]))
            me.set(op[1], hi)
            foe.set(op[1], hi)
        elif kind == "copy":
            if me.get(op[1]) < foe.get(op[1]):
                me.set(op[1], foe.get(op[1]))
        elif kind == "swap":
            a, b = me.get(op[1]), foe.get(op[1])
            me.set(op[1], b)
            foe.set(op[1], a)
        elif kind == "steal":
            for attr, n in op[1]:
                lost = min(n, foe.get(attr))
                foe.add(attr, -lost)
                me.add(attr, math.ceil(lost / 2))
        elif kind == "lowest":
            low = min(me.get(op[1]), foe.get(op[1]))
            for p in (me, foe):
                if p.get(op[1]) == low:
                    apply_ops(op[2], p, foe if p is me else me)
        else:
            raise ValueError(f"unknown op {op!r}")


def play_card_effect(c: Card, me: Player, foe: Player) -> None:
    """Pay the cost and apply the effect (no hand handling)."""
    me.add(c.resource, -c.cost)
    apply_ops(c.ops, me, foe)


class Deck:
    """Endless weighted draw pile (like Arcomage: every draw is from the full deck)."""

    def __init__(self, rng: random.Random, cards: list[Card] | None = None):
        self.rng = rng
        self.cards = cards or DECK
        self.ids = [c.id for c in self.cards]
        self.weights = [c.weight for c in self.cards]

    def draw(self) -> str:
        return self.rng.choices(self.ids, self.weights)[0]


class Game:
    def __init__(self, preset: Preset | str = DEFAULT_PRESET, seed: int | None = None, first: int = 0):
        self.preset = PRESETS[preset] if isinstance(preset, str) else preset
        self.seed = seed if seed is not None else random.randrange(1 << 30)
        self.rng = random.Random(self.seed)
        self.deck = Deck(self.rng)
        pr = self.preset
        self.players = [Player(pr.tower, pr.wall, pr.producer, pr.producer, pr.producer, pr.stock, pr.stock, pr.stock)
                        for _ in range(2)]
        for p in self.players:
            p.hand = [self.deck.draw() for _ in range(pr.hand_size)]
        self.current = first
        self.turn = 1                  # counts turns of both players
        self.phase = "play"            # "play" | "discard" | "over"
        self.winner: int | str | None = None   # 0, 1, "draw"
        self.reason: str | None = None
        self.history: list[Event] = []
        self.last_production: tuple | None = None
        self._start_turn()

    # ----------------------------------------------------------- helpers
    @property
    def me(self) -> Player:
        return self.players[self.current]

    @property
    def foe(self) -> Player:
        return self.players[1 - self.current]

    @property
    def over(self) -> bool:
        return self.phase == "over"

    def clone(self) -> "Game":
        return copy.deepcopy(self)

    def hand_cards(self, who: int | None = None) -> list[Card]:
        return [BY_ID[c] for c in self.players[self.current if who is None else who].hand]

    def can_play(self, i: int) -> bool:
        if self.phase != "play" or not 0 <= i < len(self.me.hand):
            return False
        return self.me.can_afford(BY_ID[self.me.hand[i]])

    def can_discard(self, i: int) -> bool:
        if self.over or not 0 <= i < len(self.me.hand):
            return False
        if not BY_ID[self.me.hand[i]].undiscardable:
            return True
        # safety valve: if every card is undiscardable and nothing is playable, allow it
        return not any(self._normal_actions())

    def _normal_actions(self):
        hand = self.me.hand
        for i, cid in enumerate(hand):
            c = BY_ID[cid]
            if self.phase == "play" and self.me.can_afford(c):
                yield Action("play", i)
            if not c.undiscardable:
                yield Action("discard", i)

    def legal_actions(self) -> list[Action]:
        if self.over:
            return []
        acts = list(self._normal_actions())
        if not acts:
            acts = [Action("discard", i) for i in range(len(self.me.hand))]
        return acts

    def is_legal(self, action) -> bool:
        kind, i = action
        return self.can_play(i) if kind == "play" else self.can_discard(i) if kind == "discard" else False

    # ----------------------------------------------------------- flow
    def _start_turn(self) -> None:
        p = self.me
        gain = (p.compiler, p.kernel, p.colony)
        p.code += p.compiler
        p.bytes += p.kernel
        p.penguins += p.colony
        self.last_production = (self.current, gain)
        self._check_victory()

    def _refill(self, p: Player) -> None:
        while len(p.hand) < self.preset.hand_size:
            p.hand.append(self.deck.draw())

    def act(self, action) -> Event:
        kind, i = action
        if not self.is_legal(action):
            raise ValueError(f"illegal action {action!r} in phase {self.phase}")
        who = self.current
        p, o = self.me, self.foe
        before = (p.stats(), o.stats())
        cid = p.hand.pop(i)
        c = BY_ID[cid]
        again = False
        if kind == "play":
            play_card_effect(c, p, o)
            self._refill(p)
            if c.draw_discard:
                p.hand.append(self.deck.draw())       # one extra card, then a forced discard
                self.phase = "discard"
                again = True
            elif c.play_again:
                again = True
        else:
            self._refill(p)
            if self.phase == "discard":               # the forced discard of a draw/discard card
                self.phase = "play"
                again = True
        ev = Event(who, kind, cid, self.turn, before, (p.stats(), o.stats()), again)
        self.history.append(ev)
        self._check_victory()
        if not self.over and not again:
            self.current = 1 - self.current
            self.turn += 1
            self.phase = "play"
            self._start_turn()
            ev.production = self.last_production
        return ev

    # ----------------------------------------------------------- victory
    def wins(self, k: int) -> str | None:
        p, o = self.players[k], self.players[1 - k]
        pr = self.preset
        if p.tower >= pr.win_tower:
            return "tower"
        if o.tower <= 0:
            return "destroy"
        if any(p.get(s) >= pr.win_resource for s in STOCKS):
            return "resource"
        return None

    def _check_victory(self) -> None:
        w0, w1 = self.wins(0), self.wins(1)
        if w0 and w1:
            self.winner, self.reason, self.phase = "draw", "draw", "over"
        elif w0 or w1:
            self.winner = 0 if w0 else 1
            self.reason = w0 or w1
            self.phase = "over"


def score(game: Game, k: int, difficulty: str = "normal") -> int:
    """Final score for player k (only meaningful for a win; losses score 0)."""
    if game.winner != k:
        return 0
    p = game.players[k]
    mult = {"easy": 1.0, "normal": 1.5, "hard": 2.0}.get(difficulty, 1.0)
    own_turns = max(1, (game.turn + 1) // 2)
    base = 500 + 4 * p.tower + 2 * p.wall + sum(p.get(s) for s in STOCKS) // 2
    speed = max(0, 400 - 8 * own_turns)
    return int((base + speed) * mult)
