#!/usr/bin/env python3
"""Synthesize all TuxoMage sound effects and music loops from code.

Everything this script produces is original work for TuxoMage, released under
CC0 1.0 (public domain dedication). Requires numpy; music is encoded to OGG
Vorbis with ffmpeg (libvorbis).

    python3 tools/make_sounds.py
"""
from __future__ import annotations

import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parent.parent / "tuxomage" / "assets"
rng = np.random.default_rng(7)


# ------------------------------------------------------------------ basics
def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def t_axis(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def env(n: int, a=0.005, d=0.1, s=0.0, r=0.05, dur=None) -> np.ndarray:
    """Linear attack, exponential-ish decay to sustain, linear release."""
    t = np.arange(n) / SR
    total = n / SR if dur is None else dur
    e = np.ones(n)
    e[t < a] = t[t < a] / max(a, 1e-6)
    after = t >= a
    e[after] = s + (1 - s) * np.exp(-(t[after] - a) / max(d, 1e-6))
    rel_start = max(0.0, total - r)
    rel = t >= rel_start
    e[rel] *= np.clip(1 - (t[rel] - rel_start) / max(r, 1e-6), 0, 1)
    return e


def sine(f, t, phase=0.0):
    return np.sin(2 * np.pi * f * t + phase)


def tri(f, t):
    return 2 * np.abs(2 * ((f * t) % 1.0) - 1) - 1


def soft_square(f, t, harmonics=7):
    out = np.zeros_like(t)
    for k in range(1, harmonics * 2, 2):
        out += np.sin(2 * np.pi * f * k * t) / k
    return out * (4 / np.pi) * 0.6


def sweep(f0, f1, t, curve="exp"):
    dur = t[-1] if len(t) else 1
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / max(dur, 1e-6))
    else:
        f = f0 + (f1 - f0) * t / max(dur, 1e-6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def lowpass(x, alpha=0.2):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def mix_at(buf, sig, start_s):
    i = int(start_s * SR)
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i]


def normalize(x, peak=0.85):
    m = np.max(np.abs(x)) or 1.0
    return x * (peak / m)


# ------------------------------------------------------------ instruments
def bell(midi, dur, vel=1.0):
    t = t_axis(dur)
    f = hz(midi)
    x = sine(f, t) + 0.35 * sine(2 * f, t) * np.exp(-t * 6) + 0.18 * sine(3.01 * f, t) * np.exp(-t * 9)
    return vel * x * env(len(t), a=0.003, d=dur * 0.35, r=min(0.05, dur * 0.3))


def pluck(midi, dur, vel=1.0):
    t = t_axis(dur)
    f = hz(midi)
    x = 0.7 * tri(f, t) + 0.3 * sine(2 * f, t) * np.exp(-t * 8)
    return vel * x * env(len(t), a=0.004, d=dur * 0.45, s=0.0, r=0.04)


def lead(midi, dur, vel=1.0):
    t = t_axis(dur)
    f = hz(midi) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 4, 0, 1))  # gentle vibrato
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    return vel * x * env(len(t), a=0.015, d=0.25, s=0.55, r=min(0.08, dur * 0.4))


def bass(midi, dur, vel=1.0):
    t = t_axis(dur)
    f = hz(midi)
    x = sine(f, t) + 0.25 * sine(2 * f, t) + 0.08 * tri(f, t)
    return vel * x * env(len(t), a=0.006, d=0.22, s=0.35, r=0.05)


def pad(midis, dur, vel=1.0):
    t = t_axis(dur)
    x = np.zeros_like(t)
    for m in midis:
        f = hz(m)
        x += sine(f * 1.002, t) + sine(f * 0.998, t) + 0.2 * sine(2 * f, t)
    x /= max(1, len(midis))
    return vel * x * env(len(t), a=dur * 0.3, d=10, s=1.0, r=dur * 0.35)


def kick(vel=1.0):
    t = t_axis(0.18)
    return vel * sweep(140, 48, t) * env(len(t), a=0.002, d=0.07, r=0.03)


def hat(vel=1.0, dur=0.05):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    hp = noise - lowpass(noise, 0.35)
    return vel * hp * env(n, a=0.001, d=dur * 0.3, r=0.01)


def shaker(vel=1.0):
    n = int(0.09 * SR)
    noise = rng.standard_normal(n)
    hp = noise - lowpass(noise, 0.25)
    return vel * hp * env(n, a=0.02, d=0.03, r=0.02)


