# TuxoMage 🐧🏰

*[English below](#english)*

Pingvines, linuxos témájú, toronyépítős kártyajáték egy ember és a gép között, Python 3 + pygame alapon.
Az *Arcomage* nevű klasszikus játék ihlette.

> **Szerző:** Siposs Attila <sipiatti@gmail.com>  
> A játék *vibe coding* technikával, a **Grok Bot** segítségével készült.

## A játék

Két pingvinvarázsló, te és a gép, egymás ellen játszik. Mindkettőtöknek van egy **Tornya** és előtte egy **Tűzfala**,
valamint három termelő épülete és a hozzájuk tartozó készlet:

| Termelő | Készlet | Kártyaszín | Mire jó főleg |
|---|---|---|---|
| **Fordító** | **Kód** | piros | tűzfal, termelés, trükkök |
| **Kernel** | **Bájt** | kék | torony, varázslatok, lopás, csere |
| **Kolónia** | **Pingvin** | zöld | pingvinsereg, vagyis sebzés |

* **Saját köröd elején** minden termelő annyi egységet ad a készletéhez, amennyi a szintje.
* A kezedben **6 lap** van. Egy körben egy lapot **kijátszol** (ha ki tudod fizetni a színének megfelelő készletből), vagy **eldobsz**.
  Kijátszás vagy eldobás után új lapot húzol.
* Egyes lapok után **újra jössz** (a lapon „+” jelzés), kettő pedig **húzást és eldobást** ad (pl. *grep*). A „Rögzített konfig” nem dobható el.
* A **sebzés először a tűzfalat** bontja, a maradék a tornyot. A „toronysebzés” közvetlenül a toronyra megy.
* A termelők legalább 1-esek maradnak; a torony, a fal és a készletek nem mennek 0 alá.

**Győzelem**, ha a te tornyod eléri a célt, ha az ellenfél tornya 0-ra esik, vagy ha valamelyik készleted eléri az erőforráscélt.
Ha egyszerre mindketten nyernétek, **döntetlen** az eredmény.

| Előbeállítás | Torony | Tűzfal | Termelők | Készletek | Toronycél | Erőforráscél |
|---|---|---|---|---|---|---|
| Klasszikus | 20 | 5 | 2 | 5 | 50 | 150 |
| Gyors | 15 | 5 | 3 | 10 | 40 | 100 |
| Erőd | 25 | 20 | 2 | 10 | 75 | 200 |
| Maraton | 30 | 10 | 3 | 15 | 100 | 300 |

A paklit **102 saját lap** alkotja, 34 piros, 34 kék és 34 zöld. Néhány példa:
*Tűzfalbővítés* (5 Kód: +6 Tűzfal), *Forkbomba* (5 Bájt: minden toronyra 7 sebzés, mindenki −1 Kernel),
*Pingvin-adatközpont* (21 Bájt: +20 Torony), *Csomagszimatoló* (Bájt lopása), *Konfigcsere* (tűzfalak cseréje),
*Kardszárnyú delfinraj* (25 Pingvin: 20 sebzés, az ellenfél −10 Bájt, −1 Kolónia).
Minden lap a teljes listájával együtt a menü **Kártyák** képernyőjén böngészhető.

A **gép** három szinten játszik (Könnyű / Normál / Nehéz). Minden lehetséges lépést leszimulál, kiértékeli az állást,
az újra-jössz lapokat láncban is végiggondolja, a Nehéz szint pedig hangolt súlyokkal és véletlen nélkül dönt.

## Irányítás

| Egér / billentyű | Hatás |
|---|---|
| Bal klikk egy lapon | kijátszás |
| Jobb klikk, vagy húzás a kukába | eldobás |
| Kuka gomb / D | eldobó mód be/ki (utána a bal klikk eldob) |
| 1–6 / Shift + 1–6 | adott lap kijátszása / eldobása |
| Egér a lapon | nagyított lap |
| M / S | zene / hangeffektek be/ki |
| Esc | szünet (folytatás, beállítások, feladás) |
| F11 | teljes képernyő |

A ki nem fizethető lapok szürkék. A gép lapja animálva repül középre, ott egy ideig látható, és a napló is rögzíti.
A beállításokban állítható a zene és az effektek hangereje, a nyelv (magyar / angol), a teljes képernyő és a gép tempója.
Ha nincs hangeszköz, a játék hang nélkül fut; a `--mute` kapcsolóval a hangeszközt meg sem nyitja.
A statisztika (nehézségi szintenként), a dicsőségtábla és a beállítások helye: `~/.local/share/tuxomage/save.json`
(vagy `$XDG_DATA_HOME/tuxomage`, illetve `$TUXOMAGE_DATA_DIR`).

## Futtatás

```bash
sudo apt install python3-pygame      # vagy: pip install -r requirements.txt
python3 -m tuxomage                  # a projekt mappájából
python3 -m tuxomage --lang en --fullscreen --mute
# vagy telepítve:
pip install .  &&  tuxomage
```

Tesztek: `python3 -m pytest` (vagy `pip install -r requirements-dev.txt` után).

### Debian/Ubuntu csomag (.deb)

```bash
packaging/build_deb.sh                          # -> dist/tuxomage_0.1.0_all.deb
sudo apt install ./dist/tuxomage_0.1.0_all.deb  # telepítés
tuxomage                                        # vagy a menüből: Játékok → TuxoMage
sudo apt remove tuxomage                        # eltávolítás
```

## Jogi megjegyzés

A TuxoMage az *Arcomage* (3DO / New World Computing) játékmenetéből merít ihletet, de **nem áll kapcsolatban** vele
vagy jogtulajdonosaival. **Egyetlen eredeti lapnevet, szöveget, grafikát vagy hangot sem** használ: minden lap, kép,
hang és zene saját készítésű.

---

## English

A penguin and Linux themed tower-building card game for one human against the computer, written in Python 3 with pygame 2.
Inspired by the classic *Arcomage*.

> **Author:** Siposs Attila <sipiatti@gmail.com>  
> This game was created using *vibe coding*, with the help of **Grok Bot**.

**Rules.** Each side has a **Tower**, a **Firewall** in front of it, and three producers with their stocks:
**Compiler → Code** (red cards: walls, production, tricks), **Kernel → Bytes** (blue: tower, magic, stealing, swaps),
**Colony → Penguins** (green: the penguin army, i.e. damage). At the start of your turn every producer adds its level to its stock.
You hold **6 cards**. Each turn you either **play** one, paying its cost from the stock of its colour, or **discard** one; then you draw.
Some cards let you **play again** (marked "+"), two let you draw and discard (e.g. *grep*), and *Pinned Config* cannot be discarded.
**Damage hits the Firewall first**, and the rest goes to the Tower. "Tower damage" bypasses the Firewall.
Producers never drop below 1, and the other values never drop below 0.
**You win** when your Tower reaches the target, the enemy Tower falls to 0, or any of your stocks reaches the resource target.
If both players win at the same moment, the game is a **draw**.

| Preset | Tower | Firewall | Producers | Stocks | Tower goal | Resource goal |
|---|---|---|---|---|---|---|
| Classic | 20 | 5 | 2 | 5 | 50 | 150 |
| Quick | 15 | 5 | 3 | 10 | 40 | 100 |
| Fortress | 25 | 20 | 2 | 10 | 75 | 200 |
| Marathon | 30 | 10 | 3 | 15 | 100 | 300 |

**Deck:** 102 original cards (34 red, 34 blue, 34 green), stored as data in `tuxomage/cards.py`.
Each card's effect is written in a small effect language (add, damage, tower damage, conditions, max, copy, swap, steal, "whoever is lowest").
Card texts in both languages are generated from those effects, so a card's text always matches what it does. Every card is unit-tested.

**AI:** Easy, Normal and Hard. The AI simulates every legal action, scores the resulting position (towers, walls, production, stocks, threats, win/loss),
follows play-again chains, and picks a discard by how useful each card is. Easy adds a lot of noise and sometimes plays at random.
Hard uses tuned weights, looks deeper into chains and has no randomness. In tests, Hard beats Normal about 58% of the time and Easy about 75%.

**Controls:**
* Left click a card to play it.
* Right click a card, or drag it onto the bin, to discard it. The bin button or **D** toggles discard mode.
* Keys **1–6** play a card, and **Shift+1–6** discard one.
* Hover over a card to zoom in.
* **M** / **S** toggle music / sound effects.
* **Esc** pauses (resume, settings, give up), and **F11** toggles fullscreen.

Unaffordable cards are greyed out. The computer's card flies to the centre and stays visible for a moment, and the log records every move.
Settings include music/effects volume, language (Hungarian / English), fullscreen and AI speed.
If no audio device is available, the game runs silently; `--mute` skips opening the audio device entirely.
Statistics per difficulty, high scores and settings live in `~/.local/share/tuxomage/save.json`
(or `$XDG_DATA_HOME/tuxomage`, or `$TUXOMAGE_DATA_DIR`).

**Run:** `python3 -m tuxomage [--lang hu|en] [--fullscreen] [--mute]`. It needs `python3-pygame` or `pip install -r requirements.txt`.
Alternatively, run `pip install .` and then `tuxomage`. Tests: `python3 -m pytest`.

**Debian package:** `packaging/build_deb.sh` builds a reproducible `dist/tuxomage_0.1.0_all.deb` with plain `dpkg-deb`.
Install it with `sudo apt install ./dist/tuxomage_0.1.0_all.deb`.
It depends on `python3 (>= 3.10)` and `python3-pygame (>= 2.1)`.
The maintainer is set at the top of the script, or via `TUXOMAGE_MAINTAINER`.

**Project layout**

```
tuxomage/            game package (python3 -m tuxomage)
  cards.py           the 102 cards (data + effect language + HU/EN text generator)
  engine.py          rules, presets, turns, victory, scoring (pure Python)
  ai.py              computer opponent (easy / normal / hard)
  i18n.py            Hungarian / English strings
  storage.py         statistics / high scores / settings JSON
  audio.py           sound effects + music (silent fallback)
  app.py, render.py, ui.py, theme.py, resources.py   pygame front-end
  assets/            fonts (OFL), penguins, icons, card art, sounds, music (CC0)
tools/make_assets.py   regenerates all artwork from SVG code
tools/make_sounds.py   synthesizes all sound effects + music
tools/screenshots.py   headless screenshots
data/                  desktop entry + icons
packaging/             build_deb.sh, launcher, man page, debian/
tests/                 pytest suite (rules, every card, AI, AI-vs-AI games, UI)
```

**Disclaimer:** TuxoMage is inspired by the gameplay of *Arcomage* (3DO / New World Computing).
It is **not affiliated** with Arcomage or its rights holders, and it uses **no original card names, texts, artwork or audio**.

License: MIT © 2026 Siposs Attila (code); assets see [CREDITS.md](CREDITS.md).
