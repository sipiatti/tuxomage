import random

import pytest

from tuxomage.cards import BY_ID
from tuxomage.engine import PRESETS, Action, Game, Player, apply_ops, score


def test_presets_and_start_values():
    g = Game("classic", seed=1, first=0)
    p0, p1 = g.players
    pr = PRESETS["classic"]
    assert (pr.tower, pr.wall, pr.producer, pr.stock, pr.win_tower, pr.win_resource) == (20, 5, 2, 5, 50, 150)
    # first player already produced for the opening turn
    assert (p0.code, p0.bytes, p0.penguins) == (7, 7, 7)
    assert (p1.code, p1.bytes, p1.penguins) == (5, 5, 5)
    assert len(p0.hand) == len(p1.hand) == 6
    for key in PRESETS:
        Game(key, seed=2)


def test_damage_hits_wall_first_then_tower():
    p = Player(tower=20, wall=5)
    p.damage(8)
    assert (p.wall, p.tower) == (0, 17)
    p.damage(100)
    assert p.tower == 0 and p.wall == 0


def test_clamps():
    p = Player(compiler=1, code=2)
    p.add("compiler", -5)
    p.add("code", -9)
    p.add("wall", -9)
    assert (p.compiler, p.code, p.wall) == (1, 0, 0)


def _force_hand(g, who, cards):
    g.players[who].hand = list(cards)


def test_play_pays_cost_refills_and_passes_turn():
    g = Game(seed=3, first=0)
    _force_hand(g, 0, ["iptables_rule"] * 6)
    me = g.players[0]
    code, wall = me.code, me.wall
    ev = g.act(Action("play", 0))
    assert ev.kind == "play" and not ev.again
    assert me.code == code - 2 and me.wall == wall + 3
    assert len(me.hand) == 6
    assert g.current == 1 and g.turn == 2
    # the other player has produced
    assert g.players[1].code == 5 + 2


def test_cannot_play_unaffordable_but_can_discard():
    g = Game(seed=4, first=0)
    _force_hand(g, 0, ["mainframe"] * 6)
    assert not g.can_play(0)
    with pytest.raises(ValueError):
        g.act(Action("play", 0))
    assert g.can_discard(0)
    g.act(Action("discard", 0))
    assert g.current == 1


def test_play_again_keeps_turn_without_production():
    g = Game(seed=5, first=0)
    _force_hand(g, 0, ["hotfix", "iptables_rule", "iptables_rule", "iptables_rule", "iptables_rule", "iptables_rule"])
    me = g.players[0]
    code = me.code
    ev = g.act(Action("play", 0))
    assert ev.again and g.current == 0 and g.phase == "play"
    assert me.code == code - 1
    g.act(Action("play", 0))
    assert g.current == 1


def test_draw_discard_flow():
    g = Game(seed=6, first=0)
    _force_hand(g, 0, ["grep", "iptables_rule", "iptables_rule", "iptables_rule", "iptables_rule", "iptables_rule"])
    g.act(Action("play", 0))
    assert g.phase == "discard" and g.current == 0
    assert len(g.players[0].hand) == 7
    assert not g.can_play(0)
    assert all(a.kind == "discard" for a in g.legal_actions())
    g.act(Action("discard", 0))
    assert g.phase == "play" and g.current == 0 and len(g.players[0].hand) == 6
    g.act(Action("play", 0))
    assert g.current == 1


def test_undiscardable_card():
    g = Game(seed=7, first=0)
    _force_hand(g, 0, ["pinned_config", "mainframe", "mainframe", "mainframe", "mainframe", "mainframe"])
    assert not g.can_discard(0)
    assert g.can_discard(1)
    # only undiscardable + unaffordable -> safety valve allows a discard
    _force_hand(g, 0, ["pinned_config"] * 6)
    g.players[0].bytes = 0
    assert g.legal_actions() and all(a.kind == "discard" for a in g.legal_actions())


@pytest.mark.parametrize("how", ["tower", "destroy", "resource"])
def test_win_conditions(how):
    g = Game(seed=8, first=0)
    me, foe = g.players
    if how == "tower":
        me.tower = 48
        _force_hand(g, 0, ["kernel_module"] * 6)
    elif how == "destroy":
        foe.tower, foe.wall = 3, 0
        _force_hand(g, 0, ["kernel_panic"] * 6)
    else:
        me.code = 149
        _force_hand(g, 0, ["lucky_commit"] * 6)
    me.bytes = max(me.bytes, 10)
    g.act(Action("play", 0))
    assert g.over and g.winner == 0 and g.reason == how
    assert g.legal_actions() == []
    assert score(g, 0, "hard") > score(g, 0, "easy") > 0
    assert score(g, 1) == 0


def test_resource_win_at_start_of_turn_by_production():
    g = Game(seed=9, first=0)
    g.players[1].penguins = 149
    _force_hand(g, 0, ["iptables_rule"] * 6)
    g.act(Action("play", 0))
    assert g.over and g.winner == 1 and g.reason == "resource"


def test_simultaneous_win_is_a_draw():
    g = Game(seed=10, first=0)
    me, foe = g.players
    me.tower, me.wall = 5, 0
    foe.tower, foe.wall = 5, 0
    _force_hand(g, 0, ["fork_bomb"] * 6)
    me.bytes = 20
    g.act(Action("play", 0))
    assert g.over and g.winner == "draw"


def test_random_games_always_finish_and_stay_valid():
    for seed in range(60):
        rng = random.Random(seed)
        g = Game(rng.choice(list(PRESETS)), seed=seed, first=seed % 2)
        while not g.over:
            acts = g.legal_actions()
            assert acts
            g.act(rng.choice(acts))
            for p in g.players:
                assert p.tower >= 0 and p.wall >= 0
                assert min(p.compiler, p.kernel, p.colony) >= 1
                assert min(p.code, p.bytes, p.penguins) >= 0
                assert len(p.hand) in (6, 7)
            assert g.turn < 5000
        assert g.winner in (0, 1, "draw")


def test_seed_is_deterministic():
    def run(seed):
        g = Game(seed=seed)
        rng = random.Random(1)
        while not g.over:
            g.act(rng.choice(g.legal_actions()))
        return g.turn, g.winner, [p.stats() for p in g.players]
    assert run(42) == run(42)


def test_apply_ops_unknown_raises():
    with pytest.raises(ValueError):
        apply_ops([("nope",)], Player(), Player())
