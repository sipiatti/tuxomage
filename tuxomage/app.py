"""TuxoMage pygame application: menu, setup, play, results, cards, stats, help, settings."""
from __future__ import annotations

import argparse
import math
import os
import random
import sys

import pygame

from . import __version__, theme
from .ai import AI
from .audio import Audio
from .cards import BY_ID, CATEGORY_ORDER, DECK, NAMES, PRODUCER_OF, STOCKS
from .engine import PRESETS, Game, score as game_score
from .i18n import lang, set_lang, tr
from .render import CARD_H, CARD_W, ZOOM_H, ZOOM_W, card_back, card_surface, draw_tower, draw_wall
from .resources import font, icon_path, image
from .storage import Store
from .ui import (Button, IconButton, Particles, Slider, Snow, card, draw_background, ease_out_back, mix,
                 rainbow_title, text)

W, H = theme.WIDTH, theme.HEIGHT
AI_SPEED = {"slow": 1.6, "normal": 1.0, "fast": 0.55}


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ===================================================================== scenes
class Scene:
    music: str | None = "menu"      # background track for this scene (None = keep current)

    def __init__(self, app: "App"):
        self.app = app
        self.buttons: list[Button] = []
        self.t = 0.0

    def handle(self, event):
        for b in self.buttons:
            if b.handle(event):
                return True
        return False

    def update(self, dt):
        self.t += dt
        for b in self.buttons:
            b.update(dt)
        self.refresh_audio_buttons()

    def draw(self, surf):
        for b in self.buttons:
            b.draw(surf)

    def audio_buttons(self, positions, size=52):
        """Round music / effects / settings (/ help) buttons."""
        app = self.app
        out = [IconButton(positions[0], "icons/music.png", theme.BTN_MINT, app.toggle_music, size, tr("tip_music")),
               IconButton(positions[1], "icons/speaker.png", theme.BTN_BLUE, app.toggle_sfx, size, tr("tip_sfx")),
               IconButton(positions[2], "icons/gear.png", theme.BTN_PURPLE,
                          lambda: app.goto(SettingsScene(app, self)), size, tr("tip_settings"))]
        if len(positions) > 3:
            out.append(IconButton(positions[3], "icons/question.png", theme.BTN_ORANGE,
                                  lambda: app.goto(HelpScene(app, self)), size, tr("tip_help")))
        self.sound_btns = out
        self.buttons += out
        return out

    def refresh_audio_buttons(self):
        btns = getattr(self, "sound_btns", None)
        if not btns:
            return
        a = self.app.audio
        btns[0].icon = "icons/music_off.png" if a.music_muted else "icons/music.png"
        btns[0].colors = theme.BTN_GREY if a.music_muted else theme.BTN_MINT
        btns[1].icon = "icons/speaker_off.png" if a.sfx_muted else "icons/speaker.png"
        btns[1].colors = theme.BTN_GREY if a.sfx_muted else theme.BTN_BLUE

    def on_language(self):
        """Called after a language switch; scenes rebuild their labels."""


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.build()

    def build(self):
        app = self.app
        x, w, h, y = W // 2 - 170, 340, 58, 300
        self.buttons = [
            Button((x, y, w, h), tr("play"), theme.BTN_PINK, action=lambda: app.goto(SetupScene(app))),
            Button((x, y + 70, w, h), tr("howto"), theme.BTN_BLUE, action=lambda: app.goto(HelpScene(app, self))),
            Button((x, y + 140, w, h), tr("cards"), theme.BTN_MINT, icon="icons/cards.png",
                   action=lambda: app.goto(CardsScene(app, self))),
            Button((x, y + 210, w, h), tr("stats"), theme.BTN_YELLOW, icon="icons/star.png",
                   action=lambda: app.goto(StatsScene(app, self))),
            Button((x, y + 280, w, h), tr("quit"), theme.BTN_PURPLE, action=app.quit),
        ]
        self.audio_buttons([(W - 166, 46), (W - 106, 46), (W - 46, 46)])

    def on_language(self):
        self.build()

    def draw(self, surf):
        rainbow_title(surf, "TuxoMage", 118, (W // 2, 130), self.t)
        text(surf, tr("subtitle"), 30, theme.TEXT_SOFT, "bold", center=(W // 2, 222))
        # two duelling penguin wizards with their towers
        for i, (px, img_name, tint) in enumerate(((250, "player", theme.PLAYER_TINT), (W - 250, "ai", theme.AI_TINT))):
            ground = 600
            tx = px - 120 if i == 0 else px + 120
            draw_tower(surf, tx, ground, 170 + 12 * math.sin(self.t * 1.3 + i), tint, self.t,
                       flag=(255, 143, 171) if i == 0 else (178, 145, 255))
            bounce = abs(math.sin(self.t * 2.4 + i * 1.3)) * 18
            mood = "_happy" if int(self.t * 0.8 + i) % 3 == 0 else ""
            img = image(f"penguins/{img_name}{mood}.png", 170)
            if i == 1:
                img = pygame.transform.flip(img, True, False)
            surf.blit(img, img.get_rect(midbottom=(px, ground + 6 - bounce)))
        pygame.draw.ellipse(surf, theme.SNOW, (-80, 590, 520, 90))
        pygame.draw.ellipse(surf, theme.SNOW, (W - 440, 590, 520, 90))
        super().draw(surf)
        st = self.app.store.data["stats"]
        won = sum(s["won"] for s in st.values())
        played = sum(s["played"] for s in st.values())
        if played:
            text(surf, f"{tr('won')}: {won} / {played}", 22, theme.TEXT_SOFT, "medium", center=(W // 2, H - 22))
        text(surf, f"v{__version__}", 18, theme.TEXT_SOFT, "medium", midright=(W - 16, H - 20))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.app.goto(SetupScene(self.app))
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.quit()
            return True
        return super().handle(event)


class SetupScene(Scene):
    """Choose rules preset, opponent difficulty and who starts."""

    def __init__(self, app):
        super().__init__(app)
        self.build()

    def build(self):
        app = self.app
        s = app.store.settings
        self.buttons = []
        self.preset_btns = {}
        for i, key in enumerate(PRESETS):
            b = Button((86 + i * 282, 150, 262, 58), tr(f"preset_{key}"), theme.BTN_BLUE, size=28,
                       action=lambda k=key: self._set("preset", k))
            self.preset_btns[key] = b
        self.diff_btns = {}
        for i, key in enumerate(("easy", "normal", "hard")):
            b = Button((180 + i * 316, 368, 290, 58), tr(key), theme.BTN_MINT, size=28,
                       action=lambda k=key: self._set("difficulty", k))
            self.diff_btns[key] = b
        self.first_btns = {}
        for i, key in enumerate(("player", "ai", "random")):
            label = tr({"player": "first_player_v", "ai": "first_ai", "random": "first_random"}[key])
            b = Button((300 + i * 236, 520, 210, 52), label, theme.BTN_ORANGE, size=26,
                       action=lambda k=key: self._set("first", k))
            self.first_btns[key] = b
        self.buttons += list(self.preset_btns.values()) + list(self.diff_btns.values()) + list(self.first_btns.values())
        self.buttons += [Button((W // 2 + 20, H - 90, 260, 64), tr("start"), theme.BTN_PINK, size=32,
                                action=self.start),
                         Button((W // 2 - 280, H - 90, 260, 64), tr("back"), theme.BTN_PURPLE, size=30,
                                action=lambda: app.goto(MenuScene(app)))]
        self.audio_buttons([(W - 166, 46), (W - 106, 46), (W - 46, 46)])
        self.refresh()

    def on_language(self):
        self.build()

    def _set(self, k, v):
        self.app.store.settings[k] = v
        self.app.store.save()
        self.refresh()

    def refresh(self):
        s = self.app.store.settings
        for key, b in self.preset_btns.items():
            b.colors = theme.BTN_BLUE if s["preset"] == key else theme.BTN_GREY
        for key, b in self.diff_btns.items():
            b.colors = {"easy": theme.BTN_MINT, "normal": theme.BTN_YELLOW, "hard": theme.BTN_PINK}[key] \
                if s["difficulty"] == key else theme.BTN_GREY
        for key, b in self.first_btns.items():
            b.colors = theme.BTN_ORANGE if s["first"] == key else theme.BTN_GREY

    def start(self):
        s = self.app.store.settings
        first = {"player": 0, "ai": 1}.get(s["first"], random.randint(0, 1))
        self.app.goto(PlayScene(self.app, s["preset"], s["difficulty"], first))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.start()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.goto(MenuScene(self.app))
            return True
        return super().handle(event)

    def draw(self, surf):
        rainbow_title(surf, tr("setup_title"), 60, (W // 2, 54), self.t, wave=3)
        s = self.app.store.settings
        card(surf, (60, 104, W - 120, 196), radius=26)
        text(surf, tr("rules_preset"), 30, theme.TEXT, "black", midleft=(90, 128))
        for key, b in self.preset_btns.items():
            p = PRESETS[key]
            col = theme.TEXT if s["preset"] == key else theme.TEXT_SOFT
            cx = b.rect.centerx
            text(surf, tr("preset_line1", t=p.tower, w=p.wall), 19, col, "medium", center=(cx, 232))
            text(surf, tr("preset_line2", p=p.producer, s=p.stock), 19, col, "medium", center=(cx, 254))
            text(surf, tr("preset_line3", wt=p.win_tower, wr=p.win_resource), 19, col, "bold", center=(cx, 278))
        card(surf, (60, 318, W - 120, 150), radius=26)
        text(surf, tr("difficulty"), 30, theme.TEXT, "black", midleft=(90, 342))
        for key, b in self.diff_btns.items():
            col = theme.TEXT if s["difficulty"] == key else theme.TEXT_SOFT
            text(surf, tr(f"{key}_d"), 19, col, "medium", center=(b.rect.centerx, 448))
        card(surf, (60, 484, W - 120, 104), radius=26)
        text(surf, tr("first_player"), 30, theme.TEXT, "black", midleft=(90, 546))
        img = image("penguins/player_happy.png", 120)
        surf.blit(img, img.get_rect(bottomleft=(60, H - 10)))
        img = pygame.transform.flip(image("penguins/ai.png", 120), True, False)
        surf.blit(img, img.get_rect(bottomright=(W - 60, H - 10)))
        super().draw(surf)


# ======================================================================= play
FIELD = pygame.Rect(212, 58, 856, 414)
GROUND = FIELD.bottom - 38
PANEL_W = 190
PANEL_X = {0: 12, 1: W - 12 - PANEL_W}
TOWER_X = {0: FIELD.x + 74, 1: FIELD.right - 74}
WALL_X = {0: FIELD.x + 160, 1: FIELD.right - 160}
MASCOT_X = {0: FIELD.x + 232, 1: FIELD.right - 232}
CENTER = pygame.Rect(0, 0, 170, 238)
CENTER.midtop = (FIELD.centerx, FIELD.y + 10)
LOG_RECT = pygame.Rect(FIELD.centerx - 150, CENTER.bottom + 8, 300, 116)
HAND_Y = 494
BIN = pygame.Rect(W - 136, 536, 120, 132)
DECK_POS = (76, 600)
ROW_ATTRS = [("compiler", "code"), ("kernel", "bytes"), ("colony", "penguins")]


class HandCard:
    def __init__(self, cid, pos):
        self.cid = cid
        self.x, self.y = pos
        self.lift = 0.0
        self.shake = 0.0


class Floater:
    def __init__(self, msg, color, x, y):
        self.msg, self.color, self.x, self.y, self.age = msg, color, x, y, 0.0


class PlayScene(Scene):
    music = "game"

    def __init__(self, app, preset: str = "classic", difficulty: str = "normal", first: int = 0,
                 seed: int | None = None):
        super().__init__(app)
        self.preset_key = preset
        self.difficulty = difficulty
        self.first = first
        self.game = Game(preset, seed=seed, first=first)
        self.ai = AI(difficulty, seed=None if seed is None else seed + 1)
        self.speed = AI_SPEED.get(app.store.settings.get("ai_speed", "normal"), 1.0)
        self.view = [dict(p.stats()) for p in self.game.players]
        self.target = [dict(p.stats()) for p in self.game.players]
        self.flash = [{}, {}]                 # attr -> remaining highlight time
        self.shake = [0.0, 0.0]               # tower shake
        self.mood = [("", 0.0), ("", 0.0)]    # (mood suffix, until t)
        self.hand_ui = [HandCard(c, self._slot_pos(i, len(self.game.players[0].hand)))
                        for i, c in enumerate(self.game.players[0].hand)]
        self.queue: list[list] = []           # [duration, start_fn, update_fn|None, started]
        self.anim = None                      # current card flight
        self.center_card: str | None = None
        self.center_discarded = False
        self.center_by = 0
        self.center_pop = 0.0
        self.log: list[tuple] = []            # (player, cid, kind)
        self.floaters: list[Floater] = []
        self.particles = Particles()
        self.toast = ("", 0.0)
        self.hover = None
        self.press = None
        self.drag = None
        self.drag_pos = (0, 0)
        self.discard_mode = False
        self.overlay = None
        self.finished = False
        self.mouse = (-100, -100)
        self.vis_current = first              # whose turn the screen shows (lags the engine during animations)
        self.build_buttons()
        # the opening turn: production for the first player already happened in Game()
        self._after_action(None)

    # ---------------------------------------------------------------- layout
    def build_buttons(self):
        app = self.app
        self.buttons = [IconButton((36, 28), "icons/home.png", theme.BTN_PINK, self.pause, 44, tr("tip_menu")),
                        IconButton((86, 28), "icons/question.png", theme.BTN_ORANGE,
                                   lambda: app.goto(HelpScene(app, self)), 44, tr("tip_help"))]
        self.audio_buttons([(W - 136, 28), (W - 86, 28), (W - 36, 28)], size=44)

    def on_language(self):
        self.build_buttons()

    @staticmethod
    def _slot_pos(i, n):
        left, right = 152, BIN.x - 10
        avail = right - left
        total = n * CARD_W + (n - 1) * 14
        if total <= avail:
            return (left + (avail - total) // 2 + i * (CARD_W + 14), HAND_Y)
        step = (avail - CARD_W) / max(1, n - 1)
        return (left + int(i * step), HAND_Y)

    def slot_rect(self, i):
        hc = self.hand_ui[i]
        return pygame.Rect(int(hc.x), int(hc.y - hc.lift), CARD_W, CARD_H)

    # ----------------------------------------------------------------- state
    @property
    def human_turn(self) -> bool:
        return (not self.game.over and self.game.current == 0 and not self.queue and self.anim is None
                and self.overlay is None)

    def px_per_unit(self):
        top_tower = max(self.game.preset.win_tower, max(v["tower"] for v in self.view))
        return (GROUND - FIELD.y - 112) / top_tower

    # ------------------------------------------------------------- actions
    def human_act(self, kind, i):
        g = self.game
        if not self.human_turn:
            return
        if not (0 <= i < len(g.players[0].hand)):
            return
        c = BY_ID[g.players[0].hand[i]]
        if g.phase == "discard":
            kind = "discard"
        if kind == "play" and not g.can_play(i):
            need = c.cost - g.players[0].get(c.resource)
            self.say(tr("need_more", n=need, res=NAMES[lang()][c.resource]))
            self.hand_ui[i].shake = 0.4
            self.app.audio.play("denied")
            return
        if kind == "discard" and not g.can_discard(i):
            self.say(tr("cant_discard"))
            self.hand_ui[i].shake = 0.4
            self.app.audio.play("denied")
            return
        src = self.slot_rect(i)
        self.discard_mode = False
        self._perform((kind, i), src)

    def _perform(self, action, src_rect):
        g = self.game
        who = g.current
        kind, i = action
        cid = g.players[who].hand[i]
        self.vis_current = who
        ev = g.act(action)
        snap_after = [None, None]
        snap_after[ev.player] = ev.after[0]
        snap_after[1 - ev.player] = ev.after[1]
        final = [dict(p.stats()) for p in g.players]
        if who == 0:
            self.hand_ui.pop(i)
        self.anim = {"cid": cid, "from": pygame.Rect(src_rect), "t": 0.0,
                     "dur": 0.42 if who == 0 else 0.55 * self.speed, "kind": kind, "who": who}
        self.app.audio.play("play" if kind == "play" else "discard")
        hold = 0.0 if who == 0 else 0.75 * self.speed
        self.queue.append([hold, None, None, False])
        self.queue.append([0.0, lambda: self._apply(snap_after, ev, kind), None, False])
        self.queue.append([0.45, None, None, False])
        if ev.production:
            self.queue.append([0.0, lambda: self._production(final, ev.production), None, False])
            self.queue.append([0.35, None, None, False])
        self.queue.append([0.0, lambda: self._after_action(ev), None, False])

    def _land(self):
        a = self.anim
        self.center_card = a["cid"]
        self.center_discarded = a["kind"] == "discard"
        self.center_by = a["who"]
        self.center_pop = self.t
        self.log.append((a["who"], a["cid"], a["kind"]))
        del self.log[:-5]
        self.anim = None

    def _apply(self, after, ev, kind):
        for k in (0, 1):
            before = self.target[k]
            new = after[k]
            for attr, val in new.items():
                d = val - before[attr]
                if d:
                    self._float(k, attr, d)
            self.target[k] = dict(new)
        if kind == "play":
            self._effect_feedback(ev)
        self._sync_hand()

    def _effect_feedback(self, ev):
        a = self.app.audio
        actor = ev.player
        before = {actor: ev.before[0], 1 - actor: ev.before[1]}
        after = {actor: ev.after[0], 1 - actor: ev.after[1]}
        damaged = built = towered = False
        for k in (0, 1):
            dt_ = after[k]["tower"] - before[k]["tower"]
            dw = after[k]["wall"] - before[k]["wall"]
            if dt_ < 0 or dw < 0:
                damaged = True
                self.shake[k] = 0.45
                cx = TOWER_X[k] if dt_ < 0 else WALL_X[k]
                self.particles.sparkle(cx, GROUND - 60, 18, (150, 200, 255))
                self.mood[k] = ("_sad", self.t + 1.6)
                self.mood[1 - k] = ("_happy", self.t + 1.6)
            if dw > 0:
                built = True
                self.particles.sparkle(WALL_X[k], GROUND - 40, 10, (255, 170, 90))
            if dt_ > 0:
                towered = True
                self.particles.sparkle(TOWER_X[k], GROUND - 120, 16, theme.HINT_GLOW)
                self.mood[k] = ("_happy", self.t + 1.4)
        if damaged:
            a.play("damage")
        if towered:
            a.play("tower")
        if built:
            a.play("build")
        if not (damaged or towered or built):
            a.play("resource")

    def _production(self, final, prod):
        who, gains = prod
        for (prod_attr, stock), g in zip(ROW_ATTRS, gains):
            if g:
                self._float(who, stock, g)
        self.target = [dict(final[0]), dict(final[1])]
        self.app.audio.play("resource", 0.6)

    def _after_action(self, ev):
        g = self.game
        self.vis_current = g.current
        self._sync_hand()
        if g.over:
            self.queue.append([0.7, self._finish, None, False])
            return
        if g.current == 1:
            if g.phase == "discard":
                self.say(tr("ai_discards"), 1.2 * self.speed)
            elif ev is not None and ev.player == 1 and ev.again:
                self.say(tr("ai_again"), 1.2 * self.speed)
            self.queue.append([0.75 * self.speed, None, None, False])
            self.queue.append([0.0, self._ai_move, None, False])
        else:
            if g.phase == "discard":
                self.say(tr("must_discard"), 2.5)
            elif ev is not None and ev.player == 0 and ev.again:
                self.say(tr("play_again"), 1.6)
            else:
                self.toast = ("", 0.0)
                self.app.audio.play("turn", 0.7)

    def _ai_move(self):
        g = self.game
        if g.over or g.current != 1:
            return
        action = self.ai.choose(g)
        src = pygame.Rect(0, 0, 60, 84)
        src.center = (PANEL_X[1] + PANEL_W // 2, FIELD.y + 30)
        self._perform(action, src)

    def _finish(self):
        if self.finished:
            return
        self.finished = True
        self.app.game_finished(self)

    def _sync_hand(self):
        hand = self.game.players[0].hand
        if [h.cid for h in self.hand_ui] != hand[:len(self.hand_ui)]:
            self.hand_ui = [HandCard(c, self._slot_pos(i, len(hand))) for i, c in enumerate(hand)]
            return
        drew = False
        while len(self.hand_ui) < len(hand):
            self.hand_ui.append(HandCard(hand[len(self.hand_ui)], (DECK_POS[0] - CARD_W // 2, DECK_POS[1] - 60)))
            drew = True
        if drew:
            self.app.audio.play("draw", 0.8)

    def _float(self, k, attr, d):
        color = theme.GOOD if d > 0 else theme.WRONG
        msg = f"+{d}" if d > 0 else f"\u2212{-d}"
        if attr in ("tower", "wall"):
            x = TOWER_X[k] if attr == "tower" else WALL_X[k]
            y = GROUND - self.target[k][attr] * self.px_per_unit() - (90 if attr == "tower" else 30)
            y = max(FIELD.y + 30, y)
        else:
            row = next(i for i, pair in enumerate(ROW_ATTRS) if attr in pair)
            x = PANEL_X[k] + 118
            y = FIELD.y + 72 + row * 110 + (74 if attr in STOCKS else 23)
        self.floaters.append(Floater(msg, color, x, y))
        self.flash[k][attr] = 0.8

    def say(self, msg, dur=1.6):
        self.toast = (msg, self.t + dur)

    def pause(self):
        if self.overlay is None and not self.finished:
            self.overlay = PauseOverlay(self.app, self)

    # ----------------------------------------------------------------- input
    def card_at(self, pos):
        for i in reversed(range(len(self.hand_ui))):
            if self.slot_rect(i).collidepoint(pos):
                return i
        return None

    def handle(self, event):
        if hasattr(event, "pos") and event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.mouse = event.pos
        if self.overlay:
            return self.overlay.handle(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause()
                return True
            if pygame.K_1 <= event.key <= pygame.K_7:
                i = event.key - pygame.K_1
                kind = "discard" if event.mod & pygame.KMOD_SHIFT else "play"
                self.human_act(kind, i)
                return True
            if event.key == pygame.K_d:
                self.discard_mode = not self.discard_mode
                return True
        if super().handle(event):
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            i = self.card_at(event.pos)
            if i is not None:
                self.human_act("discard", i)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if BIN.collidepoint(event.pos) and self.human_turn:
                self.discard_mode = not self.discard_mode
                self.app.audio.play("click")
                return True
            i = self.card_at(event.pos)
            if i is not None and self.human_turn:
                self.press = (i, event.pos)
            return True
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.card_at(event.pos)
            if self.press and self.drag is None:
                i, p0 = self.press
                if abs(event.pos[0] - p0[0]) + abs(event.pos[1] - p0[1]) > 14:
                    self.drag = i
            if self.drag is not None:
                self.drag_pos = event.pos
            return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            press, drag = self.press, self.drag
            self.press = self.drag = None
            if drag is not None:
                if BIN.collidepoint(event.pos):
                    self.human_act("discard", drag)
                elif event.pos[1] < HAND_Y - 20:
                    self.human_act("discard" if self.discard_mode else "play", drag)
                return True
            if press is not None and self.card_at(event.pos) == press[0]:
                self.human_act("discard" if self.discard_mode else "play", press[0])
                return True
        return False

    # ---------------------------------------------------------------- update
    def update(self, dt):
        super().update(dt)
        if self.overlay:
            self.overlay.update(dt)
        # tweens
        for k in (0, 1):
            for attr, val in self.target[k].items():
                cur = self.view[k][attr]
                self.view[k][attr] = cur + (val - cur) * min(1.0, dt * 7) if abs(val - cur) > 0.02 else val
            for attr in list(self.flash[k]):
                self.flash[k][attr] -= dt
                if self.flash[k][attr] <= 0:
                    del self.flash[k][attr]
            self.shake[k] = max(0.0, self.shake[k] - dt)
        n = len(self.hand_ui)
        mouse = self.mouse
        for i, hc in enumerate(self.hand_ui):
            tx, ty = self._slot_pos(i, n)
            hc.x += (tx - hc.x) * min(1.0, dt * 12)
            hc.y += (ty - hc.y) * min(1.0, dt * 12)
            want = 16.0 if (i == self.hover and self.drag is None and self.human_turn) else 0.0
            hc.lift += (want - hc.lift) * min(1.0, dt * 14)
            hc.shake = max(0.0, hc.shake - dt)
        self.hover = self.card_at(mouse) if self.drag is None else None
        for f in self.floaters:
            f.age += dt
            f.y -= 26 * dt
        self.floaters = [f for f in self.floaters if f.age < 1.4]
        self.particles.update(dt)
        # card flight
        if self.anim:
            self.anim["t"] += dt
            if self.anim["t"] >= self.anim["dur"]:
                self._land()
            return
        # sequential queue
        while self.queue:
            step = self.queue[0]
            if not step[3]:
                step[3] = True
                if step[1]:
                    step[1]()
                if self.anim:          # a new flight started (AI move) – wait for it
                    self.queue.pop(0)
                    return
            step[0] -= dt
            if step[0] > 0:
                break
            dt = -step[0]
            self.queue.pop(0)
            if self.anim:
                break

    # ------------------------------------------------------------------ draw
    def draw(self, surf):
        g = self.game
        self.draw_field(surf)
        for k in (0, 1):
            self.draw_panel(surf, k)
        self.draw_center(surf)
        self.draw_topbar(surf)
        self.draw_hand(surf)
        self.particles.draw(surf)
        for f in self.floaters:
            a = 1 - f.age / 1.4
            img = font(30, "black").render(f.msg, True, f.color)
            img.set_alpha(int(255 * min(1.0, a * 2)))
            o = font(30, "black").render(f.msg, True, theme.WHITE)
            o.set_alpha(int(255 * min(1.0, a * 2)))
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                surf.blit(o, o.get_rect(center=(f.x + dx, f.y + dy)))
            surf.blit(img, img.get_rect(center=(f.x, f.y)))
        if self.anim:
            self.draw_flight(surf)
        self.draw_toast(surf)
        Scene.draw(self, surf)
        self.draw_zoom(surf)
        if self.drag is not None and self.drag < len(self.hand_ui):
            img = card_surface(self.hand_ui[self.drag].cid, CARD_W, CARD_H, lang(), False)
            surf.blit(img, img.get_rect(center=self.drag_pos))
        if self.overlay:
            self.overlay.draw(surf)

    def draw_field(self, surf):
        sky = pygame.Surface(FIELD.size, pygame.SRCALPHA)
        for y in range(FIELD.h):
            pygame.draw.line(sky, (*mix(theme.SKY_TOP, theme.SKY_BOTTOM, y / FIELD.h), 255), (0, y), (FIELD.w, y))
        mask = pygame.Surface(FIELD.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=26)
        sky.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(sky, FIELD.topleft)
        # distant ice hills + sun
        pygame.draw.circle(surf, (255, 236, 170), (FIELD.centerx, FIELD.y + 300), 44)
        for i, (cx, r) in enumerate(((FIELD.x + 260, 120), (FIELD.centerx, 150), (FIELD.right - 260, 120))):
            pygame.draw.circle(surf, mix(theme.SNOW_SHADE, theme.WHITE, 0.3 * i % 1), (cx, GROUND + 40), r)
        g = self.game
        ppu = self.px_per_unit()
        for k in (0, 1):
            v = self.view[k]
            tint = theme.PLAYER_TINT if k == 0 else theme.AI_TINT
            flag = (255, 143, 171) if k == 0 else (178, 145, 255)
            draw_wall(surf, WALL_X[k], GROUND, min(v["wall"] * ppu, GROUND - FIELD.y - 40), self.t, self.shake[k])
            draw_tower(surf, TOWER_X[k], GROUND, v["tower"] * ppu, tint, self.t, flag, self.shake[k])
            # goal line marker
        gy = GROUND - g.preset.win_tower * ppu
        for x in range(FIELD.x + 20, FIELD.right - 20, 18):
            pygame.draw.line(surf, (255, 200, 120), (x, gy), (x + 9, gy), 2)
        # snow ground
        ground = pygame.Rect(FIELD.x, GROUND, FIELD.w, FIELD.bottom - GROUND)
        pygame.draw.rect(surf, theme.SNOW, ground, border_bottom_left_radius=26, border_bottom_right_radius=26)
        pygame.draw.line(surf, theme.SNOW_SHADE, (FIELD.x + 10, GROUND), (FIELD.right - 10, GROUND), 3)
        pygame.draw.rect(surf, theme.CARD_BORDER, FIELD, 3, border_radius=26)
        # mascots
        for k in (0, 1):
            mood, until = self.mood[k]
            if self.t > until:
                mood = ""
            if g.over:
                mood = "_happy" if g.winner == k else "_sad" if g.winner in (0, 1) else ""
            img = image(f"penguins/{'player' if k == 0 else 'ai'}{mood}.png", 86)
            if k == 1:
                img = pygame.transform.flip(img, True, False)
            hop = abs(math.sin(self.t * 4)) * 6 if mood == "_happy" else 0
            surf.blit(img, img.get_rect(midbottom=(MASCOT_X[k], GROUND + 8 - hop)))
        # value pills
        for k in (0, 1):
            v = self.view[k]
            for attr, x, icon in (("tower", TOWER_X[k], "icons/tower.png"), ("wall", WALL_X[k], "icons/wall.png")):
                pill = pygame.Rect(0, 0, 78, 30)
                pill.center = (x, GROUND + 19)
                col = theme.HINT_GLOW if attr in self.flash[k] else theme.WHITE
                pygame.draw.rect(surf, col, pill, border_radius=15)
                pygame.draw.rect(surf, theme.CARD_BORDER, pill, 2, border_radius=15)
                surf.blit(image(icon, 24), (pill.x + 6, pill.y + 3))
                text(surf, str(round(v[attr])), 22, theme.TEXT, "black", midright=(pill.right - 10, pill.centery + 1))

    def draw_panel(self, surf, k):
        g = self.game
        p = g.players[k]
        x = PANEL_X[k]
        rect = pygame.Rect(x, FIELD.y, PANEL_W, FIELD.h)
        active = self.vis_current == k and not g.over
        border = (255, 143, 171) if (active and k == 0) else (178, 145, 255) if active else theme.CARD_BORDER
        card(surf, rect, radius=22, border=None)
        if active:
            glow = 3 + int(2 * (1 + math.sin(self.t * 5)))
            pygame.draw.rect(surf, border, rect, glow, border_radius=22)
        else:
            pygame.draw.rect(surf, theme.CARD_BORDER, rect, 3, border_radius=22)
        av = image(f"penguins/{'player' if k == 0 else 'ai'}.png", 54)
        surf.blit(av, (x + 8, FIELD.y + 6))
        name = tr("you") if k == 0 else tr("computer")
        text(surf, name, 26, theme.TEXT, "black", midleft=(x + 66, FIELD.y + 26))
        sub = tr(self.difficulty) if k == 1 else tr(f"preset_{self.preset_key}")
        text(surf, sub, 16, theme.TEXT_SOFT, "bold", midleft=(x + 66, FIELD.y + 48))
        v = self.view[k]
        for row, (prod, stock) in enumerate(ROW_ATTRS):
            main, light, dark = theme.RES_COLORS[stock]
            box = pygame.Rect(x + 10, FIELD.y + 72 + row * 110, PANEL_W - 20, 102)
            pygame.draw.rect(surf, light, box, border_radius=16)
            pygame.draw.rect(surf, main, box, 3, border_radius=16)
            # producer line
            fl = prod in self.flash[k]
            surf.blit(image(f"icons/prod_{prod}.png", 30), (box.x + 8, box.y + 8))
            text(surf, NAMES[lang()][prod], 18, dark, "bold", midleft=(box.x + 44, box.y + 23))
            text(surf, f"+{round(v[prod])}", 24, theme.HINT_GLOW if fl else dark, "black",
                 midright=(box.right - 10, box.y + 23), outline=theme.WHITE if not fl else dark, outline_w=1)
            pygame.draw.line(surf, mix(main, theme.WHITE, 0.4), (box.x + 10, box.y + 44), (box.right - 10, box.y + 44), 2)
            surf.blit(image(f"icons/res_{stock}.png", 36), (box.x + 6, box.y + 54))
            text(surf, NAMES[lang()][stock], 18, dark, "bold", midleft=(box.x + 46, box.y + 72))
            fl = stock in self.flash[k]
            text(surf, str(round(v[stock])), 34, theme.HINT_GLOW if fl else theme.TEXT, "black",
                 midright=(box.right - 10, box.y + 74), outline=theme.WHITE if not fl else theme.TEXT, outline_w=1)

    def draw_center(self, surf):
        g = self.game
        # placeholder
        pygame.draw.rect(surf, (255, 255, 255), CENTER, border_radius=16)
        pygame.draw.rect(surf, theme.CARD_BORDER, CENTER, 3, border_radius=16)
        if self.center_card:
            pop = ease_out_back(min(1.0, (self.t - self.center_pop) / 0.35))
            w, h = int(CENTER.w * (0.85 + 0.15 * pop)), int(CENTER.h * (0.85 + 0.15 * pop))
            img = card_surface(self.center_card, CENTER.w, CENTER.h, lang(), False)
            if (w, h) != img.get_size():
                img = pygame.transform.smoothscale(img, (w, h))
            surf.blit(img, img.get_rect(center=CENTER.center))
            if self.center_discarded:
                stamp = font(30, "black").render(tr("discarded"), True, theme.WRONG)
                stamp = pygame.transform.rotate(stamp, 18)
                surf.blit(stamp, stamp.get_rect(center=CENTER.center))
            tag = tr("you") if self.center_by == 0 else tr("computer")
            col = (255, 143, 171) if self.center_by == 0 else (178, 145, 255)
            pill = pygame.Rect(0, 0, 90, 24)
            pill.midtop = (CENTER.centerx, CENTER.bottom - 12)
            pygame.draw.rect(surf, col, pill, border_radius=12)
            text(surf, tag, 17, theme.WHITE, "black", center=(pill.centerx, pill.centery + 1))
        else:
            text(surf, tr("last_played"), 18, theme.TEXT_SOFT, "bold", center=CENTER.center)
        # log
        r = LOG_RECT
        y = r.y + 6
        for who, cid, kind in reversed(self.log[-4:]):
            c = BY_ID[cid]
            col = theme.CAT_COLORS[c.cat][0]
            pygame.draw.circle(surf, col, (r.x + 12, y + 12), 7)
            whom = tr("you") if who == 0 else tr("computer")
            msg = tr("log_play" if kind == "play" else "log_discard", who=whom, card=c.name(lang()))
            text(surf, msg, 18, theme.TEXT if kind == "play" else theme.TEXT_SOFT, "bold" if kind == "play" else "medium",
                 midleft=(r.x + 26, y + 13))
            y += 26

    def draw_topbar(self, surf):
        g = self.game
        if g.over:
            msg, col = (tr("victory") if g.winner == 0 else tr("defeat") if g.winner == 1 else tr("draw")), theme.BTN_YELLOW
        elif self.vis_current == 0:
            msg = tr("must_discard") if g.phase == "discard" else tr("your_turn")
            col = theme.BTN_PINK
        else:
            msg, col = tr("ai_turn"), theme.BTN_PURPLE
        pill = pygame.Rect(0, 0, 320, 40)
        pill.center = (W // 2, 29)
        pygame.draw.rect(surf, col[1], pill.move(0, 4), border_radius=20)
        pygame.draw.rect(surf, col[0], pill, border_radius=20)
        text(surf, msg, 24, theme.WHITE, "black", center=(pill.centerx, pill.centery + 1), outline=col[1], outline_w=2)
        text(surf, tr("turn_n", n=(g.turn + 1) // 2), 20, theme.TEXT_SOFT, "bold", midright=(pill.left - 16, 30))
        text(surf, tr("goal", t=g.preset.win_tower, r=g.preset.win_resource), 20, theme.TEXT_SOFT, "bold",
             midleft=(pill.right + 16, 30))

    def draw_hand(self, surf):
        g = self.game
        # deck pile
        for i in range(3):
            back = card_back(110, 154)
            surf.blit(back, back.get_rect(center=(DECK_POS[0] - i * 3, DECK_POS[1] - i * 3)))
        mine = self.vis_current == 0 and not g.over
        for i, hc in enumerate(self.hand_ui):
            if i == self.drag:
                continue
            c = BY_ID[hc.cid]
            playable = g.players[0].can_afford(c) and g.phase == "play"
            dim = not playable or not mine
            img = card_surface(hc.cid, CARD_W, CARD_H, lang(), dim)
            r = self.slot_rect(i)
            if hc.shake:
                r.x += int(math.sin(hc.shake * 60) * 6)
            sh = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            pygame.draw.rect(sh, (*theme.SHADOW, 110), sh.get_rect(), border_radius=14)
            surf.blit(sh, r.move(0, 6))
            surf.blit(img, r)
            if mine and (self.discard_mode or g.phase == "discard") and not c.undiscardable:
                pygame.draw.rect(surf, theme.WRONG, r.inflate(6, 6), 3, border_radius=16)
            elif i == self.hover and mine and playable:
                pygame.draw.rect(surf, theme.HINT_GLOW, r.inflate(6, 6), 4, border_radius=16)
        # discard bin
        on = self.discard_mode or g.phase == "discard" and mine
        hovering = BIN.collidepoint(self.mouse) or (self.drag is not None and BIN.collidepoint(self.drag_pos))
        face = theme.BTN_PINK if on else theme.BTN_ORANGE if hovering else theme.BTN_GREY
        pygame.draw.rect(surf, face[1], BIN.move(0, 5), border_radius=22)
        pygame.draw.rect(surf, face[0], BIN, border_radius=22)
        surf.blit(image("icons/trash.png", 70), image("icons/trash.png", 70).get_rect(center=(BIN.centerx, BIN.y + 50)))
        text(surf, tr("discard"), 22, theme.WHITE, "black", center=(BIN.centerx, BIN.bottom - 24), outline=face[1])

    def draw_flight(self, surf):
        a = self.anim
        t = ease_out(a["t"] / a["dur"])
        src = a["from"]
        w = int(src.w + (CENTER.w - src.w) * t)
        h = int(src.h + (CENTER.h - src.h) * t)
        cx = src.centerx + (CENTER.centerx - src.centerx) * t
        cy = src.centery + (CENTER.centery - src.centery) * t - math.sin(t * math.pi) * 60
        if a["who"] == 1 and t < 0.5:
            # the AI's card flips over on its way in
            flip = 1 - t * 2
            img = card_back(CENTER.w, CENTER.h)
            img = pygame.transform.smoothscale(img, (max(2, int(w * flip)), h))
        else:
            flip = (t - 0.5) * 2 if a["who"] == 1 else 1.0
            img = card_surface(a["cid"], CENTER.w, CENTER.h, lang(), False)
            img = pygame.transform.smoothscale(img, (max(2, int(w * flip)), h))
        surf.blit(img, img.get_rect(center=(cx, cy)))

    def draw_toast(self, surf):
        msg, until = self.toast
        if not msg or self.t > until or self.game.over:
            return
        a = min(1.0, (until - self.t) * 3)
        f = font(26, "black")
        img = f.render(msg, True, theme.TEXT)
        box = img.get_rect(center=(FIELD.centerx, HAND_Y - 10)).inflate(36, 14)
        s = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, int(230 * a)), s.get_rect(), border_radius=box.h // 2)
        pygame.draw.rect(s, (*theme.CARD_BORDER, int(255 * a)), s.get_rect(), 3, border_radius=box.h // 2)
        surf.blit(s, box)
        img.set_alpha(int(255 * a))
        surf.blit(img, img.get_rect(center=box.center))

    def draw_zoom(self, surf):
        if self.overlay or self.drag is not None:
            return
        mouse = self.mouse
        cid = None
        if self.hover is not None and self.hover < len(self.hand_ui):
            cid = self.hand_ui[self.hover].cid
            r = self.slot_rect(self.hover)
            zr = pygame.Rect(0, 0, ZOOM_W, ZOOM_H)
            zr.midbottom = (r.centerx, r.top - 8)
        elif self.center_card and CENTER.collidepoint(mouse) and not self.anim:
            cid = self.center_card
            zr = pygame.Rect(0, 0, ZOOM_W, ZOOM_H)
            zr.midleft = (CENTER.right + 16, CENTER.centery + 40)
        if cid is None:
            return
        zr.clamp_ip(pygame.Rect(0, 0, W, H))
        g = self.game
        c = BY_ID[cid]
        sh = pygame.Surface(zr.size, pygame.SRCALPHA)
        pygame.draw.rect(sh, (*theme.SHADOW, 130), sh.get_rect(), border_radius=22)
        surf.blit(sh, zr.move(0, 8))
        surf.blit(card_surface(cid, ZOOM_W, ZOOM_H, lang(), False), zr)
        if cid != self.center_card or self.hover is not None:
            have = g.players[0].get(c.resource)
            if have < c.cost:
                tip = tr("need_more", n=c.cost - have, res=NAMES[lang()][c.resource])
                pill = pygame.Rect(0, 0, ZOOM_W - 20, 30)
                pill.midtop = (zr.centerx, zr.bottom + 4)
                pill.clamp_ip(pygame.Rect(0, 0, W, H))
                pygame.draw.rect(surf, theme.WRONG, pill, border_radius=15)
                text(surf, tip, 18, theme.WHITE, "black", center=(pill.centerx, pill.centery + 1))


# =================================================================== overlays
class Overlay:
    def __init__(self, app, play: PlayScene):
        self.app = app
        self.play = play
        self.buttons: list[Button] = []
        self.t = 0.0

    def handle(self, event):
        for b in self.buttons:
            if b.handle(event):
                return True
        return True

    def update(self, dt):
        self.t += dt
        for b in self.buttons:
            b.update(dt)

    def veil(self, surf, alpha=150):
        v = pygame.Surface((W, H), pygame.SRCALPHA)
        v.fill((70, 50, 110, alpha))
        surf.blit(v, (0, 0))


class PauseOverlay(Overlay):
    def __init__(self, app, play):
        super().__init__(app, play)
        x = W // 2 - 160
        self.buttons = [
            Button((x, 250, 320, 60), tr("continue"), theme.BTN_MINT, action=self.close),
            Button((x, 324, 320, 60), tr("settings"), theme.BTN_PURPLE, icon="icons/gear.png",
                   action=lambda: app.goto(SettingsScene(app, play))),
            Button((x, 398, 320, 60), tr("howto"), theme.BTN_BLUE, action=lambda: app.goto(HelpScene(app, play))),
            Button((x, 472, 320, 60), tr("give_up"), theme.BTN_PINK, action=self.give_up),
        ]

    def close(self):
        self.play.overlay = None

    def give_up(self):
        self.play.overlay = None
        self.app.give_up(self.play)

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        return super().handle(event)

    def draw(self, surf):
        self.veil(surf)
        card(surf, (W // 2 - 220, 150, 440, 420), radius=30)
        rainbow_title(surf, tr("menu"), 54, (W // 2, 200), self.t, wave=3)
        for b in self.buttons:
            b.draw(surf)


class ResultOverlay(Overlay):
    def __init__(self, app, play, result: str, points: int, record: bool):
        super().__init__(app, play)
        self.result = result
        self.points = points
        self.record = record
        self.particles = Particles()
        if result == "won":
            for i in range(3):
                self.particles.confetti(W // 2 + (i - 1) * 260, 260, 70)
        x = W // 2
        self.buttons = [Button((x - 290, 520, 270, 62), tr("rematch"), theme.BTN_PINK, action=app.rematch),
                        Button((x + 20, 520, 270, 62), tr("menu"), theme.BTN_PURPLE,
                               action=lambda: app.goto(MenuScene(app)))]

    def update(self, dt):
        super().update(dt)
        self.particles.update(dt)
        if self.result == "won" and random.random() < dt * 30:
            self.particles.rain(random.uniform(0, W))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.app.rematch()
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.goto(MenuScene(self.app))
            return True
        return super().handle(event)

    def draw(self, surf):
        self.veil(surf, 120)
        pop = ease_out_back(min(1.0, self.t / 0.5))
        panel = pygame.Rect(0, 0, int(640 * (0.8 + 0.2 * pop)), int(460 * (0.8 + 0.2 * pop)))
        panel.center = (W // 2, 370)
        card(surf, panel, radius=34)
        g = self.play.game
        title = tr("victory") if self.result == "won" else tr("defeat") if self.result == "lost" else tr("draw")
        rainbow_title(surf, title, 76, (W // 2, panel.y + 66), self.t, wave=4)
        reason = tr("reason_draw") if g.reason == "draw" else tr(f"reason_{g.reason}_{g.winner}")
        text(surf, reason, 24, theme.TEXT, "bold", center=(W // 2, panel.y + 136))
        text(surf, tr("turns_taken", n=(g.turn + 1) // 2) + " · " + tr(self.play.difficulty), 22, theme.TEXT_SOFT,
             "medium", center=(W // 2, panel.y + 172))
        if self.result == "won":
            text(surf, tr("score", n=self.points), 40, (255, 140, 60), "black", center=(W // 2, panel.y + 230),
                 outline=theme.WHITE, outline_w=3)
            if self.record:
                text(surf, tr("new_record"), 22, theme.GOOD, "black", center=(W // 2, panel.y + 272))
        for k, x in ((0, panel.x + 40), (1, panel.right - 40)):
            won = g.winner == k
            mood = "_happy" if won else "_sad" if g.winner in (0, 1) else ""
            img = image(f"penguins/{'player' if k == 0 else 'ai'}{mood}.png", 130)
            if k == 1:
                img = pygame.transform.flip(img, True, False)
            bounce = abs(math.sin(self.t * 4 + k)) * 14 if won else 0
            r = img.get_rect(midbottom=(x + (50 if k == 0 else -50), panel.y + 396 - bounce))
            surf.blit(img, r)
        for b in self.buttons:
            b.draw(surf)
        self.particles.draw(surf)


# ===================================================================== others
class StatsScene(Scene):
    def __init__(self, app, back=None):
        super().__init__(app)
        self.back = back
        self.buttons = [Button((W // 2 - 130, H - 86, 260, 62), tr("back"), theme.BTN_PINK, action=self.leave)]

    def leave(self):
        self.app.goto(self.back if isinstance(self.back, Scene) else MenuScene(self.app))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.leave()
            return True
        return super().handle(event)

    def draw(self, surf):
        rainbow_title(surf, tr("stats_title"), 60, (W // 2, 54), self.t, wave=3)
        st = self.app.store.data["stats"]
        card(surf, (60, 104, 560, 506), radius=28)
        cols = [("easy", theme.BTN_MINT), ("normal", theme.BTN_YELLOW), ("hard", theme.BTN_PINK)]
        for j, (d, col) in enumerate(cols):
            cx = 290 + j * 110
            pygame.draw.rect(surf, col[0], (cx - 50, 124, 100, 40), border_radius=20)
            text(surf, tr(d), 20, theme.WHITE, "black", center=(cx, 145), outline=col[1])
        rows = [("played", "played"), ("won", "won"), ("lost", "lost"), ("draw", "draws"),
                ("best_streak", "streak"), ("fastest_win", "fastest")]
        for i, (key, label) in enumerate(rows):
            y = 200 + i * 62
            pygame.draw.line(surf, theme.CARD_BORDER, (84, y + 30), (596, y + 30), 2)
            text(surf, tr(label), 22, theme.TEXT, "bold", midleft=(86, y))
            for j, (d, _c) in enumerate(cols):
                v = st[d].get(key, 0)
                shown = "–" if (key == "fastest_win" and not v) else str(v)
                text(surf, shown, 26, theme.TEXT, "black", center=(290 + j * 110, y))
        card(surf, (650, 104, 570, 506), radius=28)
        text(surf, tr("top_scores"), 30, theme.TEXT, "black", center=(935, 140))
        hs = self.app.store.data.get("highscores", [])
        if not hs:
            text(surf, tr("no_scores"), 22, theme.TEXT_SOFT, "medium", center=(935, 340))
            img = image("penguins/player_happy.png", 120)
            surf.blit(img, img.get_rect(center=(935, 450)))
        for i, e in enumerate(hs[:10]):
            y = 184 + i * 41
            text(surf, f"{i + 1}.", 22, theme.TEXT_SOFT, "black", midright=(704, y))
            text(surf, str(e["score"]), 24, (255, 140, 60), "black", midleft=(716, y))
            text(surf, f"{tr(e['difficulty'])} · {tr('preset_' + e['preset'])} · {tr('turns_taken', n=e['turns'])}", 18,
                 theme.TEXT, "medium", midleft=(810, y))
            text(surf, e.get("date", ""), 16, theme.TEXT_SOFT, "medium", midright=(1196, y))
        super().draw(surf)


class CardsScene(Scene):
    """Browse the whole deck, filtered by category."""
    PER_PAGE = 12

    def __init__(self, app, back=None):
        super().__init__(app)
        self.back = back
        self.filter = None
        self.page = 0
        self.mouse = (-100, -100)
        self.build()

    def build(self):
        self.buttons = [Button((W // 2 - 130, H - 76, 260, 58), tr("back"), theme.BTN_PINK, action=self.leave),
                        IconButton((60, 380), "icons/arrow_left.png", theme.BTN_BLUE, lambda: self.flip(-1), 64),
                        IconButton((W - 60, 380), "icons/arrow_right.png", theme.BTN_BLUE, lambda: self.flip(1), 64)]
        self.filter_btns = []
        labels = [(None, tr("all"), theme.BTN_PURPLE)] + [
            (c, NAMES[lang()][{"red": "code", "blue": "bytes", "green": "penguins"}[c]],
             {"red": theme.BTN_ORANGE, "blue": theme.BTN_BLUE, "green": theme.BTN_MINT}[c]) for c in CATEGORY_ORDER]
        for i, (cat, label, col) in enumerate(labels):
            b = Button((W // 2 - 380 + i * 192, 92, 180, 48), label, col, size=24,
                       action=lambda c=cat: self.set_filter(c))
            b.base = col
            b.cat = cat
            self.filter_btns.append(b)
        self.buttons += self.filter_btns

    def on_language(self):
        self.build()

    @property
    def cards(self):
        lst = [c for c in DECK if self.filter is None or c.cat == self.filter]
        return sorted(lst, key=lambda c: (CATEGORY_ORDER.index(c.cat), c.cost))

    def pages(self):
        return max(1, math.ceil(len(self.cards) / self.PER_PAGE))

    def set_filter(self, cat):
        self.filter = cat
        self.page = 0

    def flip(self, d):
        self.page = (self.page + d) % self.pages()

    def leave(self):
        self.app.goto(self.back if isinstance(self.back, Scene) else MenuScene(self.app))

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.leave()
                return True
            if event.key in (pygame.K_LEFT, pygame.K_PAGEUP):
                self.flip(-1)
                return True
            if event.key in (pygame.K_RIGHT, pygame.K_PAGEDOWN):
                self.flip(1)
                return True
        if event.type == pygame.MOUSEWHEEL:
            self.flip(-1 if event.y > 0 else 1)
            return True
        if event.type == pygame.MOUSEMOTION:
            self.mouse = event.pos
        return super().handle(event)

    def update(self, dt):
        super().update(dt)
        for b in self.filter_btns:
            b.colors = b.base if self.filter == b.cat else theme.BTN_GREY

    def draw(self, surf):
        rainbow_title(surf, tr("cards_title"), 56, (W // 2, 46), self.t, wave=3)
        cards = self.cards
        page = cards[self.page * self.PER_PAGE:(self.page + 1) * self.PER_PAGE]
        cw, ch = 150, 210
        hover = None
        mouse = self.mouse
        for i, c in enumerate(page):
            col, row = i % 6, i // 6
            r = pygame.Rect(W // 2 - 3 * (cw + 16) + 8 + col * (cw + 16), 160 + row * (ch + 14), cw, ch)
            surf.blit(card_surface(c.id, cw, ch, lang(), False), r)
            if r.collidepoint(mouse):
                hover = (c, r)
        text(surf, tr("page", a=self.page + 1, b=self.pages()) + " · " + tr("card_count", n=len(cards)), 20,
             theme.TEXT_SOFT, "bold", center=(W // 2, H - 100))
        super().draw(surf)
        if hover:
            c, r = hover
            zr = pygame.Rect(0, 0, ZOOM_W, ZOOM_H)
            zr.center = r.center
            zr.clamp_ip(pygame.Rect(0, 0, W, H))
            sh = pygame.Surface(zr.size, pygame.SRCALPHA)
            pygame.draw.rect(sh, (*theme.SHADOW, 130), sh.get_rect(), border_radius=22)
            surf.blit(sh, zr.move(0, 8))
            surf.blit(card_surface(c.id, ZOOM_W, ZOOM_H, lang(), False), zr)


class HelpScene(Scene):
    music = None
    KEYS = [("h_goal", "h_goal_t"), ("h_res", "h_res_t"), ("h_turn", "h_turn_t"), ("h_dmg", "h_dmg_t"),
            ("h_special", "h_special_t"), ("h_mouse", "h_mouse_t"), ("h_keys", "h_keys_t")]

    def __init__(self, app, back: Scene | None = None):
        super().__init__(app)
        self.back = back
        self.buttons = [Button((W // 2 - 120, H - 80, 240, 60), tr("ok"), theme.BTN_MINT, action=self.leave)]

    def leave(self):
        self.app.goto(self.back or MenuScene(self.app))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.leave()
            return True
        return super().handle(event)

    def draw(self, surf):
        from .render import wrap
        rainbow_title(surf, tr("help_title"), 60, (W // 2, 50), self.t, wave=3)
        card(surf, (40, 94, W - 80, 528), radius=28)
        y = 112
        colors = theme.TITLE_COLORS
        f = font(20, "medium")
        for i, (head, body) in enumerate(self.KEYS):
            col = colors[i % len(colors)]
            pygame.draw.circle(surf, col, (80, y + 13), 12)
            text(surf, tr(head), 24, col, "black", midleft=(104, y + 13))
            lines = wrap(tr(body), f, W - 330)
            for j, line in enumerate(lines[:2]):
                text(surf, line, 20, theme.TEXT, "medium", midleft=(104, y + 40 + j * 24))
            y += 46 + 24 * min(2, len(lines))
        text(surf, tr("h_credit"), 18, theme.TEXT_SOFT, "bold", center=(W // 2, 604))
        img = image("penguins/player_happy.png", 130)
        surf.blit(img, img.get_rect(bottomright=(W - 56, 590 + math.sin(self.t * 3) * 4)))
        for i, ic in enumerate(("prod_compiler", "prod_kernel", "prod_colony")):
            surf.blit(image(f"icons/{ic}.png", 44), (W - 200 + i * 50, 120))
        super().draw(surf)


class SettingsScene(Scene):
    """Music / effects volume + mute, language, fullscreen and AI speed."""
    music = None

    def __init__(self, app, back: Scene | None = None):
        super().__init__(app)
        self.back = back
        self.build()

    def build(self):
        app = self.app
        a = app.audio
        x0 = 460
        self.music_slider = Slider((x0, 190, 400, 18), a.music_volume, theme.BTN_MINT, self._music_vol)
        self.sfx_slider = Slider((x0, 280, 400, 18), a.sfx_volume, theme.BTN_BLUE, self._sfx_vol)
        self.sliders = [self.music_slider, self.sfx_slider]
        self.music_btn = IconButton((930, 199), "icons/music.png", theme.BTN_MINT, app.toggle_music, 56, "M")
        self.sfx_btn = IconButton((930, 289), "icons/speaker.png", theme.BTN_BLUE, app.toggle_sfx, 56, "S")
        self.lang_btn = Button((x0 - 150, 350, 420, 56), "", theme.BTN_ORANGE, icon="icons/globe.png", size=26,
                               action=self._lang)
        self.fs_btn = Button((x0 - 150, 420, 420, 56), "", theme.BTN_PURPLE, size=26, action=app.toggle_fullscreen)
        self.speed_btn = Button((x0 - 150, 490, 420, 56), "", theme.BTN_BLUE, size=26, action=self._speed)
        self.buttons = [self.music_btn, self.sfx_btn, self.lang_btn, self.fs_btn, self.speed_btn,
                        Button((W // 2 - 120, H - 92, 240, 62), tr("done"), theme.BTN_PINK, action=self.leave)]
        self.sound_btns = []

    def _music_vol(self, v):
        self.app.audio.set_music_volume(v)
        self.app.store.save()

    def _sfx_vol(self, v):
        self.app.audio.set_sfx_volume(v)
        self.app.audio.play("build")
        self.app.store.save()

    def _lang(self):
        s = self.app.store.settings
        s["lang"] = "en" if s.get("lang", "hu") == "hu" else "hu"
        set_lang(s["lang"])
        self.app.store.save()
        self.build()
        if self.back:
            self.back.on_language()

    def _speed(self):
        s = self.app.store.settings
        order = ["slow", "normal", "fast"]
        s["ai_speed"] = order[(order.index(s.get("ai_speed", "normal")) + 1) % 3]
        if isinstance(self.back, PlayScene):
            self.back.speed = AI_SPEED[s["ai_speed"]]
        self.app.store.save()

    def leave(self):
        self.app.store.save()
        self.app.goto(self.back or MenuScene(self.app))

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.leave()
            return True
        for sl in self.sliders:
            if sl.handle(event):
                return True
        return super().handle(event)

    def update(self, dt):
        super().update(dt)
        a, st = self.app.audio, self.app.store.settings
        self.music_slider.value = a.music_volume
        self.sfx_slider.value = a.sfx_volume
        self.music_btn.icon = "icons/music_off.png" if a.music_muted else "icons/music.png"
        self.music_btn.colors = theme.BTN_GREY if a.music_muted else theme.BTN_MINT
        self.sfx_btn.icon = "icons/speaker_off.png" if a.sfx_muted else "icons/speaker.png"
        self.sfx_btn.colors = theme.BTN_GREY if a.sfx_muted else theme.BTN_BLUE
        self.lang_btn.label = tr("language")
        self.fs_btn.label = tr("fullscreen", v=tr("on") if st.get("fullscreen") else tr("off"))
        self.fs_btn.colors = theme.BTN_PURPLE if st.get("fullscreen") else theme.BTN_GREY
        self.speed_btn.label = tr("ai_speed", v=tr("speed_" + st.get("ai_speed", "normal")))

    def draw(self, surf):
        rainbow_title(surf, tr("settings"), 64, (W // 2, 62), self.t, wave=3)
        card(surf, (220, 120, W - 440, 456), radius=30)
        a = self.app.audio
        for label, sl, muted, y in ((tr("music"), self.music_slider, a.music_muted, 199),
                                    (tr("sfx"), self.sfx_slider, a.sfx_muted, 289)):
            text(surf, label, 30, theme.TEXT, "black", midleft=(260, y))
            sl.draw(surf, dim=muted)
            pct = tr("muted") if muted else f"{int(round(sl.value * 100))} %"
            text(surf, pct, 20, theme.TEXT_SOFT, "medium", center=(sl.rect.centerx, y + 32))
        if not a.available:
            text(surf, tr("no_audio"), 20, theme.WRONG, "bold", center=(W // 2, 146))
        super().draw(surf)
        text(surf, tr("keys_settings"), 20, theme.TEXT_SOFT, "medium", center=(W // 2, H - 18))


# ======================================================================= app
class App:
    def __init__(self, headless: bool = False, fullscreen: bool | None = None, audio: bool = True):
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("TuxoMage")
        try:
            pygame.display.set_icon(pygame.image.load(str(icon_path())))
        except pygame.error:
            pass
        self.store = Store()
        set_lang(self.store.settings.get("lang", "hu"))
        self.audio = Audio(self.store.settings, enable=audio)
        Button.on_hover = lambda: self.audio.play("hover")
        Button.on_click = lambda: self.audio.play("click")
        fs = self.store.settings.get("fullscreen", False) if fullscreen is None else fullscreen
        self.screen = self._set_mode(fs)
        self.clock = pygame.time.Clock()
        self.snow = Snow()
        self.scene: Scene = MenuScene(self)
        self.audio.play_music(self.scene.music)
        self.running = True

    def _set_mode(self, fullscreen: bool):
        flags = pygame.SCALED | (pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE)
        try:
            return pygame.display.set_mode((W, H), flags)
        except pygame.error:
            return pygame.display.set_mode((W, H))

    # ------------------------------------------------------------ flow
    def goto(self, scene: Scene):
        self.scene = scene
        if scene.music:
            self.audio.play_music(scene.music)

    def toggle_music(self):
        self.audio.toggle_music()
        self.store.save()

    def toggle_sfx(self):
        self.audio.toggle_sfx()
        self.store.save()

    def game_finished(self, play: PlayScene):
        g = play.game
        result = "won" if g.winner == 0 else "lost" if g.winner == 1 else "draw"
        points = game_score(g, 0, play.difficulty)
        record = self.store.record_game(play.difficulty, result, points, (g.turn + 1) // 2, play.preset_key,
                                        g.reason or "")
        self.audio.duck(3.0)
        self.audio.play("victory" if result == "won" else "defeat" if result == "lost" else "turn")
        play.overlay = ResultOverlay(self, play, result, points, record)

    def give_up(self, play: PlayScene):
        if not play.finished:
            play.finished = True
            self.store.record_game(play.difficulty, "lost", 0, (play.game.turn + 1) // 2, play.preset_key, "give_up")
        self.goto(MenuScene(self))

    def rematch(self):
        sc = self.scene
        s = self.store.settings
        if isinstance(sc, PlayScene):
            first = {"player": 0, "ai": 1}.get(s.get("first"), random.randint(0, 1))
            self.goto(PlayScene(self, sc.preset_key, sc.difficulty, first))
        else:
            self.goto(SetupScene(self))

    def toggle_fullscreen(self):
        s = self.store.settings
        s["fullscreen"] = not s.get("fullscreen", False)
        self.store.save()
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            self.screen = self._set_mode(s["fullscreen"])

    def quit(self):
        self.running = False

    # ------------------------------------------------------------ loop
    def step(self, dt: float, events=()):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.toggle_music()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s and not event.mod & pygame.KMOD_CTRL:
                self.toggle_sfx()
            else:
                self.scene.handle(event)
        self.audio.update(dt)
        self.snow.update(dt)
        self.scene.update(dt)
        draw_background(self.screen, self.snow)
        self.scene.draw(self.screen)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(theme.FPS) / 1000.0, 0.1)
            self.step(dt, pygame.event.get())
            pygame.display.flip()
        self.store.save()
        self.audio.shutdown()
        pygame.quit()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tuxomage", description="TuxoMage – pingvines tornyos kártyajáték")
    parser.add_argument("--fullscreen", action="store_true", help="teljes képernyő / fullscreen")
    parser.add_argument("--mute", action="store_true", help="hang nélkül (nem nyitja meg a hangeszközt) / no audio")
    parser.add_argument("--lang", choices=("hu", "en"), help="nyelv / language")
    parser.add_argument("--version", action="version", version=f"TuxoMage {__version__}")
    args = parser.parse_args(argv)
    app = App(fullscreen=True if args.fullscreen else None, audio=not args.mute)
    if args.lang:
        app.store.settings["lang"] = args.lang
        set_lang(args.lang)
        app.scene = MenuScene(app)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
