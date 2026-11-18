#!/usr/bin/env python3
"""Generate TuxoMage's original artwork: penguin mascots, UI icons, 102 card
illustrations and the application icon (SVG sources + PNG renders).

Everything this script produces is original work for TuxoMage and is
released under CC0 1.0 (public domain dedication). Re-run after editing:

    pip install cairosvg
    python3 tools/make_assets.py
"""
import random
import sys
from pathlib import Path

import cairosvg

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from tuxomage.cards import DECK  # noqa: E402

ROOT = HERE.parent / "tuxomage" / "assets"
PNG_SIZE = 256
OUTLINE = "#4a3d6b"

# (file id, body colour, body outline, accessory id, mood)
PENGUINS = [
    ("player", "#3b4060", "#262a40", "wizard", "normal"),
    ("player_happy", "#3b4060", "#262a40", "wizard", "happy"),
    ("player_sad", "#3b4060", "#262a40", "wizard", "sad"),
    ("ai", "#4d3b60", "#30243f", "crown", "normal"),
    ("ai_happy", "#4d3b60", "#30243f", "crown", "happy"),
    ("ai_sad", "#4d3b60", "#30243f", "crown", "sad"),
]

ACCESSORIES = {
    "bowtie": """
      <g transform="translate(100 120)">
        <path d="M0 0 L-24 -13 Q-29 0 -24 13 Z" fill="#ff4d6d" stroke="#c9184a" stroke-width="3" stroke-linejoin="round"/>
        <path d="M0 0 L24 -13 Q29 0 24 13 Z" fill="#ff4d6d" stroke="#c9184a" stroke-width="3" stroke-linejoin="round"/>
        <circle r="7" fill="#ff758f" stroke="#c9184a" stroke-width="3"/>
      </g>""",
    "beanie": """
      <path d="M50 58 Q52 12 100 10 Q148 12 150 58 Z" fill="#4cc9f0" stroke="#277da1" stroke-width="4" stroke-linejoin="round"/>
      <path d="M62 30 Q100 18 138 30" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round"/>
      <rect x="44" y="50" width="112" height="20" rx="10" fill="#ffffff" stroke="#277da1" stroke-width="4"/>
      <circle cx="100" cy="10" r="13" fill="#ffffff" stroke="#277da1" stroke-width="4"/>""",
    "party": """
      <path d="M72 56 L100 -2 L128 56 Z" fill="#9b5de5" stroke="#5a189a" stroke-width="4" stroke-linejoin="round"/>
      <path d="M82 36 L118 36 M77 47 L123 47 M89 20 L111 20" stroke="#fee440" stroke-width="6" stroke-linecap="round"/>
      <circle cx="100" cy="0" r="10" fill="#00f5d4" stroke="#00a896" stroke-width="4"/>""",
    "headphones": """
      <path d="M44 86 Q44 20 100 20 Q156 20 156 86" fill="none" stroke="#ff4d8d" stroke-width="10" stroke-linecap="round"/>
      <rect x="28" y="72" width="26" height="40" rx="12" fill="#ff4d8d" stroke="#b5179e" stroke-width="4"/>
      <rect x="146" y="72" width="26" height="40" rx="12" fill="#ff4d8d" stroke="#b5179e" stroke-width="4"/>""",
    "sprout": """
      <path d="M100 48 Q98 30 100 18" fill="none" stroke="#2d6a4f" stroke-width="6" stroke-linecap="round"/>
      <path d="M100 26 Q74 2 58 20 Q76 38 100 26 Z" fill="#95d5b2" stroke="#2d6a4f" stroke-width="4" stroke-linejoin="round"/>
      <path d="M100 22 Q124 -4 144 12 Q126 34 100 22 Z" fill="#b7e4c7" stroke="#2d6a4f" stroke-width="4" stroke-linejoin="round"/>
      <circle cx="58" cy="122" r="0" fill="none"/>""",
    "crown": """
      <path d="M62 56 L58 14 L80 34 L100 6 L120 34 L142 14 L138 56 Z" fill="#ffd60a" stroke="#d39e00" stroke-width="4" stroke-linejoin="round"/>
      <circle cx="100" cy="40" r="7" fill="#ff4d6d" stroke="#c9184a" stroke-width="3"/>
      <circle cx="76" cy="44" r="5" fill="#4cc9f0" stroke="#277da1" stroke-width="3"/>
      <circle cx="124" cy="44" r="5" fill="#80ed99" stroke="#38a169" stroke-width="3"/>""",
    "wizard": """
      <path d="M48 60 Q100 44 152 60 Q160 66 150 70 Q100 58 50 70 Q40 66 48 60 Z" fill="#3a3f9e" stroke="#23266b" stroke-width="4" stroke-linejoin="round"/>
      <path d="M64 60 Q86 30 96 -2 Q110 16 136 58 Z" fill="#4a52c9" stroke="#23266b" stroke-width="4" stroke-linejoin="round"/>
      <path d="M100 22 l4 9 10 1 -8 6 3 10 -9 -6 -9 6 3 -10 -8 -6 10 -1 Z" fill="#ffd60a" stroke="#d39e00" stroke-width="2" stroke-linejoin="round"/>""",
    "bow": """
      <g transform="translate(128 40) rotate(18)">
        <path d="M0 0 Q-30 -26 -36 0 Q-30 26 0 0 Z" fill="#ffd23f" stroke="#e09f00" stroke-width="4" stroke-linejoin="round"/>
        <path d="M0 0 Q30 -26 36 0 Q30 26 0 0 Z" fill="#ffd23f" stroke="#e09f00" stroke-width="4" stroke-linejoin="round"/>
        <circle r="8" fill="#ffe66d" stroke="#e09f00" stroke-width="4"/>
      </g>""",
    "tophat": """
      <rect x="46" y="48" width="108" height="14" rx="7" fill="#2b2d42" stroke="#14151f" stroke-width="4"/>
      <rect x="66" y="0" width="68" height="54" rx="6" fill="#2b2d42" stroke="#14151f" stroke-width="4"/>
      <rect x="66" y="34" width="68" height="12" fill="#ff8fab"/>""",
}


def penguin_svg(body: str, outline: str, accessory: str, mood: str = "normal") -> str:
    acc = ACCESSORIES[accessory]
    # Accessories that sit *under* the head outline (headphones band) are drawn first.
    if mood == "happy":
        eyes = """  <path d="M74 86 Q84 72 94 86" fill="none" stroke="#1d1d2c" stroke-width="5" stroke-linecap="round"/>
  <path d="M106 86 Q116 72 126 86" fill="none" stroke="#1d1d2c" stroke-width="5" stroke-linecap="round"/>"""
    elif mood == "sad":
        eyes = """  <ellipse cx="84" cy="84" rx="8" ry="9" fill="#1d1d2c"/>
  <ellipse cx="116" cy="84" rx="8" ry="9" fill="#1d1d2c"/>
  <circle cx="86" cy="80" r="3" fill="#ffffff"/><circle cx="118" cy="80" r="3" fill="#ffffff"/>
  <path d="M72 70 L92 64 M128 70 L108 64" stroke="#1d1d2c" stroke-width="4" stroke-linecap="round"/>
  <path d="M124 94 Q130 104 124 108 Q118 104 124 94 Z" fill="#7cc6fe" stroke="#3a86ff" stroke-width="2"/>"""
    else:
        eyes = """  <ellipse cx="84" cy="82" rx="9" ry="11" fill="#1d1d2c"/>
  <ellipse cx="116" cy="82" rx="9" ry="11" fill="#1d1d2c"/>
  <circle cx="87" cy="77" r="3.6" fill="#ffffff"/>
  <circle cx="119" cy="77" r="3.6" fill="#ffffff"/>"""
    behind = acc if accessory == "headphones" else ""
    front = "" if accessory == "headphones" else acc
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -8 200 212" width="{PNG_SIZE}" height="{PNG_SIZE}">
  <ellipse cx="100" cy="196" rx="62" ry="7" fill="#000000" opacity="0.12"/>
  {behind}
  <!-- feet -->
  <ellipse cx="72" cy="186" rx="24" ry="10" fill="#ffa62b" stroke="#e07b00" stroke-width="4"/>
  <ellipse cx="128" cy="186" rx="24" ry="10" fill="#ffa62b" stroke="#e07b00" stroke-width="4"/>
  <!-- wings -->
  <ellipse cx="42" cy="128" rx="16" ry="38" transform="rotate(18 42 128)" fill="{body}" stroke="{outline}" stroke-width="4"/>
  <ellipse cx="158" cy="128" rx="16" ry="38" transform="rotate(-18 158 128)" fill="{body}" stroke="{outline}" stroke-width="4"/>
  <!-- body -->
  <path d="M100 40 C146 40 162 84 162 124 C162 166 136 184 100 184 C64 184 38 166 38 124 C38 84 54 40 100 40 Z"
        fill="{body}" stroke="{outline}" stroke-width="4"/>
  <!-- belly + face -->
  <path d="M100 92 C130 92 142 116 142 140 C142 164 124 176 100 176 C76 176 58 164 58 140 C58 116 70 92 100 92 Z" fill="#fffdf7"/>
  <ellipse cx="82" cy="82" rx="21" ry="24" fill="#fffdf7"/>
  <ellipse cx="118" cy="82" rx="21" ry="24" fill="#fffdf7"/>
{eyes}
  <!-- cheeks -->
  <ellipse cx="68" cy="102" rx="9" ry="6" fill="#ff8fab" opacity="0.65"/>
  <ellipse cx="132" cy="102" rx="9" ry="6" fill="#ff8fab" opacity="0.65"/>
  <!-- beak -->
  <path d="M86 98 Q100 90 114 98 Q108 112 100 113 Q92 112 86 98 Z" fill="#ffb627" stroke="#e07b00" stroke-width="3.5" stroke-linejoin="round"/>
  <path d="M90 102 Q100 106 110 102" fill="none" stroke="#e07b00" stroke-width="2.5" stroke-linecap="round"/>
  {front}