# ---------------------------------------------------------------- effects
def noise_burst(dur, alpha=0.3, hp=False):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    lp = lowpass(x, alpha)
    return x - lp if hp else lp


def sfx_click():
    t = t_axis(0.045)
    return 0.5 * sine(1500, t) * env(len(t), a=0.001, d=0.012, r=0.01)


def sfx_hover():
    t = t_axis(0.03)
    return 0.22 * sine(2300, t) * env(len(t), a=0.001, d=0.008, r=0.01)


def sfx_draw():                       # a card slides into the hand
    x = noise_burst(0.16, 0.5, hp=True)
    e = env(len(x), a=0.03, d=0.05, r=0.05)
    t = t_axis(0.16)
    return 0.5 * x * e + 0.15 * sweep(500, 900, t) * e


def sfx_play():                       # whoosh + pop when a card is played
    out = np.zeros(int(0.42 * SR))
    x = noise_burst(0.3, 0.12)
    t = np.arange(len(x)) / SR
    mix_at(out, 1.4 * x * np.sin(np.pi * t / t[-1]) ** 2, 0.0)
    mix_at(out, bell(79, 0.18, 0.5), 0.22)
    mix_at(out, bell(86, 0.2, 0.4), 0.27)
    return out


def sfx_discard():                    # paper flutters away, downward
    out = np.zeros(int(0.4 * SR))
    x = noise_burst(0.28, 0.25, hp=True)
    mix_at(out, 0.6 * x * env(len(x), a=0.02, d=0.1, r=0.06), 0.0)
    t = t_axis(0.3)
    mix_at(out, 0.35 * sweep(700, 260, t) * env(len(t), a=0.01, d=0.12, r=0.05), 0.04)
    return out


def sfx_build():                      # bricks stacking: three wooden clunks going up
    out = np.zeros(int(0.5 * SR))
    for i, f in enumerate((180, 230, 290)):
        t = t_axis(0.12)
        knock = (sine(f, t) + 0.5 * sine(f * 2.7, t)) * env(len(t), a=0.002, d=0.03, r=0.02)
        mix_at(out, 0.7 * knock + 0.25 * noise_burst(0.12, 0.4) * env(len(t), a=0.001, d=0.015, r=0.02), i * 0.1)
    return out


def sfx_tower():                      # magic chime rising up the tower
    out = np.zeros(int(0.8 * SR))
    for i, m in enumerate((76, 79, 83, 88, 91)):
        mix_at(out, bell(m, 0.4, 0.45), i * 0.06)
    t = t_axis(0.5)
    mix_at(out, 0.12 * sweep(800, 2400, t) * env(len(t), a=0.05, d=0.2, r=0.1), 0.05)
    return out


def sfx_damage():                     # snowball thud + ice crack
    out = np.zeros(int(0.55 * SR))
    t = t_axis(0.3)
    mix_at(out, 0.9 * sweep(160, 45, t) * env(len(t), a=0.002, d=0.09, r=0.05), 0.0)
    mix_at(out, 0.6 * noise_burst(0.3, 0.25) * env(len(t), a=0.001, d=0.06, r=0.05), 0.0)
    crack = noise_burst(0.2, 0.6, hp=True)
    mix_at(out, 0.5 * crack * env(len(crack), a=0.001, d=0.03, r=0.04), 0.08)
    return out


def sfx_resource():                   # coin-like double blip (production, resource gain)
    out = np.zeros(int(0.25 * SR))
    mix_at(out, bell(88, 0.1, 0.5), 0.0)
    mix_at(out, bell(95, 0.14, 0.5), 0.06)
    return out


def sfx_turn():                       # gentle "your turn" chime
    out = np.zeros(int(0.6 * SR))
    mix_at(out, bell(72, 0.4, 0.4), 0.0)
    mix_at(out, bell(79, 0.45, 0.35), 0.12)
    return out


def sfx_denied():                     # cannot afford that card
    t = t_axis(0.22)
    x = soft_square(150, t, 4) * env(len(t), a=0.005, d=0.1, s=0.3, r=0.05)
    return 0.5 * x


