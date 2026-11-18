"""Persist settings, statistics and the best games as JSON.

Location: $TUXOMAGE_DATA_DIR, else $XDG_DATA_HOME/tuxomage, else ~/.local/share/tuxomage
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

MAX_HIGHSCORES = 10
DIFFS = ("easy", "normal", "hard")


def data_dir() -> Path:
    env = os.environ.get("TUXOMAGE_DATA_DIR")
    if env:
        return Path(env)
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "tuxomage"


def _empty_stats() -> dict:
    return {"played": 0, "won": 0, "lost": 0, "draw": 0, "streak": 0, "best_streak": 0, "fastest_win": 0}


def default_save() -> dict:
    return {
        "version": 1,
        "stats": {d: _empty_stats() for d in DIFFS},
        "highscores": [],        # [{"score", "difficulty", "preset", "turns", "reason", "date"}]
        "settings": {"lang": "hu", "fullscreen": False, "music_volume": 0.5, "sfx_volume": 0.8,
                     "music_muted": False, "sfx_muted": False, "difficulty": "normal", "preset": "classic",
                     "first": "player", "ai_speed": "normal"},
    }


class Store:
    def __init__(self, path: Path | None = None):
        self.path = path or data_dir() / "save.json"
        self.data = default_save()
        self.load()

    def load(self) -> None:
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(loaded, dict):
            return
        base = default_save()
        base["settings"].update(loaded.get("settings") or {})
        for d in DIFFS:
            base["stats"][d].update(((loaded.get("stats") or {}).get(d)) or {})
        if isinstance(loaded.get("highscores"), list):
            base["highscores"] = loaded["highscores"][:MAX_HIGHSCORES]
        self.data = base

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
            tmp.replace(self.path)
        except OSError:
            pass

    @property
    def settings(self) -> dict:
        return self.data["settings"]

    def record_game(self, difficulty: str, result: str, score: int, turns: int, preset: str, reason: str) -> bool:
        """result: "won" | "lost" | "draw".  Returns True if the score entered the top list."""
        st = self.data["stats"].setdefault(difficulty, _empty_stats())
        st["played"] += 1
        st[result] = st.get(result, 0) + 1
        if result == "won":
            st["streak"] += 1
            st["best_streak"] = max(st["best_streak"], st["streak"])
            if not st["fastest_win"] or turns < st["fastest_win"]:
                st["fastest_win"] = turns
        else:
            st["streak"] = 0
        top = False
        if result == "won" and score > 0:
            entry = {"score": score, "difficulty": difficulty, "preset": preset, "turns": turns, "reason": reason,
                     "date": time.strftime("%Y-%m-%d")}
            lst = self.data["highscores"]
            lst.append(entry)
            lst.sort(key=lambda e: -e["score"])
            del lst[MAX_HIGHSCORES:]
            top = entry in lst
        self.save()
        return top
