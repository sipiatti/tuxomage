"""Hungarian (default) and English UI strings."""
from __future__ import annotations

LANGS = ("hu", "en")
_lang = "hu"

S = {
    # menu
    "subtitle": ("Pingvinvarázslók tornyos kártyacsatája", "A penguin wizard tower-building card duel"),
    "play": ("Új játék", "New game"),
    "rematch": ("Visszavágó", "Rematch"),
    "howto": ("Hogyan játssz?", "How to play"),
    "cards": ("Kártyák", "Cards"),
    "stats": ("Statisztika", "Statistics"),
    "quit": ("Kilépés", "Quit"),
    "menu": ("Menü", "Menu"),
    "back": ("Vissza", "Back"),
    "done": ("Kész", "Done"),
    "ok": ("Értem!", "Got it!"),
    "start": ("Indulás!", "Start!"),
    "continue": ("Folytatás", "Resume"),
    "give_up": ("Feladom", "Give up"),
    "version": ("v{v}", "v{v}"),
    # setup
    "setup_title": ("Új játék", "New game"),
    "rules_preset": ("Szabályok", "Rules"),
    "difficulty": ("Ellenfél", "Opponent"),
    "first_player": ("Ki kezd?", "Who starts?"),
    "first_player_v": ("Te", "You"),
    "first_ai": ("Gép", "Computer"),
    "first_random": ("Véletlen", "Random"),
    "easy": ("Könnyű", "Easy"),
    "normal": ("Normál", "Normal"),
    "hard": ("Nehéz", "Hard"),
    "easy_d": ("Kezdő pingvin, néha téved", "Beginner penguin, makes mistakes"),
    "normal_d": ("Megfontolt varázsló", "Thoughtful wizard"),
    "hard_d": ("Ravasz főmágus", "Cunning archmage"),
    "preset_classic": ("Klasszikus", "Classic"),
    "preset_quick": ("Gyors meccs", "Quick match"),
    "preset_fortress": ("Erődharc", "Fortress"),
    "preset_marathon": ("Maraton", "Marathon"),
    "preset_line1": ("Kezdés: torony {t}, tűzfal {w}", "Start: tower {t}, firewall {w}"),
    "preset_line2": ("termelés {p}, készlet {s}", "production {p}, stock {s}"),
    "preset_line3": ("Cél: torony {wt} / készlet {wr}", "Goal: tower {wt} / stock {wr}"),
    # play
    "you": ("Te", "You"),
    "computer": ("Gép", "Computer"),
    "your_turn": ("Te jössz!", "Your turn!"),
    "ai_turn": ("A gép gondolkodik…", "Computer is thinking…"),
    "play_again": ("Újra jössz!", "Play again!"),
    "ai_again": ("A gép újra jön!", "Computer plays again!"),
    "must_discard": ("Dobj el egy lapot!", "Discard a card!"),
    "ai_discards": ("A gép eldob egy lapot…", "Computer discards a card…"),
    "discard": ("Eldob", "Discard"),
    "discarded": ("ELDOBVA", "DISCARDED"),
    "turn_n": ("{n}. kör", "Turn {n}"),
    "goal": ("Cél: torony {t} · készlet {r}", "Goal: tower {t} · stock {r}"),
    "log_title": ("Napló", "Log"),
    "log_play": ("{who}: {card}", "{who}: {card}"),
    "log_discard": ("{who} eldobta: {card}", "{who} discarded: {card}"),
    "cost": ("Ár: {n} {res}", "Cost: {n} {res}"),
    "need_more": ("Még {n} {res} kell", "Need {n} more {res}"),
    "cant_discard": ("Ezt a lapot nem lehet eldobni!", "This card can't be discarded!"),
    "hint_controls": ("Bal klikk: kijátszás · Jobb klikk / húzás a kukába: eldobás",
                      "Left click: play · Right click / drag to bin: discard"),
    "last_played": ("Utoljára kijátszva", "Last played"),
    "production": ("termelés", "production"),
    "stock": ("készlet", "stock"),
    # results
    "victory": ("Győzelem!", "Victory!"),
    "defeat": ("Vereség…", "Defeat…"),
    "draw": ("Döntetlen!", "Draw!"),
    "reason_tower_0": ("A tornyod elérte a célmagasságot!", "Your tower reached the goal height!"),
    "reason_tower_1": ("A gép tornya elérte a célmagasságot.", "The computer's tower reached the goal height."),
    "reason_destroy_0": ("Leromboltad a gép tornyát!", "You destroyed the computer's tower!"),
    "reason_destroy_1": ("A gép lerombolta a tornyodat.", "The computer destroyed your tower."),
    "reason_resource_0": ("Összegyűjtötted a szükséges készletet!", "You collected the goal amount of a stock!"),
    "reason_resource_1": ("A gép összegyűjtötte a szükséges készletet.", "The computer collected the goal amount of a stock."),
    "reason_draw": ("Egyszerre teljesült mindkét fél győzelmi feltétele.", "Both sides reached a goal at the same time."),
    "score": ("Pontszám: {n}", "Score: {n}"),
    "new_record": ("Új rekord a toplistán!", "New entry in the top list!"),
    "turns_taken": ("{n} kör", "turns: {n}"),
    # stats
    "stats_title": ("Statisztika", "Statistics"),
    "played": ("Játszott", "Played"),
    "won": ("Nyert", "Won"),
    "lost": ("Vesztett", "Lost"),
    "draws": ("Döntetlen", "Draws"),
    "streak": ("Legjobb sorozat", "Best streak"),
    "fastest": ("Leggyorsabb győzelem", "Fastest win"),
    "top_scores": ("Legjobb győzelmek", "Best wins"),
    "no_scores": ("Még nincs győzelem – rajta!", "No wins yet – go for it!"),
    # cards
    "cards_title": ("Kártyák", "Cards"),
    "all": ("Mind", "All"),
    "page": ("{a}/{b}. oldal", "Page {a}/{b}"),
    "card_count": ("{n} lap", "{n} cards"),
    # settings
    "settings": ("Beállítások", "Settings"),
    "music": ("Zene", "Music"),
    "sfx": ("Hangok", "Sounds"),
    "muted": ("némítva", "muted"),
    "language": ("Nyelv: Magyar", "Language: English"),
    "fullscreen": ("Teljes képernyő: {v}", "Fullscreen: {v}"),
    "ai_speed": ("Gép tempója: {v}", "Computer speed: {v}"),
    "speed_slow": ("lassú", "slow"),
    "speed_normal": ("normál", "normal"),
    "speed_fast": ("gyors", "fast"),
    "on": ("BE", "ON"),
    "off": ("KI", "OFF"),
    "no_audio": ("Nem található hangeszköz – a játék hang nélkül fut.", "No audio device found – the game runs silently."),
    "keys_settings": ("M: zene be/ki   ·   S: hangok be/ki   ·   F11: teljes képernyő",
                      "M: music on/off   ·   S: sounds on/off   ·   F11: fullscreen"),
    "tip_music": ("Zene (M)", "Music (M)"),
    "tip_sfx": ("Hangok (S)", "Sounds (S)"),
    "tip_settings": ("Beállítások", "Settings"),
    "tip_help": ("Súgó", "Help"),
    "tip_menu": ("Menü (Esc)", "Menu (Esc)"),
    # help
    "help_title": ("Hogyan játssz?", "How to play"),
    "h_goal": ("A cél", "Goal"),
    "h_goal_t": ("Építsd fel a tornyodat a célig, rombold le az ellenfélét, vagy gyűjts össze elég készletet bármelyikből.",
                 "Build your tower to the goal, destroy the enemy tower, or collect enough of any one stock."),
    "h_res": ("Erőforrások", "Resources"),
    "h_res_t": ("Fordító → Kód (piros lapok) · Kernel → Bájt (kék lapok) · Kolónia → Pingvin (zöld lapok).",
                "Compiler → Code (red cards) · Kernel → Bytes (blue cards) · Colony → Penguins (green cards)."),
    "h_turn": ("A kör", "Your turn"),
    "h_turn_t": ("Köröd elején a termelők feltöltik a készleteidet. Utána kijátszol egy lapot, vagy eldobsz egyet.",
                 "At the start of your turn producers refill your stocks. Then play one card or discard one."),
    "h_dmg": ("Sebzés", "Damage"),
    "h_dmg_t": ("A sebzés először a Tűzfalat bontja, a maradék a Tornyot. A „toronysebzés” egyenesen a toronyba megy.",
                "Damage hits the Firewall first, the rest the Tower. “Tower damage” goes straight to the tower."),
    "h_special": ("Különleges lapok", "Special cards"),
    "h_special_t": ("„Újra jössz” – még egy lapot játszhatsz. „Húzz, dobj, újra jössz” – egy extra lap, egy kötelező dobás.",
                    "“Play again” – play another card. “Draw, discard, play again” – one extra card, one forced discard."),
    "h_mouse": ("Egér", "Mouse"),
    "h_mouse_t": ("Bal klikk: kijátszás · Jobb klikk, kuka gomb vagy húzás a kukába: eldobás · Rámutatás: nagyítás.",
                  "Left click: play · Right click, bin button or drag to bin: discard · Hover: zoom."),
    "h_keys": ("Billentyűk", "Keys"),
    "h_keys_t": ("1–6: lap kijátszása · Shift+1–6: eldobás · M: zene · S: hangok · F11: teljes képernyő · Esc: menü",
                 "1–6: play card · Shift+1–6: discard · M: music · S: sounds · F11: fullscreen · Esc: menu"),
    "h_credit": ("Az Arcomage (Might and Magic VII/VIII) ihlette – minden név, szöveg és kép saját.",
                 "Inspired by Arcomage (Might and Magic VII/VIII) – all names, texts and art are original."),
}


def set_lang(lang: str) -> None:
    global _lang
    _lang = lang if lang in LANGS else "hu"


def lang() -> str:
    return _lang


def tr(key: str, **kw) -> str:
    pair = S.get(key)
    if pair is None:
        return key
    s = pair[0] if _lang == "hu" else pair[1]
    return s.format(**kw) if kw else s