</svg>"""


# ----------------------------------------------------------------- UI icons
BASE_ICONS = {
    "heart": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <path d="M50 88 C20 66 6 50 6 32 C6 18 17 8 30 8 C40 8 46 14 50 22 C54 14 60 8 70 8 C83 8 94 18 94 32 C94 50 80 66 50 88 Z"
        fill="#ff5d8f" stroke="#c9184a" stroke-width="5" stroke-linejoin="round"/>
  <path d="M24 26 Q28 18 36 18" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.8"/>
</svg>""",
    "music": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <path d="M38 22 L82 12 L82 66" fill="none" stroke="#ffffff" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M38 22 L38 74" stroke="#ffffff" stroke-width="9" stroke-linecap="round"/>
  <path d="M38 30 L82 20" stroke="#ffffff" stroke-width="12"/>
  <ellipse cx="27" cy="76" rx="15" ry="11" transform="rotate(-20 27 76)" fill="#ffffff"/>
  <ellipse cx="71" cy="68" rx="15" ry="11" transform="rotate(-20 71 68)" fill="#ffffff"/>
</svg>""",
    "music_off": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <g opacity="0.75">
  <path d="M38 22 L82 12 L82 66" fill="none" stroke="#ffffff" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M38 22 L38 74" stroke="#ffffff" stroke-width="9" stroke-linecap="round"/>
  <path d="M38 30 L82 20" stroke="#ffffff" stroke-width="12"/>
  <ellipse cx="27" cy="76" rx="15" ry="11" transform="rotate(-20 27 76)" fill="#ffffff"/>
  <ellipse cx="71" cy="68" rx="15" ry="11" transform="rotate(-20 71 68)" fill="#ffffff"/>
  </g>
  <path d="M12 12 L88 88" stroke="#ff4d6d" stroke-width="12" stroke-linecap="round"/>
</svg>""",
    "speaker": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <path d="M10 38 L28 38 L50 18 L50 82 L28 62 L10 62 Z" fill="#ffffff" stroke="#ffffff" stroke-width="6" stroke-linejoin="round"/>
  <path d="M62 36 Q72 50 62 64" fill="none" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>
  <path d="M72 24 Q92 50 72 76" fill="none" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>
</svg>""",
    "speaker_off": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <path d="M10 38 L28 38 L50 18 L50 82 L28 62 L10 62 Z" fill="#ffffff" stroke="#ffffff" stroke-width="6" stroke-linejoin="round" opacity="0.75"/>
  <path d="M64 36 L88 64 M88 36 L64 64" stroke="#ff4d6d" stroke-width="10" stroke-linecap="round"/>
</svg>""",
    "gear": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <g fill="#ffffff">
    <circle cx="50" cy="50" r="28"/>
    <g id="t"><rect x="42" y="6" width="16" height="22" rx="4"/></g>
    <use href="#t" transform="rotate(45 50 50)"/><use href="#t" transform="rotate(90 50 50)"/>
    <use href="#t" transform="rotate(135 50 50)"/><use href="#t" transform="rotate(180 50 50)"/>
    <use href="#t" transform="rotate(225 50 50)"/><use href="#t" transform="rotate(270 50 50)"/>
    <use href="#t" transform="rotate(315 50 50)"/>
  </g>
  <circle cx="50" cy="50" r="11" fill="#b291ff"/>
</svg>""",
    "question": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <path d="M30 34 Q30 12 50 12 Q72 12 72 32 Q72 46 56 52 Q50 55 50 64" fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="50" cy="84" r="8" fill="#ffffff"/>
</svg>""",
    "star": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">
  <path d="M50 6 L62 36 L94 38 L69 58 L78 90 L50 72 L22 90 L31 58 L6 38 L38 36 Z" fill="#ffd60a" stroke="#e09f00" stroke-width="5" stroke-linejoin="round"/>
  <path d="M40 40 L46 30" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
</svg>""",
    "snowflake": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="64" height="64">
  <g stroke="#ffffff" stroke-width="7" stroke-linecap="round" fill="none">
    <path d="M50 8 L50 92 M14 29 L86 71 M14 71 L86 29"/>
    <path d="M40 16 L50 26 L60 16 M40 84 L50 74 L60 84"/>
  </g>
</svg>""",
}


def _icon(inner: str, size=128) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}">'
            f'<g stroke="{OUTLINE}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">{inner}</g></svg>')


UI_ICONS = {
    # stocks
    "res_code": _icon("""<rect x="8" y="14" width="84" height="72" rx="16" fill="#ff9f8a"/>
        <path d="M36 32 L18 50 L36 68 M64 32 L82 50 L64 68 M56 26 L44 74" fill="none" stroke="#ffffff" stroke-width="8"/>"""),
    "res_bytes": _icon("""<path d="M50 6 L90 28 V72 L50 94 L10 72 V28 Z" fill="#8fb8ff"/>
        <text x="50" y="62" font-family="monospace" font-weight="bold" font-size="32" text-anchor="middle" fill="#ffffff" stroke="none">01</text>"""),
    "res_penguins": _icon("""<circle cx="50" cy="50" r="42" fill="#7fdcaa"/>
        <path d="M50 18 Q74 18 74 50 Q74 80 50 80 Q26 80 26 50 Q26 18 50 18 Z" fill="#3b4060" stroke-width="3"/>
        <path d="M50 40 Q66 40 66 58 Q66 74 50 74 Q34 74 34 58 Q34 40 50 40 Z" fill="#ffffff" stroke="none"/>
        <circle cx="42" cy="36" r="4" fill="#ffffff" stroke="none"/><circle cx="58" cy="36" r="4" fill="#ffffff" stroke="none"/>
        <path d="M44 46 L56 46 L50 54 Z" fill="#ffb627" stroke-width="2"/>"""),
    # producers
    "prod_compiler": _icon("""<path d="M44 8 H56 L58 20 L68 24 L78 16 L86 24 L78 34 L82 44 L94 46 V56 L82 58 L78 68 L86 78 L78 86 L68 78 L58 82 L56 94 H44 L42 82 L32 78 L22 86 L14 78 L22 68 L18 58 L6 56 V46 L18 44 L22 34 L14 24 L22 16 L32 24 L42 20 Z" fill="#ff9f8a"/>
        <circle cx="50" cy="51" r="20" fill="#ffffff"/><path d="M44 42 L36 51 L44 60 M56 42 L64 51 L56 60" fill="none" stroke-width="5"/>"""),
    "prod_kernel": _icon("""<circle cx="50" cy="50" r="42" fill="#8fb8ff"/>
        <g fill="none" stroke="#ffffff" stroke-width="5"><ellipse cx="50" cy="50" rx="32" ry="12"/>
        <ellipse cx="50" cy="50" rx="32" ry="12" transform="rotate(60 50 50)"/><ellipse cx="50" cy="50" rx="32" ry="12" transform="rotate(-60 50 50)"/></g>
        <circle cx="50" cy="50" r="8" fill="#ffd166"/>"""),
    "prod_colony": _icon("""<path d="M8 84 A42 42 0 0 1 92 84 Z" fill="#7fdcaa"/>
        <path d="M18 64 H82 M28 46 H72 M34 84 V64 M66 84 V64 M44 64 V46 M58 64 V46" stroke="#ffffff" stroke-width="4"/>
        <path d="M38 84 V72 Q50 58 62 72 V84 Z" fill="#3b4060"/>"""),
    "tower": _icon("""<path d="M26 92 V34 H74 V92 Z" fill="#cfe3ff"/><path d="M20 36 L50 8 L80 36 Z" fill="#ff8fab"/>
        <path d="M26 54 H74 M26 72 H74 M50 36 V54 M38 54 V72 M62 54 V72 M50 72 V92" stroke-width="3"/>"""),
    "wall": _icon("""<g fill="#ff9f7a"><rect x="8" y="26" width="40" height="20" rx="3"/><rect x="52" y="26" width="40" height="20" rx="3"/>
        <rect x="8" y="50" width="18" height="20" rx="3"/><rect x="30" y="50" width="40" height="20" rx="3"/><rect x="74" y="50" width="18" height="20" rx="3"/>
        <rect x="8" y="74" width="40" height="20" rx="3"/><rect x="52" y="74" width="40" height="20" rx="3"/></g>
        <path d="M30 26 Q22 12 32 4 Q34 14 42 14 Q42 22 38 26 Z M66 26 Q58 14 68 6 Q70 14 76 14 Q76 22 72 26 Z" fill="#ffd166" stroke-width="3"/>"""),
    "trophy": _icon("""<path d="M28 12 H72 V36 Q72 62 50 62 Q28 62 28 36 Z" fill="#ffd166"/>
        <path d="M28 20 H12 Q12 44 32 46 M72 20 H88 Q88 44 68 46" fill="none" stroke-width="6"/>
        <path d="M44 62 H56 V76 H44 Z" fill="#ffb627"/><rect x="28" y="76" width="44" height="14" rx="4" fill="#ff8fab"/>
        <path d="M50 22 l4 8 9 1 -7 6 2 9 -8 -5 -8 5 2 -9 -7 -6 9 -1 Z" fill="#ffffff" stroke-width="2"/>"""),
    "trash": _icon("""<path d="M22 30 H78 L72 90 H28 Z" fill="#ffadad"/><rect x="14" y="20" width="72" height="12" rx="4" fill="#ff8fab"/>
        <path d="M40 20 V12 H60 V20 M40 44 L42 78 M60 44 L58 78 M50 44 V78" fill="none" stroke-width="5"/>"""),
    "home": _icon("""<path d="M10 50 L50 12 L90 50" fill="none" stroke-width="8"/><path d="M22 46 V88 H78 V46 L50 20 Z" fill="#ffd6a5"/>
        <rect x="42" y="62" width="16" height="26" fill="#ff8fab"/>"""),
    "cards": _icon("""<rect x="12" y="22" width="44" height="62" rx="8" fill="#8fb8ff" transform="rotate(-14 34 53)"/>
        <rect x="44" y="18" width="44" height="62" rx="8" fill="#ff9f8a" transform="rotate(12 66 49)"/>
        <rect x="30" y="16" width="44" height="64" rx="8" fill="#7fdcaa"/><circle cx="52" cy="48" r="11" fill="#ffffff"/>"""),
    "globe": _icon("""<circle cx="50" cy="50" r="40" fill="#9bf6ff"/><path d="M10 50 H90 M50 10 Q28 50 50 90 Q72 50 50 10" fill="none" stroke-width="4"/>
        <path d="M18 30 H82 M18 70 H82" stroke-width="3"/>"""),
    "robot": _icon("""<rect x="18" y="26" width="64" height="52" rx="14" fill="#c9b6f2"/><circle cx="38" cy="50" r="8" fill="#ffffff"/>
        <circle cx="62" cy="50" r="8" fill="#ffffff"/><path d="M50 26 V12" stroke-width="5"/><circle cx="50" cy="10" r="6" fill="#ff8fab"/>
        <path d="M38 66 H62" stroke-width="5"/>"""),
    "arrow_left": _icon("""<path d="M64 14 L28 50 L64 86" fill="none" stroke-width="14"/><path d="M64 14 L28 50 L64 86" fill="none" stroke="#ffffff" stroke-width="5"/>"""),
    "arrow_right": _icon("""<path d="M36 14 L72 50 L36 86" fill="none" stroke-width="14"/><path d="M36 14 L72 50 L36 86" fill="none" stroke="#ffffff" stroke-width="5"/>"""),
    "pause": _icon("""<rect x="22" y="16" width="20" height="68" rx="6" fill="#ffffff"/><rect x="58" y="16" width="20" height="68" rx="6" fill="#ffffff"/>"""),
}