def sfx_victory():
    out = np.zeros(int(2.4 * SR))
    notes = [(67, 0.0, 0.14), (72, 0.12, 0.14), (76, 0.24, 0.14), (79, 0.36, 0.3),
             (76, 0.62, 0.12), (79, 0.74, 0.12), (84, 0.86, 0.95)]
    for m, st, d in notes:
        mix_at(out, lead(m, d + 0.1, 0.5), st)
        mix_at(out, bell(m + 12, d + 0.3, 0.25), st)
    mix_at(out, pad([60, 64, 67, 72], 1.5, 0.35), 0.86)
    for st, m in ((0.0, 48), (0.36, 43), (0.86, 48)):
        mix_at(out, bass(m, 0.45, 0.5), st)
        mix_at(out, kick(0.5), st)
    for i in range(16):
        mix_at(out, bell(96 + rng.integers(0, 12), 0.15, 0.12), 0.9 + i * 0.06)
    return out


def sfx_defeat():
    out = np.zeros(int(2.0 * SR))
    for i, m in enumerate((69, 67, 65)):
        mix_at(out, lead(m, 0.34, 0.5), i * 0.36)
    t = t_axis(0.85)
    f = hz(64) * (1 - 0.06 * t / t[-1]) * (1 + 0.025 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * env(len(t), a=0.02, d=0.6, s=0.4, r=0.2)
    mix_at(out, 0.5 * x, 1.08)
    mix_at(out, bass(40, 0.9, 0.35), 1.08)
    return out


SFX_LEVEL = {"hover": 0.22, "click": 0.4, "draw": 0.35, "play": 0.6, "discard": 0.5, "build": 0.6,
             "tower": 0.6, "damage": 0.75, "resource": 0.35, "turn": 0.45, "denied": 0.5,
             "victory": 0.8, "defeat": 0.75}
SFX = {"click": sfx_click, "hover": sfx_hover, "draw": sfx_draw, "play": sfx_play, "discard": sfx_discard,
       "build": sfx_build, "tower": sfx_tower, "damage": sfx_damage, "resource": sfx_resource, "turn": sfx_turn,
       "denied": sfx_denied, "victory": sfx_victory, "defeat": sfx_defeat}


# ------------------------------------------------------------------- music
CHORD_TONES = {  # chord name -> (root midi in octave 3, triad intervals)
    "C": (48, (0, 4, 7)), "Am": (45, (0, 3, 7)), "F": (41, (0, 4, 7)), "G": (43, (0, 4, 7)),
    "Dm": (50, (0, 3, 7)), "Em": (52, (0, 3, 7)), "Bb": (46, (0, 4, 7)), "Gm": (43, (0, 3, 7)),
    "D": (50, (0, 4, 7)), "A": (45, (0, 4, 7)), "Bm": (47, (0, 3, 7)),
}


def chord_notes(name, octave_shift=0):
    root, iv = CHORD_TONES[name]
    return [root + 12 * octave_shift + i for i in iv]


def render_loop(bars, bpm, render_bar, echo=0.22):
    beat = 60.0 / bpm
    bar_len = 4 * beat
    total = bars * bar_len
    n = int(round(total * SR))
    buf = np.zeros(n + int(4 * SR))
    for b in range(bars):
        render_bar(buf, b, b * bar_len, beat)
    d = int(0.75 * beat * SR)
    wet = np.zeros_like(buf)
    wet[d:] += buf[:-d] * echo
    wet[2 * d:] += buf[:-2 * d] * echo * echo
    buf = buf + wet
    loop = buf[:n].copy()
    tail = buf[n:]
    k = min(len(tail), n)
    loop[:k] += tail[:k]
    return normalize(loop, 0.8)


def make_melody(chords, bars, scale, seed, rest_bars=(), start=74):
    g = np.random.default_rng(seed)
    mel, cur = [], start
    for b in range(bars):
        tones = {(n % 12) for n in chord_notes(chords[b % len(chords)])}
        if b in rest_bars:
            mel.append([(None, 8)])
            continue
        pattern = [[2, 1, 1, 2, 2], [3, 1, 4], [2, 2, 2, 2], [1, 1, 2, 4], [4, 2, 2], [2, 1, 1, 4]][g.integers(0, 6)]
        if b % 4 == 3:
            pattern = [2, 2, 4]
        notes = []
        for i, length in enumerate(pattern):
            cands = [n for n in scale if abs(n - cur) <= 5 and n != cur] or scale
            if i == 0 or length >= 4:
                cands = [n for n in cands if n % 12 in tones] or cands
            cur = int(g.choice(cands))
            notes.append((cur, length))
        if b % 8 == 7:
            notes[-1] = (None, notes[-1][1])
        mel.append(notes)
    return mel


# "Pingvinvarázs" – menu theme, D major, bouncy
MENU_CHORDS = ["D", "Bm", "G", "A", "D", "Bm", "Em", "A", "G", "A", "Bm", "G", "Em", "A", "D", "A"]
MENU_MELODY = make_melody(MENU_CHORDS, 16, [69, 71, 73, 74, 76, 78, 79, 81, 83, 85, 86], seed=11, start=78)


def menu_bar(buf, b, start, beat):
    tones = chord_notes(MENU_CHORDS[b])
    e = beat / 2
    for i, m in enumerate((tones[0], tones[0] + 7, tones[0] + 12, tones[0] + 7)):
        mix_at(buf, bass(m - 12 if m > 52 else m, beat * 0.9, 0.55), start + i * beat)
    arp = [tones[0] + 24, tones[2] + 24, tones[1] + 24, tones[2] + 24] * 2
    for i, m in enumerate(arp):
        mix_at(buf, bell(m, e * 1.6, 0.18 if i % 2 else 0.24), start + i * e)
    pos = 0
    for m, length in MENU_MELODY[b]:
        if m is not None:
            mix_at(buf, lead(m, length * e * 0.95, 0.32), start + pos * e)
            mix_at(buf, bell(m + 12, length * e, 0.07), start + pos * e)
        pos += length
    for i in range(4):
        mix_at(buf, kick(0.35 if i % 2 == 0 else 0.2), start + i * beat)
        mix_at(buf, shaker(0.08), start + i * beat + e)
    if b % 4 == 3:
        mix_at(buf, hat(0.1, 0.12), start + 3.5 * beat)


# "Tornyok a jégen" – gameplay loop, A minor / C major, calm and thoughtful
GAME_CHORDS = ["Am", "F", "C", "G", "Am", "Dm", "Em", "Am", "F", "G", "C", "Am", "Dm", "G", "C", "G"]
GAME_MELODY = make_melody(GAME_CHORDS, 32, [64, 65, 67, 69, 71, 72, 74, 76, 77, 79], seed=23,
                          rest_bars=(0, 1, 16), start=72)


def game_bar(buf, b, start, beat):
    tones = chord_notes(GAME_CHORDS[b % len(GAME_CHORDS)])
    e = beat / 2
    mix_at(buf, pad([t + 12 for t in tones], 4 * beat + 0.3, 0.15), start)
    mix_at(buf, bass(tones[0], beat * 1.8, 0.45), start)
    mix_at(buf, bass(tones[0] + 7 if tones[0] + 7 < 56 else tones[0] - 5, beat * 1.8, 0.35), start + 2 * beat)
    patt = [0, 1, 2, 1, 0, 1, 2, 1] if b % 2 == 0 else [0, 2, 1, 2, 0, 2, 1, 0]
    for i, k in enumerate(patt):
        mix_at(buf, pluck(tones[k] + 24, e * 1.8, 0.19 if i % 2 == 0 else 0.12), start + i * e)
    pos = 0
    for m, length in GAME_MELODY[b]:
        if m is not None:
            mix_at(buf, bell(m, length * e * 1.1, 0.26), start + pos * e)
        pos += length
    for i in range(4):
        mix_at(buf, shaker(0.045 if i % 2 else 0.03), start + i * beat + e)
    if b % 2 == 1:
        mix_at(buf, kick(0.16), start)


# --------------------------------------------------------------------- io
def write_wav(path: Path, x: np.ndarray):
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def write_ogg(path: Path, x: np.ndarray, quality=3):
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "tmp.wav"
        write_wav(wav, x)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis",
                        "-q:a", str(quality), "-metadata", "title=" + path.stem,
                        "-metadata", "artist=TuxoMage", "-metadata", "copyright=CC0 1.0", str(path)], check=True)


def main():
    (ROOT / "sounds").mkdir(parents=True, exist_ok=True)
    (ROOT / "music").mkdir(parents=True, exist_ok=True)
    for name, fn in SFX.items():
        x = fn()
        fade = min(len(x), int(0.01 * SR))
        x[-fade:] *= np.linspace(1, 0, fade)
        write_wav(ROOT / "sounds" / f"{name}.wav", normalize(x, SFX_LEVEL[name]))
    write_ogg(ROOT / "music" / "menu.ogg", render_loop(len(MENU_CHORDS), 112, menu_bar))
    write_ogg(ROOT / "music" / "game.ogg", render_loop(32, 84, game_bar, echo=0.28))
    print("sounds written to", ROOT)


if __name__ == "__main__":
    main()
