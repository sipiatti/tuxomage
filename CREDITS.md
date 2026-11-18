# Credits / Forrásmegjelölés

Author / Szerző: **Siposs Attila** <sipiatti@gmail.com>. The game, its cards, artwork and audio were created using vibe coding, with the help of Grok Bot. / A játék (a lapokkal, grafikával és hangokkal együtt) vibe coding technikával, a Grok Bot segítségével készült.

| Asset | Files | Source | License |
|---|---|---|---|
| Penguin sprites (wizard-hat player and crowned computer; normal / happy / sad) | `tuxomage/assets/penguins/*.png`, `tuxomage/assets/svg/*.svg` | Original artwork drawn as SVG code in `tools/make_assets.py` (Tux-*inspired*, not derived from Larry Ewing's Tux files) | **CC0 1.0** |
| UI icons (resources, producers, tower, wall, trophy, bin, home, cards, globe, robot, arrows, pause, gear, music, speaker, …) and the app icon | `tuxomage/assets/icons/*.png`, `data/icons/*` | Original artwork, `tools/make_assets.py` | **CC0 1.0** |
| 102 card illustrations | `tuxomage/assets/cardart/*.png` | Original artwork, `tools/make_assets.py` | **CC0 1.0** |
| Card names and texts (HU/EN) | `tuxomage/cards.py` | Original, written for TuxoMage | MIT (with the code) |
| Sound effects: click, hover, draw, play, discard, build, tower, damage, resource, turn, denied, victory, defeat | `tuxomage/assets/sounds/*.wav` | Original, synthesized from code (numpy) in `tools/make_sounds.py` | **CC0 1.0** |
| Music: "Pingvinvarázs" (menu loop, 34 s, 112 BPM, D major) and "Tornyok a jégen" (gameplay loop, 91 s, 84 BPM, A minor) | `tuxomage/assets/music/menu.ogg`, `game.ogg` | Original compositions, synthesized by `tools/make_sounds.py` (ffmpeg/libvorbis used only as the encoder) | **CC0 1.0** |
| Font **Baloo 2** (500, 700, 800) | `tuxomage/assets/fonts/Baloo2-*.ttf` | Copyright 2019 The Baloo 2 Project Authors, https://github.com/EkType/Baloo2 | **SIL Open Font License 1.1**, `tuxomage/assets/fonts/OFL.txt` |
| Game engine | not bundled | pygame, https://www.pygame.org | LGPL 2.1 |

**Inspiration:** the gameplay ideas (tower, wall, three producers, colour-coded cards) are inspired by *Arcomage* (3DO / New World Computing).
TuxoMage is not affiliated with Arcomage or its rights holders.
It contains no original Arcomage card names, card texts, artwork, sounds or music.

"Tux" the Linux penguin was originally drawn by Larry Ewing using The GIMP. TuxoMage's penguins are independent drawings in a similar spirit.