# --------------------------------------------------------------- card art
# ----------------------------------------------------------------------------
# Card illustrations: one symbolic glyph per card (100x100 viewBox), drawn with
# a shared dark-violet outline.  Composed onto a category background below.
# ----------------------------------------------------------------------------
GLYPHS = {
    "snowflake": """<g fill="none" stroke-width="7"><path d="M50 10 V90 M15 30 L85 70 M15 70 L85 30" stroke="#7cc6fe"/>
      <path d="M40 16 L50 26 L60 16 M40 84 L50 74 L60 84" stroke="#7cc6fe"/></g>
      <circle cx="50" cy="50" r="9" fill="#ffffff"/>""",
    "clover": """<circle cx="38" cy="38" r="15" fill="#80ed99"/><circle cx="62" cy="38" r="15" fill="#80ed99"/>
      <circle cx="38" cy="60" r="15" fill="#80ed99"/><circle cx="62" cy="60" r="15" fill="#80ed99"/>
      <path d="M50 52 Q58 78 72 90" fill="none" stroke-width="6"/><circle cx="50" cy="49" r="6" fill="#ffd60a"/>""",
    "bandage": """<g transform="rotate(-35 50 50)"><rect x="12" y="36" width="76" height="28" rx="14" fill="#ffcf99"/>
      <rect x="36" y="36" width="28" height="28" fill="#fff1e0"/>
      <circle cx="44" cy="44" r="2" fill="#4a3d6b" stroke="none"/><circle cx="56" cy="44" r="2" fill="#4a3d6b" stroke="none"/>
      <circle cx="44" cy="56" r="2" fill="#4a3d6b" stroke="none"/><circle cx="56" cy="56" r="2" fill="#4a3d6b" stroke="none"/></g>""",
    "keyboard": """<rect x="8" y="30" width="84" height="44" rx="8" fill="#e0d7ff"/>
      <g fill="#ffffff" stroke-width="3"><rect x="16" y="38" width="10" height="9" rx="2"/><rect x="30" y="38" width="10" height="9" rx="2"/>
      <rect x="44" y="38" width="10" height="9" rx="2"/><rect x="58" y="38" width="10" height="9" rx="2"/><rect x="72" y="38" width="12" height="9" rx="2"/>
      <rect x="16" y="52" width="14" height="9" rx="2"/><rect x="34" y="52" width="32" height="9" rx="2"/><rect x="70" y="52" width="14" height="9" rx="2"/></g>""",
    "branch": """<path d="M30 85 V20 M30 62 Q30 44 70 40 V30" fill="none" stroke-width="7" stroke="#ff8fab"/>
      <circle cx="30" cy="20" r="10" fill="#ffd166"/><circle cx="30" cy="85" r="10" fill="#ffd166"/><circle cx="70" cy="26" r="10" fill="#9bf6ff"/>""",
    "coffee": """<path d="M22 40 H70 V70 Q70 86 54 86 H38 Q22 86 22 70 Z" fill="#ffffff"/>
      <path d="M70 48 Q86 48 86 60 Q86 72 70 70" fill="none" stroke-width="6"/>
      <rect x="27" y="44" width="38" height="10" fill="#b5835a" stroke="none"/>
      <path d="M36 32 Q30 24 36 16 M50 32 Q44 24 50 14 M64 32 Q58 24 64 16" fill="none" stroke="#c9b6f2" stroke-width="4"/>""",
    "moon": """<path d="M62 14 A38 38 0 1 0 86 64 A30 30 0 1 1 62 14 Z" fill="#ffe66d"/>
      <circle cx="78" cy="22" r="3" fill="#ffffff"/><circle cx="86" cy="40" r="2" fill="#ffffff"/>""",
    "fork": """<path d="M50 90 V55 M50 55 Q50 40 28 34 V12 M50 55 Q50 40 72 34 V12" fill="none" stroke-width="7" stroke="#a0c4ff"/>
      <circle cx="28" cy="14" r="9" fill="#ffadad"/><circle cx="72" cy="14" r="9" fill="#caffbf"/><circle cx="50" cy="88" r="9" fill="#ffd166"/>""",
    "wall": """<g fill="#ff9f7a"><rect x="10" y="22" width="38" height="18" rx="3"/><rect x="52" y="22" width="38" height="18" rx="3"/>
      <rect x="10" y="44" width="18" height="18" rx="3"/><rect x="32" y="44" width="36" height="18" rx="3"/><rect x="72" y="44" width="18" height="18" rx="3"/>
      <rect x="10" y="66" width="38" height="18" rx="3"/><rect x="52" y="66" width="38" height="18" rx="3"/></g>
      <path d="M30 22 Q24 10 32 4 Q34 14 40 12 Q40 18 36 22 Z M66 22 Q60 12 68 6 Q70 14 74 14 Q74 18 72 22 Z" fill="#ffd166" stroke-width="3"/>""",
    "funnel": """<path d="M12 18 H88 L58 54 V82 L42 90 V54 Z" fill="#a0c4ff"/>
      <circle cx="30" cy="10" r="5" fill="#ffadad" stroke-width="3"/><circle cx="50" cy="8" r="5" fill="#caffbf" stroke-width="3"/><circle cx="70" cy="10" r="5" fill="#ffd166" stroke-width="3"/>""",
    "scroll": """<rect x="22" y="18" width="56" height="66" rx="4" fill="#fff4d6"/>
      <circle cx="22" cy="22" r="8" fill="#ffd6a5"/><circle cx="78" cy="80" r="8" fill="#ffd6a5"/>
      <path d="M32 36 H68 M32 48 H68 M32 60 H58" stroke-width="4"/>""",
    "disc": """<circle cx="50" cy="50" r="38" fill="#e0e7ff"/><circle cx="50" cy="50" r="38" fill="none" stroke="#c9b6f2" stroke-width="2"/>
      <path d="M50 18 A32 32 0 0 1 82 50" fill="none" stroke="#ffadad" stroke-width="5"/><path d="M50 82 A32 32 0 0 1 18 50" fill="none" stroke="#9bf6ff" stroke-width="5"/>
      <circle cx="50" cy="50" r="10" fill="#ffffff"/>""",
    "quake": """<path d="M8 70 H30 L38 52 L48 82 L58 40 L66 70 H92" fill="none" stroke="#ff6b6b" stroke-width="6"/>
      <rect x="30" y="16" width="40" height="22" rx="4" fill="#b8c0ff" transform="rotate(-8 50 27)"/>
      <path d="M20 30 L26 34 M80 30 L74 34" stroke-width="4"/>""",
    "puzzle": """<path d="M20 30 H40 Q36 18 48 18 Q60 18 56 30 H78 V50 Q90 46 90 58 Q90 70 78 66 V84 H20 V64 Q8 68 8 56 Q8 44 20 48 Z" fill="#bdb2ff"/>""",
    "knot": """<path d="M20 50 C20 20 50 20 50 50 C50 80 80 80 80 50 C80 20 50 20 50 50 C50 80 20 80 20 50 Z" fill="none" stroke="#ff8fab" stroke-width="8"/>
      <path d="M14 30 L28 20 M86 70 L72 80" stroke-width="5"/>""",
    "shield": """<path d="M50 8 L86 22 V48 Q86 76 50 92 Q14 76 14 48 V22 Z" fill="#ff9f7a"/>
      <path d="M50 18 L76 28 V48 Q76 68 50 80 Z" fill="#ffd6a5" stroke="none"/>
      <path d="M38 48 Q38 32 50 30 Q48 40 56 42 Q62 50 56 60 Q50 66 44 60 Q38 56 38 48 Z" fill="#ffd166" stroke-width="3"/>""",
    "brokengear": """<path d="M50 14 L58 16 L60 26 L70 30 L78 24 L84 32 L78 40 L80 50 L90 54 L88 62 L48 50 Z" fill="#c9b6f2"/>
      <path d="M44 56 L86 66 L82 74 L72 72 L66 80 L68 90 L58 92 L54 82 L44 80 L36 86 L28 80 L32 70 L26 62 L16 60 L16 50 L26 46 L30 36 L22 28 L30 20 L38 26 L44 22 L46 14 Z" fill="#c9b6f2"/>
      <circle cx="44" cy="52" r="10" fill="#ffffff"/><path d="M60 40 L52 60" stroke="#ff6b6b" stroke-width="4"/>""",
    "monitor": """<rect x="10" y="16" width="80" height="54" rx="6" fill="#4a3d6b"/><rect x="16" y="22" width="68" height="42" rx="3" fill="#9bf6ff" stroke="none"/>
      <path d="M24 34 L32 40 L24 46 M36 48 H48" fill="none" stroke="#4a3d6b" stroke-width="4"/>
      <path d="M40 70 L36 84 H64 L60 70" fill="#c9b6f2"/>""",
    "broom": """<path d="M76 10 L46 52" stroke="#b5835a" stroke-width="8"/><path d="M30 46 L56 60 L44 90 Q24 86 14 72 Z" fill="#ffd166"/>
      <path d="M26 64 L40 72 M20 72 L36 82" stroke-width="3"/>
      <path d="M70 70 l3 7 7 1 -6 4 2 7 -6 -4 -6 4 2 -7 -6 -4 7 -1 Z" fill="#ffffff" stroke-width="2.5"/>""",
    "tent": """<path d="M50 12 L90 84 H10 Z" fill="#ffadad"/><path d="M50 12 L64 84 H36 Z" fill="#ffd6a5"/>
      <path d="M50 12 V6 L64 10 L50 14" fill="#80ed99" stroke-width="3"/><path d="M4 84 H96" stroke-width="5"/>""",
    "diamond": """<path d="M28 18 H72 L90 40 L50 90 L10 40 Z" fill="#9bf6ff"/><path d="M10 40 H90 M28 18 L40 40 L50 90 L60 40 L72 18" fill="none" stroke-width="3"/>
      <path d="M40 40 L50 18 L60 40" fill="none" stroke-width="3"/>""",
    "package": """<path d="M50 10 L88 28 V72 L50 90 L12 72 V28 Z" fill="#ffd6a5"/><path d="M12 28 L50 46 L88 28 M50 46 V90" fill="none"/>
      <path d="M31 19 L69 37 V50" fill="none" stroke="#ff8fab" stroke-width="6"/>""",
    "castle": """<path d="M14 90 V36 H24 V44 H34 V36 H44 V44 H56 V36 H66 V44 H76 V36 H86 V90 Z" fill="#ffadad"/>
      <path d="M40 90 V70 Q50 58 60 70 V90" fill="#4a3d6b"/><path d="M50 36 V10 L70 16 L50 22" fill="#ffd166" stroke-width="3.5"/>""",
    "calendar": """<rect x="14" y="18" width="72" height="68" rx="8" fill="#ffffff"/><path d="M14 36 H86" stroke-width="4"/>
      <rect x="14" y="18" width="72" height="18" rx="8" fill="#ff8fab"/><path d="M30 10 V24 M70 10 V24" stroke-width="6"/>
      <text x="50" y="76" font-family="sans-serif" font-weight="bold" font-size="30" text-anchor="middle" fill="#4a3d6b" stroke="none">LTS</text>""",
    "mountain": """<path d="M4 88 L36 30 L52 54 L64 38 L96 88 Z" fill="#b8c0ff"/><path d="M36 30 L26 48 L34 46 L40 52 L46 44 Z" fill="#ffffff" stroke-width="3"/>
      <path d="M64 38 L56 50 L64 48 L70 52 Z" fill="#ffffff" stroke-width="3"/>""",
    "cannon": """<rect x="20" y="36" width="56" height="24" rx="12" fill="#a0a8c8" transform="rotate(-24 48 48)"/>
      <circle cx="40" cy="70" r="16" fill="#b5835a"/><circle cx="40" cy="70" r="5" fill="#4a3d6b"/>
      <rect x="76" y="12" width="14" height="12" rx="2" fill="#ffd166" stroke-width="3"/><rect x="84" y="28" width="10" height="9" rx="2" fill="#9bf6ff" stroke-width="3"/>""",
    "server": """<rect x="22" y="8" width="56" height="84" rx="6" fill="#d0d6f9"/>
      <g fill="#ffffff" stroke-width="3"><rect x="30" y="16" width="40" height="14" rx="3"/><rect x="30" y="36" width="40" height="14" rx="3"/>
      <rect x="30" y="56" width="40" height="14" rx="3"/></g><circle cx="62" cy="23" r="3" fill="#80ed99" stroke="none"/>
      <circle cx="62" cy="43" r="3" fill="#80ed99" stroke="none"/><circle cx="62" cy="63" r="3" fill="#ff8fab" stroke="none"/>
      <path d="M36 80 H64" stroke-width="4"/>""",
    "hourglass": """<path d="M24 10 H76 M24 90 H76" stroke-width="7"/><path d="M30 12 Q30 40 50 50 Q30 60 30 88 H70 Q70 60 50 50 Q70 40 70 12 Z" fill="#e0f2ff"/>
      <path d="M38 80 Q50 66 62 80 Z M40 24 H60 Q56 38 50 44 Q44 38 40 24 Z" fill="#ffd166" stroke="none"/>""",
    "seedling": """<path d="M50 90 V50" stroke="#52b788" stroke-width="7"/><path d="M50 56 Q22 56 18 28 Q46 26 50 56 Z" fill="#95d5b2"/>
      <path d="M50 48 Q56 18 84 18 Q82 46 50 48 Z" fill="#b7e4c7"/><path d="M26 90 H74" stroke-width="6" stroke="#b5835a"/>""",
    "water": """<path d="M50 8 Q78 46 78 62 A28 28 0 0 1 22 62 Q22 46 50 8 Z" fill="#7cc6fe"/>
      <path d="M36 62 Q36 74 48 78" fill="none" stroke="#ffffff" stroke-width="5"/>""",
    "house": """<path d="M12 48 L50 14 L88 48" fill="none" stroke-width="7"/><path d="M22 44 V88 H78 V44 L50 20 Z" fill="#ffd6a5"/>
      <rect x="42" y="62" width="16" height="26" fill="#ff8fab"/><rect x="28" y="52" width="12" height="12" fill="#9bf6ff" stroke-width="3"/>
      <rect x="60" y="52" width="12" height="12" fill="#9bf6ff" stroke-width="3"/>""",
    "honey": """<path d="M24 40 Q24 30 50 30 Q76 30 76 40 L72 82 Q72 90 50 90 Q28 90 28 82 Z" fill="#ffd166"/>
      <rect x="22" y="22" width="56" height="12" rx="6" fill="#ffadad"/>
      <path d="M36 44 Q36 56 42 56 Q48 56 48 44" fill="#ffb627" stroke-width="3"/>
      <circle cx="74" cy="16" r="6" fill="#ffe66d" stroke-width="3"/><path d="M70 10 L64 4 M78 10 L84 4" stroke-width="3"/>""",
    "swap": """<path d="M14 36 H72 L60 24 M86 64 H28 L40 76" fill="none" stroke-width="8" stroke="#ff8fab"/>
      <path d="M14 36 H72 L60 24 M86 64 H28 L40 76" fill="none" stroke-width="3"/>""",
    "patch": """<rect x="18" y="18" width="64" height="64" rx="10" fill="#caffbf" transform="rotate(8 50 50)"/>
      <path d="M26 30 L34 26 M36 22 L44 20 M70 74 L78 70 M24 66 L22 74" stroke-width="3"/>
      <path d="M38 50 H62 M50 38 V62" stroke="#ff6b6b" stroke-width="7"/>""",
    "signal": """<circle cx="50" cy="70" r="8" fill="#ff8fab"/><path d="M34 56 A22 22 0 0 1 66 56 M24 44 A36 36 0 0 1 76 44 M14 32 A50 50 0 0 1 86 32"
      fill="none" stroke="#7cc6fe" stroke-width="7"/>""",
    "chip": """<rect x="24" y="24" width="52" height="52" rx="6" fill="#80ed99"/>
      <path d="M34 24 V12 M50 24 V12 M66 24 V12 M34 76 V88 M50 76 V88 M66 76 V88 M24 34 H12 M24 50 H12 M24 66 H12 M76 34 H88 M76 50 H88 M76 66 H88" stroke-width="4"/>
      <rect x="36" y="36" width="28" height="28" rx="3" fill="#ffffff"/>""",
    "gear": """<path d="M44 8 H56 L58 20 L68 24 L78 16 L86 24 L78 34 L82 44 L94 46 V56 L82 58 L78 68 L86 78 L78 86 L68 78 L58 82 L56 94 H44 L42 82 L32 78 L22 86 L14 78 L22 68 L18 58 L6 56 V46 L18 44 L22 34 L14 24 L22 16 L32 24 L42 20 Z" fill="#bdb2ff"/>
      <circle cx="50" cy="51" r="14" fill="#ffffff"/>""",
    "magnifier": """<circle cx="42" cy="42" r="26" fill="#e0f7ff"/><path d="M60 60 L86 86" stroke-width="12"/><path d="M60 60 L86 86" stroke="#ffadad" stroke-width="5"/>
      <text x="42" y="50" font-family="monospace" font-weight="bold" font-size="22" text-anchor="middle" fill="#4a3d6b" stroke="none">.*</text>""",
    "pin": """<path d="M50 54 L50 92" stroke-width="6"/><circle cx="50" cy="34" r="24" fill="#ff8fab"/><circle cx="42" cy="26" r="7" fill="#ffffff" stroke="none"/>""",
    "lightning": """<path d="M56 6 L22 56 H46 L38 94 L80 38 H56 L66 6 Z" fill="#ffd166"/>""",
    "cpu": """<rect x="20" y="20" width="60" height="60" rx="6" fill="#a0c4ff"/>
      <path d="M32 20 V10 M44 20 V10 M56 20 V10 M68 20 V10 M32 80 V90 M44 80 V90 M56 80 V90 M68 80 V90 M20 32 H10 M20 44 H10 M20 56 H10 M20 68 H10 M80 32 H90 M80 44 H90 M80 56 H90 M80 68 H90" stroke-width="4"/>
      <g fill="#ffffff" stroke-width="3"><rect x="30" y="30" width="16" height="16" rx="2"/><rect x="54" y="30" width="16" height="16" rx="2"/>
      <rect x="30" y="54" width="16" height="16" rx="2"/><rect x="54" y="54" width="16" height="16" rx="2"/></g>""",
    "bits": """<g font-family="monospace" font-weight="bold" font-size="30" fill="#4a3d6b" stroke="none" text-anchor="middle">
      <text x="28" y="40">1</text><text x="72" y="40" fill="#ff6b6b">0</text><text x="28" y="82" fill="#ff6b6b">0</text><text x="72" y="82">1</text></g>
      <path d="M46 30 Q62 18 66 34 M54 70 Q38 82 34 66" fill="none" stroke="#7cc6fe" stroke-width="5"/>""",
    "disk": """<rect x="14" y="20" width="72" height="60" rx="8" fill="#c9b6f2"/><circle cx="50" cy="50" r="20" fill="#ffffff"/>
      <circle cx="50" cy="50" r="5" fill="#4a3d6b"/><path d="M54 52 L76 70" stroke-width="5"/><circle cx="76" cy="28" r="3" fill="#80ed99" stroke="none"/>""",
    "alarm": """<circle cx="50" cy="54" r="32" fill="#ff8fab"/><circle cx="50" cy="54" r="24" fill="#ffffff"/>
      <path d="M50 38 V56 L60 62" fill="none" stroke-width="5"/><path d="M14 26 L28 14 M86 26 L72 14" stroke-width="7"/>
      <text x="50" y="14" font-family="sans-serif" font-weight="bold" font-size="16" text-anchor="middle" fill="#ff4d6d" stroke="none">!!</text>""",
    "battery": """<rect x="14" y="30" width="64" height="40" rx="6" fill="#ffffff"/><rect x="78" y="42" width="8" height="16" rx="2" fill="#4a3d6b"/>
      <rect x="20" y="36" width="44" height="28" rx="3" fill="#80ed99" stroke="none"/><path d="M48 32 L36 52 H50 L42 70" fill="none" stroke="#ffd166" stroke-width="6"/>
      <path d="M48 32 L36 52 H50 L42 70" fill="none" stroke-width="2"/>""",
    "music": """<path d="M38 72 V22 L80 14 V64" fill="none" stroke-width="7"/><ellipse cx="30" cy="74" rx="12" ry="9" fill="#ff8fab"/>
      <ellipse cx="72" cy="66" rx="12" ry="9" fill="#9bf6ff"/><path d="M38 34 L80 26" stroke-width="7"/>""",
    "scales": """<path d="M50 14 V86 M30 86 H70 M18 28 H82" stroke-width="6"/><circle cx="50" cy="14" r="6" fill="#ffd166"/>
      <path d="M18 28 L8 56 H28 Z M82 28 L72 56 H92 Z" fill="none" stroke-width="3"/>
      <path d="M6 56 Q18 70 30 56 Z M70 56 Q82 70 94 56 Z" fill="#ffd166"/>""",
    "ram": """<rect x="8" y="34" width="84" height="30" rx="4" fill="#80ed99"/>
      <g fill="#4a3d6b" stroke="none"><rect x="16" y="40" width="12" height="16" rx="2"/><rect x="34" y="40" width="12" height="16" rx="2"/>
      <rect x="54" y="40" width="12" height="16" rx="2"/><rect x="72" y="40" width="12" height="16" rx="2"/></g>
      <path d="M14 64 V72 M22 64 V72 M30 64 V72 M38 64 V72 M46 64 V72 M58 64 V72 M66 64 V72 M74 64 V72 M82 64 V72" stroke="#ffd166" stroke-width="4"/>""",
    "book": """<path d="M50 24 Q30 12 10 20 V82 Q30 74 50 86 Q70 74 90 82 V20 Q70 12 50 24 Z" fill="#ffffff"/>
      <path d="M50 24 V86" stroke-width="4"/><path d="M18 34 Q30 30 42 36 M18 48 Q30 44 42 50 M58 36 Q70 30 82 34 M58 50 Q70 44 82 48" fill="none" stroke="#c9b6f2" stroke-width="4"/>
      <text x="30" y="72" font-family="monospace" font-weight="bold" font-size="14" text-anchor="middle" fill="#ff6b6b" stroke="none">man</text>""",
    "skull": """<path d="M50 12 Q84 12 84 46 Q84 62 72 68 V82 H28 V68 Q16 62 16 46 Q16 12 50 12 Z" fill="#ffffff"/>
      <circle cx="36" cy="46" r="9" fill="#4a3d6b"/><circle cx="64" cy="46" r="9" fill="#4a3d6b"/><path d="M50 56 L45 64 H55 Z" fill="#4a3d6b"/>
      <path d="M40 72 V82 M50 72 V82 M60 72 V82" stroke-width="3"/>""",
    "notebook": """<rect x="20" y="10" width="62" height="80" rx="6" fill="#ffd6a5"/><path d="M14 22 H26 M14 38 H26 M14 54 H26 M14 70 H26" stroke-width="5"/>
      <rect x="34" y="22" width="38" height="18" rx="3" fill="#ffffff" stroke-width="3"/><path d="M36 56 H72 M36 68 H64" stroke-width="4"/>""",
    "ssd": """<rect x="14" y="22" width="72" height="56" rx="6" fill="#4a3d6b"/><rect x="20" y="28" width="60" height="44" rx="3" fill="#bdb2ff" stroke="none"/>
      <text x="50" y="58" font-family="sans-serif" font-weight="bold" font-size="20" text-anchor="middle" fill="#ffffff" stroke="none">SSD</text>
      <path d="M70 14 L60 26 H68 L62 36" fill="none" stroke="#ffd166" stroke-width="4"/>""",
    "bomb": """<circle cx="44" cy="58" r="30" fill="#5a5080"/><circle cx="34" cy="48" r="7" fill="#ffffff" stroke="none" opacity="0.6"/>
      <path d="M62 34 Q70 22 80 22" fill="none" stroke-width="5"/>
      <path d="M80 22 l4 -10 4 10 10 0 -8 6 4 10 -10 -6 -10 6 4 -10 -8 -6 Z" fill="#ffd166" stroke-width="2" transform="translate(-4 2) scale(0.9) translate(10 0)"/>
      <text x="44" y="66" font-family="monospace" font-weight="bold" font-size="16" text-anchor="middle" fill="#ffffff" stroke="none">:(){}</text>""",
    "clock": """<circle cx="50" cy="50" r="38" fill="#ffffff"/><path d="M50 24 V50 L68 60" fill="none" stroke-width="6"/>
      <path d="M50 14 V20 M50 80 V86 M14 50 H20 M80 50 H86" stroke-width="4"/><circle cx="50" cy="50" r="4" fill="#ff8fab"/>""",
    "brackets": """<text x="50" y="68" font-family="monospace" font-weight="bold" font-size="54" text-anchor="middle" fill="#ff8fab" stroke-width="3">{ }</text>
      <circle cx="50" cy="52" r="6" fill="#ffd166"/>""",
    "stack": """<g fill="#a0c4ff"><rect x="16" y="14" width="68" height="18" rx="5"/><rect x="16" y="38" width="68" height="18" rx="5"/>
      <rect x="16" y="62" width="68" height="18" rx="5"/></g><g fill="#80ed99" stroke="none"><circle cx="72" cy="23" r="4"/><circle cx="72" cy="47" r="4"/><circle cx="72" cy="71" r="4"/></g>""",
    "heart": """<path d="M50 86 C14 62 8 42 18 26 C28 12 44 16 50 30 C56 16 72 12 82 26 C92 42 86 62 50 86 Z" fill="#ff8fab"/>
      <path d="M28 34 Q30 26 38 26" fill="none" stroke="#ffffff" stroke-width="5"/>""",
    "rack": """<rect x="12" y="8" width="34" height="84" rx="4" fill="#d0d6f9"/><rect x="54" y="8" width="34" height="84" rx="4" fill="#d0d6f9"/>
      <g stroke-width="3"><path d="M18 22 H40 M18 36 H40 M18 50 H40 M18 64 H40 M18 78 H40 M60 22 H82 M60 36 H82 M60 50 H82 M60 64 H82 M60 78 H82"/></g>
      <g stroke="none"><circle cx="36" cy="29" r="3" fill="#80ed99"/><circle cx="78" cy="43" r="3" fill="#ff8fab"/><circle cx="36" cy="57" r="3" fill="#ffd166"/><circle cx="78" cy="71" r="3" fill="#80ed99"/></g>""",
    "camera": """<rect x="10" y="28" width="80" height="54" rx="8" fill="#bdb2ff"/><path d="M34 28 L40 16 H60 L66 28" fill="#bdb2ff"/>
      <circle cx="50" cy="55" r="17" fill="#ffffff"/><circle cx="50" cy="55" r="8" fill="#7cc6fe"/><circle cx="78" cy="38" r="4" fill="#ffd166"/>""",
    "flame": """<path d="M50 6 Q74 30 74 56 Q74 88 50 92 Q26 88 26 58 Q26 40 40 26 Q42 42 50 44 Q46 22 50 6 Z" fill="#ff9f7a"/>
      <path d="M50 52 Q62 64 60 76 Q58 86 50 86 Q42 86 40 76 Q40 64 50 52 Z" fill="#ffd166" stroke-width="3"/>""",
    "igloo": """<path d="M8 84 A42 42 0 0 1 92 84 Z" fill="#e0f2ff"/><path d="M16 64 H84 M26 46 H74 M30 84 V64 M60 84 V64 M42 64 V46 M66 64 V46 M50 46 V34 M30 46 V58" stroke="#a0c4ff" stroke-width="3"/>
      <path d="M38 84 V72 Q50 58 62 72 V84 Z" fill="#4a3d6b"/><path d="M50 42 V18 L66 24 L50 30" fill="#ff8fab" stroke-width="3"/>""",
    "container": """<rect x="8" y="28" width="84" height="48" rx="4" fill="#7cc6fe"/>
      <path d="M22 34 V70 M36 34 V70 M50 34 V70 M64 34 V70 M78 34 V70" stroke-width="3"/>
      <path d="M20 28 Q24 18 30 22 Q34 12 40 20 M60 28 Q66 18 72 24" fill="none" stroke-width="3"/><path d="M4 82 Q20 74 36 82 Q52 90 68 82 Q84 74 96 82" fill="none" stroke="#7cc6fe" stroke-width="5"/>""",
    "gift": """<rect x="16" y="40" width="68" height="48" rx="4" fill="#ff8fab"/><rect x="10" y="30" width="80" height="16" rx="4" fill="#ffadad"/>
      <path d="M50 30 V88" stroke="#ffd166" stroke-width="10"/><path d="M50 30 V88" stroke-width="2"/>
      <path d="M50 30 Q34 6 26 22 Q30 32 50 30 Q66 6 74 22 Q70 32 50 30 Z" fill="#ffd166"/>""",
    "rainbow": """<g fill="none" stroke-width="9"><path d="M12 80 A38 38 0 0 1 88 80" stroke="#ff8fab"/><path d="M22 80 A28 28 0 0 1 78 80" stroke="#ffd166"/>
      <path d="M32 80 A18 18 0 0 1 68 80" stroke="#80ed99"/></g><path d="M4 82 Q12 70 22 80 Q30 72 36 82 Z M64 82 Q70 72 78 80 Q88 70 96 82 Z" fill="#ffffff"/>""",
    "wrench": """<path d="M66 8 Q86 10 88 30 L76 32 L68 24 L70 12 Z" fill="#c9b6f2"/>
      <path d="M70 12 Q52 14 54 34 L14 74 Q12 84 22 88 Q30 88 64 48 Q84 50 88 30 L76 32 L68 24 Z" fill="#c9b6f2"/><circle cx="22" cy="80" r="4" fill="#ffffff"/>""",
    "key": """<circle cx="30" cy="40" r="20" fill="#ffd166"/><circle cx="26" cy="36" r="7" fill="#ffffff"/>
      <path d="M44 54 L84 88 M66 72 L74 64 M76 82 L84 74" stroke-width="8"/><path d="M44 54 L84 88" stroke="#ffd166" stroke-width="3"/>""",
    "party": """<path d="M14 90 L36 30 L72 66 Z" fill="#bdb2ff"/><path d="M24 64 L46 74 M30 48 L58 62" stroke="#ffd166" stroke-width="5"/>
      <g stroke="none"><circle cx="60" cy="18" r="5" fill="#ff8fab"/><circle cx="82" cy="34" r="5" fill="#80ed99"/><circle cx="78" cy="12" r="4" fill="#7cc6fe"/></g>
      <path d="M48 26 Q56 14 50 6 M70 46 Q82 46 90 52" fill="none" stroke-width="3"/>""",
    "fishbone": """<path d="M14 50 L30 36 V64 Z" fill="#ffffff"/><path d="M30 50 H76" stroke-width="5"/>
      <path d="M40 36 V64 M52 34 V66 M64 36 V64" stroke-width="4"/><path d="M76 50 Q78 34 92 40 Q96 50 92 60 Q78 66 76 50 Z" fill="#ffffff"/>
      <path d="M84 46 L88 50 M88 46 L84 50" stroke-width="2.5"/>""",
    "penguin": """@PENGUIN@""",
    "troll": """<path d="M20 40 Q20 12 50 12 Q80 12 80 40 V70 Q80 90 50 90 Q20 90 20 70 Z" fill="#95d5b2"/>
      <path d="M20 30 L8 18 M80 30 L92 18" stroke-width="5"/><circle cx="38" cy="42" r="6" fill="#ffffff"/><circle cx="62" cy="42" r="6" fill="#ffffff"/>
      <circle cx="38" cy="44" r="2.5" fill="#4a3d6b"/><circle cx="62" cy="44" r="2.5" fill="#4a3d6b"/><path d="M30 32 L44 36 M70 32 L56 36" stroke-width="4"/>
      <path d="M36 70 Q50 60 64 70" fill="none" stroke-width="4"/><path d="M40 68 L42 74 L44 66" fill="#ffffff" stroke-width="2"/>""",
    "egg": """<path d="M50 10 Q78 12 80 54 Q80 88 50 88 Q20 88 20 54 Q22 12 50 10 Z" fill="#fff4d6"/>
      <path d="M22 54 L32 46 L42 56 L52 44 L62 56 L72 46 L80 54" fill="none" stroke-width="4"/>
      <circle cx="40" cy="30" r="4" fill="#c9b6f2" stroke="none"/><circle cx="60" cy="72" r="5" fill="#9bf6ff" stroke="none"/>""",
    "binoculars": """<circle cx="30" cy="62" r="20" fill="#bdb2ff"/><circle cx="70" cy="62" r="20" fill="#bdb2ff"/>
      <circle cx="30" cy="62" r="10" fill="#9bf6ff"/><circle cx="70" cy="62" r="10" fill="#9bf6ff"/>
      <rect x="20" y="22" width="20" height="26" rx="4" fill="#5a5080"/><rect x="60" y="22" width="20" height="26" rx="4" fill="#5a5080"/><rect x="40" y="34" width="20" height="12" fill="#5a5080"/>""",
    "mail": """<rect x="10" y="24" width="80" height="54" rx="6" fill="#ffffff"/><path d="M10 28 L50 56 L90 28" fill="none" stroke-width="4"/>
      <circle cx="80" cy="24" r="12" fill="#ff6b6b"/><text x="80" y="30" font-family="sans-serif" font-weight="bold" font-size="16" text-anchor="middle" fill="#ffffff" stroke="none">99</text>""",
    "snowball": """<circle cx="46" cy="54" r="30" fill="#ffffff"/><circle cx="36" cy="44" r="6" fill="#e0f2ff" stroke="none"/><circle cx="56" cy="64" r="8" fill="#e0f2ff" stroke="none"/>
      <path d="M82 22 L90 14 M84 34 L94 34 M72 16 L74 6" stroke="#7cc6fe" stroke-width="5"/>""",
    "ghost": """<path d="M22 86 V44 Q22 12 50 12 Q78 12 78 44 V86 L68 78 L59 86 L50 78 L41 86 L32 78 Z" fill="#e0d7ff"/>
      <ellipse cx="40" cy="42" rx="5" ry="8" fill="#4a3d6b"/><ellipse cx="60" cy="42" rx="5" ry="8" fill="#4a3d6b"/>
      <path d="M44 60 Q50 66 56 60" fill="none" stroke-width="4"/>""",
    "bug": """<ellipse cx="50" cy="58" rx="24" ry="30" fill="#ff8fab"/><circle cx="50" cy="26" r="12" fill="#5a5080"/>
      <path d="M50 30 V88" stroke-width="3"/><path d="M26 46 L10 38 M26 60 H8 M28 74 L12 84 M74 46 L90 38 M74 60 H92 M72 74 L88 84 M44 16 L36 6 M56 16 L64 6" stroke-width="4"/>
      <circle cx="40" cy="52" r="5" fill="#5a5080" stroke="none"/><circle cx="60" cy="70" r="5" fill="#5a5080" stroke="none"/>""",
    "walrus": """<path d="M14 70 Q14 26 50 26 Q86 26 86 70 Q86 88 50 88 Q14 88 14 70 Z" fill="#d4a373"/>
      <circle cx="38" cy="46" r="4" fill="#4a3d6b"/><circle cx="62" cy="46" r="4" fill="#4a3d6b"/>
      <ellipse cx="42" cy="62" rx="10" ry="8" fill="#e9c46a"/><ellipse cx="58" cy="62" rx="10" ry="8" fill="#e9c46a"/>
      <path d="M40 68 L38 90 L46 70 M60 68 L62 90 L54 70" fill="#ffffff" stroke-width="3"/>""",
    "snake": """<path d="M14 80 Q30 60 46 74 Q62 88 74 70 Q86 52 66 42 Q46 32 58 18" fill="none" stroke="#80ed99" stroke-width="14"/>
      <path d="M14 80 Q30 60 46 74 Q62 88 74 70 Q86 52 66 42 Q46 32 58 18" fill="none" stroke-width="2.5"/>
      <circle cx="60" cy="14" r="10" fill="#80ed99"/><circle cx="63" cy="11" r="2.5" fill="#4a3d6b" stroke="none"/><path d="M70 14 L80 12 M78 12 L82 8 M78 12 L82 16" stroke="#ff6b6b" stroke-width="2.5"/>""",
    "nest": """<path d="M10 56 Q50 98 90 56 Z" fill="#d4a373"/><path d="M14 62 L86 62 M20 72 L80 70 M30 82 L70 80" stroke-width="3"/>
      <ellipse cx="38" cy="50" rx="11" ry="14" fill="#fff4d6"/><ellipse cx="60" cy="48" rx="11" ry="14" fill="#e0f2ff"/>
      <ellipse cx="50" cy="56" rx="10" ry="12" fill="#ffe0f0"/>""",
    "gnome": """<path d="M28 50 L50 6 L72 50 Z" fill="#ff6b6b"/><circle cx="50" cy="56" r="14" fill="#ffd6a5"/>
      <path d="M30 60 Q50 98 70 60 Q60 70 50 66 Q40 70 30 60 Z" fill="#ffffff"/><circle cx="50" cy="60" r="5" fill="#ffadad"/>
      <circle cx="43" cy="52" r="2.5" fill="#4a3d6b" stroke="none"/><circle cx="57" cy="52" r="2.5" fill="#4a3d6b" stroke="none"/>""",
    "pizza": """<path d="M50 90 L14 22 Q50 6 86 22 Z" fill="#ffd166"/><path d="M14 22 Q50 6 86 22 L82 30 Q50 16 18 30 Z" fill="#d4a373"/>
      <circle cx="44" cy="40" r="6" fill="#ff6b6b"/><circle cx="60" cy="52" r="6" fill="#ff6b6b"/><circle cx="48" cy="66" r="5" fill="#ff6b6b"/>""",
    "skate": """<path d="M20 20 H52 V54 Q80 54 84 70 H18 Z" fill="#ffffff"/><path d="M26 30 H46 M26 40 H46" stroke-width="3"/>
      <path d="M10 82 H90 Q94 82 92 76" fill="none" stroke="#7cc6fe" stroke-width="6"/><path d="M30 70 V82 M70 70 V82" stroke-width="4"/>""",
    "seal": """<path d="M12 78 Q16 46 44 42 Q52 22 70 22 Q88 22 88 40 Q88 54 70 56 Q66 80 40 84 Q20 86 12 78 Z" fill="#b8c0ff"/>
      <circle cx="68" cy="36" r="4" fill="#4a3d6b"/><circle cx="82" cy="40" r="3" fill="#4a3d6b"/>
      <path d="M78 46 Q72 52 64 48" fill="none" stroke-width="3"/><path d="M30 60 Q34 68 28 74" fill="none" stroke-width="3"/>
      <g fill="#7a85d8" stroke="none"><circle cx="40" cy="62" r="3"/><circle cx="52" cy="70" r="3"/><circle cx="34" cy="74" r="2.5"/></g>""",
    "horns": """<path d="M24 44 Q6 30 10 10 Q24 28 36 30 M76 44 Q94 30 90 10 Q76 28 64 30" fill="#fff4d6"/>
      <path d="M26 36 Q26 20 50 20 Q74 20 74 36 L68 76 Q50 92 32 76 Z" fill="#b5835a"/>
      <circle cx="40" cy="44" r="5" fill="#ffffff"/><circle cx="60" cy="44" r="5" fill="#ffffff"/><circle cx="40" cy="46" r="2" fill="#4a3d6b" stroke="none"/>
      <circle cx="60" cy="46" r="2" fill="#4a3d6b" stroke="none"/><path d="M32 36 L46 40 M68 36 L54 40" stroke-width="4"/>
      <ellipse cx="50" cy="70" rx="12" ry="8" fill="#d4a373"/>""",
    "hoodie": """<path d="M22 90 V50 Q22 14 50 14 Q78 14 78 50 V90 Z" fill="#5a5080"/><path d="M32 54 Q32 28 50 28 Q68 28 68 54 Q68 70 50 70 Q32 70 32 54 Z" fill="#2b2540"/>
      <g fill="#80ed99" stroke="none"><rect x="40" y="46" width="6" height="4"/><rect x="54" y="46" width="6" height="4"/></g>
      <text x="50" y="86" font-family="monospace" font-weight="bold" font-size="12" text-anchor="middle" fill="#80ed99" stroke="none">1337</text>""",
    "radar": """<circle cx="50" cy="50" r="38" fill="#caffbf"/><circle cx="50" cy="50" r="24" fill="none" stroke-width="3"/><circle cx="50" cy="50" r="10" fill="none" stroke-width="3"/>
      <path d="M50 50 L78 24" stroke-width="5"/><path d="M50 50 L78 24 A38 38 0 0 1 88 50 Z" fill="#80ed99" stroke="none" opacity="0.8"/>
      <circle cx="66" cy="62" r="4" fill="#ff6b6b"/><circle cx="30" cy="36" r="3" fill="#ff6b6b"/>""",
    "bear": """<circle cx="28" cy="26" r="11" fill="#ffffff"/><circle cx="72" cy="26" r="11" fill="#ffffff"/>
      <path d="M50 18 Q86 18 86 54 Q86 88 50 88 Q14 88 14 54 Q14 18 50 18 Z" fill="#ffffff"/>
      <circle cx="38" cy="48" r="4" fill="#4a3d6b"/><circle cx="62" cy="48" r="4" fill="#4a3d6b"/>
      <ellipse cx="50" cy="66" rx="14" ry="11" fill="#f1f5ff"/><ellipse cx="50" cy="61" rx="6" ry="4" fill="#4a3d6b"/>""",
    "mask": """<path d="M8 36 Q50 22 92 36 Q92 70 64 70 Q56 70 50 60 Q44 70 36 70 Q8 70 8 36 Z" fill="#5a5080"/>
      <ellipse cx="32" cy="46" rx="10" ry="7" fill="#ffffff"/><ellipse cx="68" cy="46" rx="10" ry="7" fill="#ffffff"/>
      <text x="50" y="92" font-family="monospace" font-weight="bold" font-size="16" text-anchor="middle" fill="#ff6b6b" stroke="none">#root</text>""",
    "narwhal": """<path d="M10 66 Q14 40 46 40 Q74 40 78 58 Q80 76 52 80 Q24 82 10 66 Z" fill="#a0c4ff"/>
      <path d="M74 46 L96 18" stroke-width="5"/><path d="M74 46 L96 18" stroke="#fff4d6" stroke-width="2"/>
      <path d="M12 66 L2 56 M12 66 L4 78" stroke-width="5"/><circle cx="62" cy="54" r="4" fill="#4a3d6b"/>
      <path d="M30 70 Q40 76 52 72" fill="none" stroke="#ffffff" stroke-width="4"/>""",
    "target": """<circle cx="50" cy="50" r="38" fill="#ffffff"/><circle cx="50" cy="50" r="28" fill="#ff8fab"/><circle cx="50" cy="50" r="18" fill="#ffffff"/>
      <circle cx="50" cy="50" r="8" fill="#ff8fab"/><circle cx="72" cy="28" r="8" fill="#ffffff" stroke-width="3"/>""",
    "hook": """<path d="M60 8 V58 Q60 82 40 82 Q22 82 22 64 L32 70" fill="none" stroke-width="8"/>
      <path d="M60 8 V58 Q60 82 40 82 Q22 82 22 64" fill="none" stroke="#c9b6f2" stroke-width="3"/>
      <rect x="64" y="22" width="26" height="18" rx="3" fill="#ffffff" stroke-width="3"/><path d="M64 24 L77 32 L90 24" fill="none" stroke-width="2.5"/>""",
    "footprint": """<ellipse cx="38" cy="62" rx="14" ry="20" fill="#e0f2ff"/><ellipse cx="66" cy="34" rx="12" ry="17" fill="#e0f2ff"/>
      <g fill="#e0f2ff"><circle cx="26" cy="36" r="5"/><circle cx="36" cy="32" r="5"/><circle cx="46" cy="34" r="5"/>
      <circle cx="56" cy="10" r="4"/><circle cx="66" cy="8" r="4"/><circle cx="76" cy="10" r="4"/></g>""",
    "nose": """<path d="M50 14 Q60 50 70 62 Q76 72 64 76 Q56 78 50 72 Q44 78 36 76 Q24 72 30 62 Q40 50 50 14 Z" fill="#ffd6a5"/>
      <ellipse cx="42" cy="70" rx="4" ry="3" fill="#4a3d6b"/><ellipse cx="58" cy="70" rx="4" ry="3" fill="#4a3d6b"/>
      <path d="M82 30 Q90 40 82 50 M90 22 Q102 40 90 58" fill="none" stroke="#7cc6fe" stroke-width="4"/>
      <text x="16" y="34" font-family="monospace" font-weight="bold" font-size="14" fill="#4a3d6b" stroke="none">0101</text>""",
    "iceberg": """<path d="M4 58 H96" stroke="#7cc6fe" stroke-width="5"/><path d="M26 58 L40 18 L52 30 L62 14 L76 58 Z" fill="#ffffff"/>
      <path d="M20 58 L80 58 L66 92 L32 92 Z" fill="#a0c4ff" opacity="0.8"/><circle cx="44" cy="44" r="3" fill="#4a3d6b"/><circle cx="58" cy="44" r="3" fill="#4a3d6b"/>
      <path d="M44 52 Q51 48 58 52" fill="none" stroke-width="3"/>""",
    "lock": """<path d="M30 46 V32 Q30 12 50 12 Q70 12 70 32 V46" fill="none" stroke-width="8"/>
      <rect x="18" y="44" width="64" height="46" rx="8" fill="#ffd166"/><circle cx="50" cy="62" r="7" fill="#4a3d6b"/><path d="M50 66 V78" stroke-width="5"/>""",
    "orca": """<path d="M6 60 Q20 30 56 34 Q86 36 94 58 Q74 74 40 72 Q20 72 6 60 Z" fill="#3d3a5c"/>
      <path d="M46 36 L52 10 L62 36" fill="#3d3a5c"/><path d="M40 60 Q60 72 84 60 Q64 66 40 60 Z" fill="#ffffff" stroke="none"/>
      <ellipse cx="72" cy="48" rx="7" ry="4" fill="#ffffff" stroke="none"/><path d="M6 60 L0 48 M6 60 L2 72" stroke-width="5"/>""",
    "spear": """<path d="M20 86 L76 22" stroke="#b5835a" stroke-width="7"/><path d="M76 22 L70 12 L92 8 L88 30 L80 26 Z" fill="#d0d6f9"/>
      <path d="M30 70 L22 64 L18 76 Z" fill="#ff8fab" stroke-width="3"/>""",
    "pup": """<ellipse cx="50" cy="60" rx="34" ry="28" fill="#ffffff"/><circle cx="38" cy="54" r="7" fill="#4a3d6b"/><circle cx="62" cy="54" r="7" fill="#4a3d6b"/>
      <circle cx="40" cy="51" r="2.5" fill="#ffffff" stroke="none"/><circle cx="64" cy="51" r="2.5" fill="#ffffff" stroke="none"/>
      <ellipse cx="50" cy="68" rx="5" ry="3.5" fill="#4a3d6b"/><path d="M30 72 L14 70 M30 76 L16 80 M70 72 L86 70 M70 76 L84 80" stroke-width="2.5"/>""",
    "rocket": """<path d="M50 6 Q72 26 70 62 H30 Q28 26 50 6 Z" fill="#ffffff"/><circle cx="50" cy="36" r="9" fill="#7cc6fe"/>
      <path d="M30 50 L16 70 H30 Z M70 50 L84 70 H70 Z" fill="#ff8fab"/><path d="M38 62 Q50 98 62 62 Z" fill="#ffd166"/>""",
    "crown": """<path d="M12 74 L8 26 L32 46 L50 16 L68 46 L92 26 L88 74 Z" fill="#ffd166"/><rect x="12" y="74" width="76" height="12" rx="4" fill="#ffb627"/>
      <circle cx="50" cy="56" r="7" fill="#ff8fab"/><circle cx="28" cy="62" r="5" fill="#7cc6fe"/><circle cx="72" cy="62" r="5" fill="#80ed99"/>""",
    "bird": """<path d="M6 40 Q30 30 50 50 Q70 30 94 40 Q72 42 58 58 Q50 66 42 58 Q28 42 6 40 Z" fill="#ffffff"/>
      <circle cx="50" cy="54" r="9" fill="#ffffff"/><path d="M50 58 L56 64 L50 66" fill="#ffd166" stroke-width="3"/>
      <path d="M14 70 Q24 64 34 70 M64 76 Q74 70 84 76" fill="none" stroke="#c9b6f2" stroke-width="3"/>""",
}

