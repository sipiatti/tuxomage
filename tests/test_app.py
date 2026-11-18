"""Headless smoke tests of the pygame front end."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from tuxomage import app as A  # noqa: E402
from tuxomage.i18n import S, set_lang, tr  # noqa: E402


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("TUXOMAGE_DATA_DIR", str(tmp_path))
    a = A.App(headless=True, audio=False)
    yield a
    set_lang("hu")       # (pygame is not quit: cached fonts must stay valid between tests)


def run(app, seconds):
    for _ in range(int(seconds * 60)):
        app.step(1 / 60, ())


def test_all_strings_have_both_languages():
    for key, pair in S.items():
        assert len(pair) == 2 and all(pair), key


def test_every_scene_draws(app):
    menu = A.MenuScene(app)
    for scene in (menu, A.SetupScene(app), A.HelpScene(app, menu), A.SettingsScene(app, menu),
                  A.CardsScene(app, menu), A.StatsScene(app, menu)):
        app.goto(scene)
        run(app, 0.2)
    for lang in ("en", "hu"):
        set_lang(lang)
        app.goto(A.MenuScene(app))
        run(app, 0.1)


def test_full_game_through_the_ui(app):
    """A whole game where an AI plays the human side via PlayScene.human_act."""
    play = A.PlayScene(app, "quick", "easy", first=0, seed=5)
    app.goto(play)
    helper = A.AI("normal", seed=2)
    for _ in range(20000):
        if play.overlay is not None:
            break
        if play.human_turn:
            kind, i = helper.choose(play.game)
            play.human_act(kind, i)
        app.step(1 / 30, ())
    assert play.game.over
    assert isinstance(play.overlay, A.ResultOverlay)
    st = app.store.data["stats"]["easy"]
    assert st["played"] == 1
    # rematch starts a fresh game
    app.rematch()
    assert isinstance(app.scene, A.PlayScene) and app.scene is not play


def test_unaffordable_click_is_refused(app):
    play = A.PlayScene(app, "classic", "normal", first=0, seed=1)
    app.goto(play)
    run(app, 0.3)
    play.game.players[0].hand[0] = "mainframe"
    play.hand_ui[0].cid = "mainframe"
    play.human_act("play", 0)
    assert play.game.current == 0 and play.anim is None
    assert play.toast[0] == tr("need_more", n=24 - play.game.players[0].code, res="Kód")


def test_mouse_play_and_right_click_discard(app):
    play = A.PlayScene(app, "classic", "normal", first=0, seed=2)
    app.goto(play)
    run(app, 0.6)
    play.game.players[0].hand[0] = "iptables_rule"
    play.hand_ui[0].cid = "iptables_rule"
    r = play.slot_rect(0)
    for ev in (pygame.event.Event(pygame.MOUSEMOTION, pos=r.center, rel=(0, 0), buttons=(0, 0, 0)),
               pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=r.center, button=1),
               pygame.event.Event(pygame.MOUSEBUTTONUP, pos=r.center, button=1)):
        app.step(1 / 60, [ev])
    assert play.game.history[-1].kind == "play" and play.game.history[-1].player == 0
    while not play.human_turn and not play.game.over:
        app.step(1 / 30, ())
    if not play.game.over:
        r = play.slot_rect(1)
        n = len(play.game.history)
        app.step(1 / 60, [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=r.center, button=3)])
        assert play.game.history[n].kind == "discard"


def test_give_up_counts_as_loss(app):
    play = A.PlayScene(app, "classic", "hard", first=1, seed=3)
    app.goto(play)
    run(app, 0.2)
    app.give_up(play)
    assert app.store.data["stats"]["hard"]["lost"] == 1
    assert isinstance(app.scene, A.MenuScene)


def test_language_switch(app):
    menu = A.MenuScene(app)
    s = A.SettingsScene(app, menu)
    app.goto(s)
    s._lang()
    assert app.store.settings["lang"] == "en" and tr("play") == "New game"
    s._lang()
    assert tr("play") == "Új játék"
