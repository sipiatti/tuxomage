"""Drawing of cards, card backs, towers, firewalls and resource panels."""
from __future__ import annotations

import math
from functools import lru_cache

import pygame

from . import theme
from .cards import BY_ID, CATEGORY_NAMES, Card
from .i18n import lang
from .resources import font, image
from .ui import mix

CARD_W, CARD_H = 150, 210
ZOOM_W, ZOOM_H = 250, 350


def wrap(msg: str, f: pygame.font.Font, width: int) -> list[str]:
    lines, cur = [], ""
    for word in msg.split():
        test = f"{cur} {word}".strip()
        if f.size(test)[0] <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(msg: str, max_w: int, size: int, weight="black", min_size=10) -> pygame.font.Font:
    while size > min_size and font(size, weight).size(msg)[0] > max_w:
        size -= 1
    return font(size, weight)


def _blit_center(surf, img, center):
    surf.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))


@lru_cache(maxsize=512)
def card_surface(cid: str, w: int = CARD_W, h: int = CARD_H, language: str = "hu", dim: bool = False) -> pygame.Surface:
    c: Card = BY_ID[cid]
    s = w / CARD_W
    main, light, dark = theme.CAT_COLORS[c.cat]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    r = int(14 * s)
    pygame.draw.rect(surf, theme.WHITE, (0, 0, w, h), border_radius=r)
    pygame.draw.rect(surf, light, (0, 0, w, int(34 * s)), border_top_left_radius=r, border_top_right_radius=r)
    # name
    name = c.name(language)
    f = fit_font(name, int(w - 16 * s), int(19 * s), "black", int(11 * s))
    img = f.render(name, True, dark)
    _blit_center(surf, img, (w / 2, 18 * s))
    # art
    aw = int(w - 14 * s)
    ah = int(aw * 190 / 300)
    art = pygame.transform.smoothscale(image(f"cardart/{cid}.png"), (aw, ah))
    ax, ay = int(7 * s), int(34 * s)
    mask = pygame.Surface((aw, ah), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=int(8 * s))
    art = art.convert_alpha() if pygame.display.get_surface() else art
    art_masked = pygame.Surface((aw, ah), pygame.SRCALPHA)
    art_masked.blit(art, (0, 0))
    art_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(art_masked, (ax, ay))
    pygame.draw.rect(surf, mix(main, theme.WHITE, 0.3), (ax, ay, aw, ah), max(1, int(2 * s)), border_radius=int(8 * s))
    # text
    top = ay + ah + int(5 * s)
    bottom = h - int(30 * s)
    body = c.text(language)
    size = int(15 * s)
    while True:
        tf = font(size, "bold")
        lines = wrap(body, tf, int(w - 16 * s))
        lh = tf.get_linesize() - int(4 * s)
        if len(lines) * lh <= bottom - top or size <= int(9 * s):
            break
        size -= 1
    y = top + max(0, (bottom - top - len(lines) * lh) // 2)
    for line in lines:
        img = tf.render(line, True, theme.TEXT)
        surf.blit(img, img.get_rect(midtop=(w // 2, y)))
        y += lh
    # footer: category + cost badge
    cat = CATEGORY_NAMES[language][c.cat]
    img = font(int(12 * s), "bold").render(cat, True, mix(dark, theme.WHITE, 0.25))
    surf.blit(img, img.get_rect(midleft=(int(10 * s), h - int(15 * s))))
    br = int(17 * s)
    bc = (w - int(22 * s), h - int(20 * s))
    pygame.draw.circle(surf, dark, (bc[0], bc[1] + int(2 * s)), br)
    pygame.draw.circle(surf, main, bc, br)
    pygame.draw.circle(surf, theme.WHITE, bc, br, max(2, int(2.5 * s)))
    ico = image(f"icons/res_{c.resource}.png", int(18 * s))
    surf.blit(ico, ico.get_rect(center=(bc[0] - br - int(8 * s), bc[1])))
    num = font(int(20 * s), "black").render(str(c.cost), True, theme.WHITE)
    _blit_center(surf, num, (bc[0], bc[1] + int(1 * s)))
    # border
    pygame.draw.rect(surf, main, (0, 0, w, h), max(2, int(4 * s)), border_radius=r)
    if c.play_again or c.draw_discard:          # little "again" ribbon
        pygame.draw.circle(surf, theme.HINT_GLOW, (int(w - 14 * s), int(44 * s)), int(9 * s))
        pygame.draw.circle(surf, theme.WHITE, (int(w - 14 * s), int(44 * s)), int(9 * s), max(1, int(2 * s)))
        star = font(int(14 * s), "black").render("+", True, dark)
        _blit_center(surf, star, (w - 14 * s, 45 * s))
    if dim:
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(veil, (236, 232, 244, 165), veil.get_rect(), border_radius=r)
        surf.blit(veil, (0, 0))
    return surf


@lru_cache(maxsize=16)
def card_back(w: int = CARD_W, h: int = CARD_H) -> pygame.Surface:
    s = w / CARD_W
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    r = int(14 * s)
    pygame.draw.rect(surf, (178, 150, 240), (0, 0, w, h), border_radius=r)
    inner = pygame.Rect(0, 0, w, h).inflate(-int(16 * s), -int(16 * s))
    pygame.draw.rect(surf, (204, 186, 255), inner, border_radius=int(10 * s))
    for i in range(-h, w, int(18 * s)):
        pygame.draw.line(surf, (214, 200, 255), (inner.x + i, inner.bottom), (inner.x + i + inner.h, inner.y), max(1, int(3 * s)))
    pygame.draw.rect(surf, theme.WHITE, inner, max(2, int(3 * s)), border_radius=int(10 * s))
    logo = image("icons/tuxomage.png", int(w * 0.62))
    surf.blit(logo, logo.get_rect(center=(w // 2, h // 2)))
    pygame.draw.rect(surf, (128, 96, 214), (0, 0, w, h), max(2, int(4 * s)), border_radius=r)
    return surf


# ------------------------------------------------------------------ towers
def draw_tower(surf, cx: int, ground: int, height: float, tint, t: float, flag=(255, 209, 102), shake=0.0):
    """Ice-block tower with a cone roof and a waving flag; ``height`` in pixels (body only)."""
    w = 92
    h = max(6, int(height))
    x = int(cx - w / 2 + math.sin(t * 60) * shake * 4)
    body = pygame.Rect(x, ground - h, w, h)
    light = mix(tint, theme.WHITE, 0.55)
    dark = mix(tint, (80, 60, 120), 0.35)
    pygame.draw.rect(surf, light, body)
    # ice block rows
    row = 18
    clip = surf.get_clip()
    surf.set_clip(body)
    for i, y in enumerate(range(ground, ground - h - row, -row)):
        off = 0 if i % 2 == 0 else 23
        for bx in range(x - 46 + off, x + w, 46):
            r = pygame.Rect(bx + 2, y - row + 2, 42, row - 3)
            pygame.draw.rect(surf, mix(tint, theme.WHITE, 0.72 if (i + bx // 46) % 3 else 0.62), r, border_radius=4)
            pygame.draw.line(surf, theme.WHITE, (r.x + 5, r.y + 3), (r.x + 16, r.y + 3), 2)
    surf.set_clip(clip)
    # windows
    for wy in range(ground - 46, ground - h + 34, -64):
        win = pygame.Rect(0, 0, 18, 24)
        win.midbottom = (body.centerx, wy)
        pygame.draw.rect(surf, (74, 61, 107), win, border_top_left_radius=9, border_top_right_radius=9)
        pygame.draw.rect(surf, (255, 230, 140), win.inflate(-6, -6), border_top_left_radius=6, border_top_right_radius=6)
    pygame.draw.rect(surf, dark, body, 3)
    # battlements + cone roof
    top = ground - h
    for i in range(4):
        pygame.draw.rect(surf, light, (x - 4 + i * 26, top - 10, 18, 12), border_radius=3)
        pygame.draw.rect(surf, dark, (x - 4 + i * 26, top - 10, 18, 12), 3, border_radius=3)
    roof = [(x - 10, top - 8), (x + w + 10, top - 8), (x + w / 2, top - 70)]
    pygame.draw.polygon(surf, tint, roof)
    pygame.draw.polygon(surf, dark, roof, 3)
    pygame.draw.line(surf, theme.WHITE, (x + 14, top - 16), (x + w / 2 - 4, top - 62), 3)
    # flag pole + waving flag
    px, py = x + w / 2, top - 70
    pygame.draw.line(surf, (74, 61, 107), (px, py), (px, py - 34), 3)
    pts = []
    for i in range(9):
        fx = px + i * 4
        fy = py - 34 + math.sin(t * 5 + i * 0.7) * 2.5 * (i / 8)
        pts.append((fx, fy))
    pts += [(fx, fy + 16) for fx, fy in reversed(pts)]
    pygame.draw.polygon(surf, flag, pts)
    pygame.draw.polygon(surf, (74, 61, 107), pts, 2)
    return body


def draw_wall(surf, cx: int, ground: int, height: float, t: float, shake=0.0):
    """Firewall: brick wall with little flames on top."""
    w = 40
    h = int(height)
    if h <= 0:
        pygame.draw.rect(surf, (230, 200, 190), (cx - w // 2, ground - 4, w, 4), border_radius=2)
        return pygame.Rect(cx - w // 2, ground - 4, w, 4)
    x = int(cx - w / 2 + math.sin(t * 60) * shake * 4)
    body = pygame.Rect(x, ground - h, w, h)
    pygame.draw.rect(surf, (255, 190, 160), body)
    clip = surf.get_clip()
    surf.set_clip(body)
    row = 12
    for i, y in enumerate(range(ground, ground - h - row, -row)):
        off = 0 if i % 2 == 0 else 10
        for bx in range(x - 20 + off, x + w, 20):
            pygame.draw.rect(surf, (255, 150, 120) if (i + bx // 20) % 2 else (250, 132, 104),
                             (bx + 1, y - row + 1, 18, row - 2), border_radius=2)
    surf.set_clip(clip)
    pygame.draw.rect(surf, (200, 90, 70), body, 3)
    # flames
    top = ground - h
    for i, fx in enumerate((x + 8, x + 20, x + 32)):
        fl = 12 + 5 * math.sin(t * 9 + i * 1.9)
        pts = [(fx - 7, top), (fx - 4, top - fl * 0.6), (fx, top - fl), (fx + 4, top - fl * 0.6), (fx + 7, top)]
        pygame.draw.polygon(surf, (255, 170, 60), pts)
        inner = [(fx - 3, top), (fx, top - fl * 0.55), (fx + 3, top)]
        pygame.draw.polygon(surf, (255, 230, 120), inner)
    return body