CATEGORY_STYLE = {
    # gradient top, gradient bottom, pattern colour, pattern glyphs
    "red": ("#ffe1d6", "#ffb8a3", "#ffffff", ["{ }", "&lt;/&gt;", ";", "( )", "#!", "[ ]"]),
    "blue": ("#dfe9ff", "#c4b8ff", "#ffffff", ["0", "1", "01", "10", "0x", "1"]),
    "green": ("#dbf7e6", "#a6e6c8", "#ffffff", ["*", "~", "o", "*", "~", "°"]),
}
ART_W, ART_H = 300, 190


def penguin_glyph() -> str:
    svg = penguin_svg("#3b4060", "#262a40", "bowtie", "happy")
    inner = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return f'<svg x="4" y="0" width="92" height="98" viewBox="0 -8 200 212">{inner}</svg>'


def card_art_svg(card) -> str:
    top, bottom, pcol, chars = CATEGORY_STYLE[card.cat]
    rng = random.Random(card.id)
    pattern = []
    for _ in range(16):
        x, y = rng.uniform(0, ART_W), rng.uniform(10, ART_H - 30)
        ch = rng.choice(chars)
        size = rng.uniform(14, 26)
        rot = rng.uniform(-25, 25)
        pattern.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="monospace" font-weight="bold" font-size="{size:.0f}" '
                       f'fill="{pcol}" opacity="0.55" transform="rotate({rot:.0f} {x:.0f} {y:.0f})">{ch}</text>')
    hills = (f'<path d="M0 {ART_H - 34} Q{ART_W * 0.25:.0f} {ART_H - 58} {ART_W * 0.5:.0f} {ART_H - 38} '
             f'Q{ART_W * 0.75:.0f} {ART_H - 18} {ART_W} {ART_H - 44} V{ART_H} H0 Z" fill="#ffffff" opacity="0.85"/>')
    glyph = GLYPHS[card.icon]
    if "@PENGUIN@" in glyph:
        glyph = penguin_glyph()
    gsize = 150
    gx, gy = (ART_W - gsize) / 2, (ART_H - gsize) / 2 - 2
    scale = gsize / 100
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ART_W} {ART_H}" width="{ART_W}" height="{ART_H}">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>
  <rect width="{ART_W}" height="{ART_H}" fill="url(#bg)"/>
  {''.join(pattern)}
  {hills}
  <ellipse cx="{ART_W / 2}" cy="{gy + gsize - 4}" rx="{gsize * 0.36}" ry="9" fill="#000000" opacity="0.10"/>
  <g transform="translate({gx} {gy}) scale({scale})" stroke="{OUTLINE}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round">
    {glyph}
  </g>
