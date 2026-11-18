#!/usr/bin/env python3
"""Render screenshots of every screen headlessly (SDL dummy driver).

    python3 tools/screenshots.py [OUTPUT_DIR]      (default: ./screenshots)
"""
import os
import sys
import tempfile
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["TUXOMAGE_DATA_DIR"] = tempfile.mkdtemp(prefix="tuxomage-shots-")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from tuxomage import app as A  # noqa: E402
from tuxomage.i18n import set_lang  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "screenshots")
OUT.mkdir(parents=True, exist_ok=True)
app = A.App(headless=True, audio=False)


def run(seconds, events=()):
    events = list(events)
    steps = max(1, int(seconds * 60))
    for i in range(steps):
        app.step(1 / 60, events if i == 0 else ())


def shot(name):
    pygame.image.save(app.screen, str(OUT / f"{name}.png"))
    print("saved", OUT / f"{name}.png")


def motion(pos):
    pygame.mouse.set_pos(pos)
    return [pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0))]


run(1.2)
shot("01_menu")
app.goto(A.SetupScene(app))
run(0.6)
shot("02_setup")

# a game where the player starts; play a few turns automatically to fill the log
play = A.PlayScene(app, "classic", "normal", first=0, seed=7)
app.goto(play)
run(1.0)
shot("03_game_start")
helper = A.AI("normal", seed=3)
for _ in range(5):
    while not play.human_turn and not play.game.over:
        run(0.1)
    if play.game.over:
        break
    kind, i = helper.choose(play.game)
    play.human_act(kind, i)
    run(0.2)
while not play.human_turn and not play.game.over:
    run(0.1)
run(0.5)
shot("04_game_midgame")
# hover a card -> zoom
r = play.slot_rect(2)
run(0.4, motion(r.center))
shot("05_card_hover")
# AI turn: a fresh game where the computer starts; catch its card in flight and on the table
run(0.2, motion((10, 10)))
main_play = play
play = A.PlayScene(app, "classic", "hard", first=1, seed=21)
app.goto(play)
for _ in range(600):
    run(1 / 60)
    if play.anim and play.anim["who"] == 1 and play.anim["t"] > play.anim["dur"] * 0.75:
        break
shot("06_ai_turn_flight")
for _ in range(600):
    run(1 / 60)
    if play.anim is None and play.center_by == 1 and play.center_card:
        break
run(0.3)
shot("07_ai_card_shown")
play = main_play
app.goto(play)
run(0.2)

# victory: give the player a winning card
g = play.game
while not play.human_turn and not g.over:
    run(0.1)
if not g.over:
    g.players[0].tower = g.preset.win_tower - 8
    g.players[0].bytes = 30
    g.players[0].hand[0] = "penguin_datacenter"
    play._sync_hand()
    play.hand_ui[0].cid = "penguin_datacenter"
    play.target[0]["tower"] = play.view[0]["tower"] = g.players[0].tower
    play.human_act("play", 0)
run(3.0)
shot("08_victory")

# defeat screen (English)
app.store.settings["lang"] = "en"
set_lang("en")
play = A.PlayScene(app, "quick", "hard", first=0, seed=11)
app.goto(play)
run(0.5)
shot("09_game_english")
g = play.game
g.players[0].tower = 3
g.players[0].wall = 0
play.target[0].update(tower=3, wall=0)
g.players[1].hand[0] = "albatross_squadron"
g.players[1].penguins = 40
g.players[0].hand[0] = "hotfix"
g.players[0].code = 0
g.players[0].hand[0] = "code_freeze"
play.human_act("discard", 0)
run(6.0)
shot("10_defeat_english")
app.store.settings["lang"] = "hu"
set_lang("hu")

app.goto(A.SettingsScene(app, A.MenuScene(app)))
run(0.6)
shot("11_settings")
app.goto(A.HelpScene(app, A.MenuScene(app)))
run(0.6)
shot("12_help")
cs = A.CardsScene(app, A.MenuScene(app))
app.goto(cs)
run(0.5, motion((640 - 3 * 166 + 8 + 2 * 166 + 75, 270)))
shot("13_cards")
cs.set_filter("green")
cs.flip(1)
run(0.3, motion((10, 10)))
shot("14_cards_green")
app.goto(A.StatsScene(app, A.MenuScene(app)))
run(0.6)
shot("15_stats")
print("ok")
