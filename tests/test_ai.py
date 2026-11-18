import pytest

from tuxomage.ai import AI, DIFFICULTIES, evaluate
from tuxomage.engine import PRESETS, Game, Player


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_ai_always_returns_legal_move(difficulty):
    for seed in range(15):
        g = Game(seed=seed, first=seed % 2)
        ai = AI(difficulty, seed=seed)
        while not g.over:
            act = ai.choose(g)
            assert g.is_legal(act)
            g.act(act)


@pytest.mark.parametrize("preset", list(PRESETS))
def test_full_ai_vs_ai_games_complete(preset):
    results = []
    for seed in range(40):
        g = Game(preset, seed=seed, first=seed % 2)
        ais = [AI(DIFFICULTIES[seed % 3], seed=seed), AI(DIFFICULTIES[(seed + 1) % 3], seed=seed + 7)]
        while not g.over:
            g.act(ais[g.current].choose(g))
            assert g.turn < 3000
        results.append(g.winner)
    assert set(results) <= {0, 1, "draw"}


def test_ai_takes_an_immediate_win():
    g = Game(seed=3, first=0)
    me, foe = g.players
    foe.tower, foe.wall = 4, 0
    me.bytes = 10
    me.hand = ["kernel_module", "iptables_rule", "kernel_panic", "bug_hunter", "rookery", "hotfix"]
    for diff in ("normal", "hard"):
        h = g.clone()
        act = AI(diff, seed=1).choose(h)
        h.act(act)
        assert h.over and h.winner == 0          # kernel_panic or bug_hunter, not a detour


def test_ai_discards_when_nothing_is_affordable():
    g = Game(seed=4, first=0)
    me = g.players[0]
    me.code = me.bytes = me.penguins = 0
    me.hand = ["mainframe", "orca_pod", "penguin_datacenter", "rock_solid", "supercomputer", "bastion_wall"]
    act = AI("hard").choose(g)
    assert act.kind == "discard"


def test_evaluate_prefers_better_positions():
    pr = PRESETS["classic"]
    a, b = Player(tower=30), Player(tower=20)
    assert evaluate(a, b, pr) > evaluate(b, a, pr)
    assert evaluate(Player(tower=50), Player(), pr) > 1000
    assert evaluate(Player(), Player(tower=0), pr) > 1000
    assert evaluate(Player(tower=0), Player(), pr) < -1000


def test_hard_beats_easy_more_often():
    wins = 0
    n = 60
    for seed in range(n):
        g = Game(seed=1000 + seed, first=seed % 2)
        ais = [AI("hard", seed=seed), AI("easy", seed=seed + 1)]
        while not g.over:
            g.act(ais[g.current].choose(g))
        wins += g.winner == 0
    assert wins / n > 0.6