</svg>"""


def app_icon_svg() -> str:
    """Penguin mage in front of a tower: the application icon."""
    peng = penguin_svg("#3b4060", "#262a40", "wizard", "happy").split(">", 1)[1].rsplit("</svg>", 1)[0]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <rect x="8" y="8" width="240" height="240" rx="56" fill="#ffe3f0"/>
  <rect x="8" y="8" width="240" height="240" rx="56" fill="none" stroke="#c9b6f2" stroke-width="8"/>
  <g stroke="{OUTLINE}" stroke-width="5" stroke-linejoin="round">
    <path d="M150 230 V92 H214 V230 Z" fill="#cfe3ff"/><path d="M142 96 L182 46 L222 96 Z" fill="#ff8fab"/>
    <path d="M150 130 H214 M150 166 H214 M150 200 H214 M182 96 V130 M166 130 V166 M198 130 V166 M182 166 V200" stroke-width="3"/>
    <path d="M182 46 V22 L204 30 L182 38" fill="#ffd166" stroke-width="4"/>
  </g>
  <svg x="16" y="40" width="168" height="196" viewBox="0 -8 200 212">{peng}</svg>
</svg>"""


def render(svg: str, out: Path, w=None, h=None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(out), output_width=w, output_height=h)


def main() -> None:
    for d in ("penguins", "icons", "svg", "cardart"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    for pid, body, outline, acc, mood in PENGUINS:
        svg = penguin_svg(body, outline, acc, mood)
        (ROOT / "svg" / f"{pid}.svg").write_text(svg, encoding="utf-8")
        render(svg, ROOT / "penguins" / f"{pid}.png", PNG_SIZE, PNG_SIZE)
    for name, svg in {**BASE_ICONS, **UI_ICONS}.items():
        (ROOT / "svg" / f"{name}.svg").write_text(svg, encoding="utf-8")
        render(svg, ROOT / "icons" / f"{name}.png", 128, 128)
    missing = sorted({c.icon for c in DECK} - set(GLYPHS))
    if missing:
        raise SystemExit(f"missing card glyphs: {missing}")
    for c in DECK:
        render(card_art_svg(c), ROOT / "cardart" / f"{c.id}.png", ART_W, ART_H)
    app = app_icon_svg()
    render(app, ROOT / "icons" / "tuxomage.png", 128, 128)
    data = ROOT.parent.parent / "data" / "icons"
    data.mkdir(parents=True, exist_ok=True)
    (data / "tuxomage.svg").write_text(app, encoding="utf-8")
    for size in (16, 22, 24, 32, 48, 64, 128, 256, 512):
        render(app, data / "hicolor" / f"{size}x{size}" / "apps" / "tuxomage.png", size, size)
    print("assets written to", ROOT)


if __name__ == "__main__":
    main()
