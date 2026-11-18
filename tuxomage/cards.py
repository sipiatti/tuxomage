"""The TuxoMage deck: 102 original Linux / penguin themed cards.

Every card is pure data.  Its effect is a list of *operations* written in a
tiny DSL which the engine executes (see :func:`tuxomage.engine.apply_ops`) and
from which the card text is generated in Hungarian and English, so the text can
never disagree with what the card really does.

Operations (``who`` is ``"self"``, ``"enemy"`` or ``"both"``)::

    ("add", who, attr, n)            change an attribute by n (may be negative)
    ("dmg", who, n)                  damage: hits the Firewall first, the rest the Tower
    ("tdmg", who, n)                 damage straight to the Tower
    ("if", cond, then_ops, else_ops) cond = (lhs, "<"|">"|"=", rhs); lhs/rhs = (who, attr) or int
    ("max", attr)                    both players' attr becomes the higher one
    ("copy", attr)                   if yours is lower, it becomes equal to the enemy's
    ("swap", attr)                   swap the attribute with the enemy
    ("steal", ((attr, n), ...))      enemy loses up to n of each; you gain half (rounded up)
    ("lowest", attr, ops)            ops hit the player(s) with the lowest attr (who = "it")

Attributes: tower, wall, the three producers (compiler, kernel, colony) and
the three stocks (code, bytes, penguins).

Card mechanics and balance follow the classic tower-building card game
Arcomage (Might and Magic VII/VIII); names, texts and art are all original.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# category -> (stock resource paying for it, its producer)
CATEGORIES = {"red": ("code", "compiler"), "blue": ("bytes", "kernel"), "green": ("penguins", "colony")}
CATEGORY_ORDER = ("red", "blue", "green")
STOCKS = ("code", "bytes", "penguins")
PRODUCERS = ("compiler", "kernel", "colony")
PRODUCER_OF = {"code": "compiler", "bytes": "kernel", "penguins": "colony"}
ATTRS = ("tower", "wall") + PRODUCERS + STOCKS

NAMES = {
    "hu": {"tower": "Torony", "wall": "Tűzfal", "compiler": "Fordító", "kernel": "Kernel", "colony": "Kolónia",
           "code": "Kód", "bytes": "Bájt", "penguins": "Pingvin"},
    "en": {"tower": "Tower", "wall": "Firewall", "compiler": "Compiler", "kernel": "Kernel", "colony": "Colony",
           "code": "Code", "bytes": "Bytes", "penguins": "Penguins"},
}
CATEGORY_NAMES = {
    "hu": {"red": "Kód-lap", "blue": "Bájt-lap", "green": "Pingvin-lap"},
    "en": {"red": "Code card", "blue": "Bytes card", "green": "Penguin card"},
}


@dataclass(frozen=True)
class Card:
    id: str
    cat: str
    cost: int
    weight: int
    name_hu: str
    name_en: str
    ops: tuple
    icon: str
    play_again: bool = False
    draw_discard: bool = False      # draw 1, discard 1, play again
    undiscardable: bool = False
    tags: tuple = field(default=())

    @property
    def resource(self) -> str:
        return CATEGORIES[self.cat][0]

    def name(self, lang: str = "hu") -> str:
        return self.name_hu if lang == "hu" else self.name_en

    def text(self, lang: str = "hu") -> str:
        return card_text(self, lang)


def _c(cid, cat, cost, weight, hu, en, ops, icon, **flags):
    return Card(cid, cat, cost, weight, hu, en, tuple(ops), icon, **flags)


S, E, B = "self", "enemy", "both"

# ---------------------------------------------------------------- red: Kód
RED = [
    _c("code_freeze", "red", 0, 3, "Kódbefagyasztás", "Code Freeze", [("add", B, "code", -8)], "snowflake"),
    _c("lucky_commit", "red", 0, 1, "Szerencsés commit", "Lucky Commit",
       [("add", S, "code", 2), ("add", S, "bytes", 2)], "clover", play_again=True),
    _c("hotfix", "red", 1, 2, "Gyorsjavítás", "Hotfix", [("add", S, "wall", 1)], "bandage", play_again=True),
    _c("new_contributor", "red", 3, 3, "Új fejlesztő", "New Contributor", [("add", S, "compiler", 1)], "keyboard"),
    _c("catch_up_merge", "red", 4, 3, "Felzárkózó merge", "Catch-up Merge",
       [("if", ((S, "compiler"), "<", (E, "compiler")), [("add", S, "compiler", 2)], [("add", S, "compiler", 1)])],
       "branch"),
    _c("intern_squad", "red", 7, 2, "Gyakornokcsapat", "Intern Squad",
       [("add", S, "wall", 4), ("add", S, "compiler", 1)], "coffee"),
    _c("night_shift", "red", 2, 3, "Éjszakai műszak", "Night Shift",
       [("add", S, "wall", 5), ("add", S, "bytes", -6)], "moon"),
    _c("fork_it", "red", 5, 2, "Forkold le!", "Fork It!", [("copy", "compiler")], "fork"),
    _c("iptables_rule", "red", 2, 3, "iptables-szabály", "iptables Rule", [("add", S, "wall", 3)], "wall"),
    _c("packet_filter", "red", 3, 2, "Csomagszűrő", "Packet Filter", [("add", S, "wall", 4)], "funnel"),
    _c("open_standard", "red", 2, 3, "Nyílt szabvány", "Open Standard",
       [("add", B, "compiler", 1), ("add", S, "bytes", 4)], "scroll"),
    _c("clean_install", "red", 3, 3, "Tiszta telepítés", "Clean Install",
       [("if", ((S, "wall"), "=", 0), [("add", S, "wall", 6)], [("add", S, "wall", 3)])], "disc"),
    _c("server_quake", "red", 7, 2, "Szerverterem-rengés", "Server Room Quake",
       [("add", B, "wall", -5)], "quake", play_again=True),
    _c("hidden_module", "red", 8, 1, "Rejtett modul", "Hidden Module", [("add", S, "kernel", 1)], "puzzle",
       play_again=True),
    _c("dependency_hell", "red", 0, 3, "Függőségi pokol", "Dependency Hell", [("add", B, "compiler", -1)], "knot"),
    _c("firewall_upgrade", "red", 5, 3, "Tűzfalbővítés", "Firewall Upgrade", [("add", S, "wall", 6)], "shield"),
    _c("broken_build", "red", 4, 2, "Eltört build", "Broken Build", [("add", E, "compiler", -1)], "brokengear"),
    _c("new_workstation", "red", 6, 2, "Új munkaállomás", "New Workstation", [("add", S, "compiler", 2)], "monitor"),
    _c("big_refactor", "red", 0, 2, "Nagy refaktorálás", "Big Refactor",
       [("add", S, "compiler", -1), ("add", S, "wall", 10), ("add", S, "bytes", 5)], "broom"),
    _c("hardened_firewall", "red", 8, 3, "Megerősített tűzfal", "Hardened Firewall", [("add", S, "wall", 8)],
       "shield"),
    _c("dev_camp", "red", 9, 2, "Fejlesztői tábor", "Dev Camp",
       [("add", S, "wall", 5), ("add", S, "colony", 1)], "tent"),
    _c("clean_code", "red", 9, 2, "Kristálytiszta kód", "Crystal Clear Code",
       [("add", S, "wall", 7), ("add", S, "bytes", 7)], "diamond"),
    _c("stable_release", "red", 11, 2, "Stabil kiadás", "Stable Release",
       [("add", S, "wall", 6), ("add", S, "tower", 3)], "package"),
    _c("bastion_wall", "red", 13, 2, "Bástyafal", "Bastion Wall", [("add", S, "wall", 12)], "castle"),
    _c("lts_release", "red", 15, 2, "Hosszú távú kiadás", "LTS Release",
       [("add", S, "wall", 8), ("add", S, "tower", 5)], "calendar"),
    _c("rock_solid", "red", 16, 2, "Sziklaszilárd tűzfal", "Rock-solid Firewall", [("add", S, "wall", 15)],
       "mountain"),
    _c("packet_cannon", "red", 18, 2, "Csomagágyú", "Packet Cannon",
       [("add", S, "wall", 6), ("dmg", E, 10)], "cannon"),
    _c("mainframe", "red", 24, 2, "Nagyszámítógép", "Mainframe",
       [("add", S, "wall", 20), ("add", S, "tower", 8)], "server"),
    _c("crunch_time", "red", 7, 2, "Hajrá-hét", "Crunch Week",
       [("add", S, "wall", 9), ("add", S, "penguins", -5)], "hourglass"),
    _c("starter_repo", "red", 1, 2, "Kezdő repó", "Starter Repo",
       [("add", S, "wall", 1), ("add", S, "tower", 1), ("add", S, "penguins", 2)], "seedling"),
    _c("flooded_server", "red", 6, 3, "Beázott szerverterem", "Flooded Server Room",
       [("lowest", "wall", [("add", "it", "colony", -1), ("tdmg", "it", 2)])], "water"),
    _c("hackerspace", "red", 10, 2, "Hackerspace", "Hackerspace",
       [("add", S, "penguins", 6), ("add", S, "wall", 6),
        ("if", ((S, "colony"), "<", (E, "colony")), [("add", S, "colony", 1)], [])], "house"),
    _c("honeypot", "red", 14, 2, "Mézesbödön", "Honeypot", [("add", S, "wall", 7), ("dmg", E, 6)], "honey"),
    _c("config_swap", "red", 17, 2, "Konfigcsere", "Config Swap", [("swap", "wall")], "swap"),
]

# ---------------------------------------------------------------- blue: Bájt
BLUE = [
    _c("tiny_patch", "blue", 1, 2, "Apró folt", "Tiny Patch", [("add", S, "tower", 1)], "patch", play_again=True),
    _c("ping", "blue", 2, 2, "Ping", "Ping", [("tdmg", E, 1)], "signal", play_again=True),
    _c("kernel_module", "blue", 2, 3, "Kernelmodul", "Kernel Module", [("add", S, "tower", 3)], "chip"),
    _c("scheduler_tuning", "blue", 3, 2, "Ütemező-hangolás", "Scheduler Tuning", [("add", S, "kernel", 1)],
       "gear"),
    _c("grep", "blue", 2, 1, "grep", "grep", [], "magnifier", draw_discard=True),
    _c("pinned_config", "blue", 5, 2, "Rögzített konfig", "Pinned Config", [("add", S, "tower", 3)], "pin",
       undiscardable=True),
    _c("overclock_burst", "blue", 4, 3, "Túlhajtási löket", "Overclock Burst",
       [("add", S, "tower", 2), ("tdmg", E, 2)], "lightning"),
    _c("multicore", "blue", 6, 2, "Többmagos processzor", "Multicore CPU",
       [("add", S, "kernel", 1), ("add", S, "tower", 3), ("add", E, "tower", 1)], "cpu"),
    _c("bit_flip", "blue", 2, 3, "Bitfordulás", "Bit Flip", [("tdmg", E, 3)], "bits"),
    _c("swap_partition", "blue", 3, 3, "Swap partíció", "Swap Partition", [("add", S, "tower", 5)], "disk"),
    _c("kernel_panic", "blue", 4, 3, "Kernelpánik", "Kernel Panic", [("tdmg", E, 5)], "alarm"),
    _c("overvolt", "blue", 3, 2, "Feszültségemelés", "Overvolting",
       [("tdmg", S, 5), ("add", S, "kernel", 2)], "battery"),
    _c("harmony_build", "blue", 7, 2, "Harmonikus build", "Harmony Build",
       [("add", S, "kernel", 1), ("add", S, "tower", 3), ("add", S, "wall", 3)], "music"),
    _c("gpl_parity", "blue", 7, 2, "GPL-egyenlőség", "GPL Parity", [("max", "kernel")], "scales"),
    _c("ram_upgrade", "blue", 6, 2, "RAM-bővítés", "RAM Upgrade", [("add", S, "tower", 8)], "ram"),
    _c("man_pages", "blue", 9, 2, "Man oldalak", "Man Pages",
       [("add", S, "tower", 5), ("add", S, "kernel", 1)], "book"),
    _c("oom_killer", "blue", 8, 3, "OOM-gyilkos", "OOM Killer",
       [("add", S, "kernel", -1), ("tdmg", E, 9)], "skull"),
    _c("ext4_journal", "blue", 7, 2, "Ext4-napló", "Ext4 Journal",
       [("add", S, "tower", 5), ("add", E, "code", -6)], "notebook"),
    _c("ssd", "blue", 10, 2, "SSD-meghajtó", "SSD Drive", [("add", S, "tower", 11)], "ssd"),
    _c("fork_bomb", "blue", 5, 3, "Forkbomba", "Fork Bomb",
       [("tdmg", B, 7), ("add", B, "kernel", -1)], "bomb"),
    _c("cron_job", "blue", 13, 2, "Cron-feladat", "Cron Job",
       [("add", S, "tower", 6), ("tdmg", E, 4)], "clock"),
    _c("bytecode", "blue", 4, 2, "Bájtkód-fordítás", "Bytecode Build",
       [("add", S, "tower", 7), ("add", S, "code", -10)], "brackets"),
    _c("raid_array", "blue", 12, 2, "RAID-tömb", "RAID Array",
       [("add", S, "tower", 8), ("add", S, "wall", 3)], "stack"),
    _c("community_support", "blue", 14, 2, "Közösségi támogatás", "Community Support",
       [("add", S, "tower", 8), ("add", S, "colony", 1)], "heart"),
    _c("supercomputer", "blue", 16, 2, "Szuperszámítógép", "Supercomputer", [("add", S, "tower", 15)], "rack"),
    _c("snapshot", "blue", 15, 2, "Pillanatkép-mentés", "Snapshot Backup",
       [("add", S, "tower", 10), ("add", S, "wall", 5), ("add", S, "penguins", 5)], "camera"),
    _c("live_patch", "blue", 17, 2, "Élő kernelfolt", "Live Kernel Patch",
       [("add", S, "tower", 12), ("dmg", E, 6)], "flame"),
    _c("penguin_datacenter", "blue", 21, 2, "Pingvin-adatközpont", "Penguin Datacenter",
       [("add", S, "tower", 20)], "igloo"),
    _c("container_image", "blue", 8, 2, "Konténerkép", "Container Image",
       [("add", S, "tower", 11), ("add", S, "wall", -6)], "container"),
    _c("goodie_bag", "blue", 0, 2, "Ajándékcsomag", "Goodie Bag",
       [("if", ((S, "tower"), "<", (E, "tower")), [("add", S, "tower", 2)], [("add", S, "tower", 1)])], "gift"),
    _c("open_source_gift", "blue", 0, 2, "Nyílt forrású ajándék", "Open Source Gift",
       [("add", B, "tower", 1), ("add", S, "bytes", 3)], "rainbow"),
    _c("junior_sysadmin", "blue", 5, 3, "Ifjú rendszergazda", "Junior Sysadmin",
       [("add", S, "tower", 4), ("add", S, "penguins", -3), ("tdmg", E, 2)], "wrench"),
    _c("zero_day", "blue", 11, 2, "Nulladik napi rés", "Zero-day Exploit",
       [("if", ((S, "tower"), ">", (E, "wall")), [("tdmg", E, 8)], [("dmg", E, 8)])], "key"),
    _c("release_party", "blue", 18, 2, "Kiadási buli", "Release Party",
       [("add", S, "tower", 13), ("add", S, "penguins", 6), ("add", S, "code", 6)], "party"),
]

# ---------------------------------------------------------------- green: Pingvin
GREEN = [
    _c("fish_shortage", "green", 0, 2, "Halhiány", "Fish Shortage", [("add", B, "penguins", -6)], "fishbone"),
    _c("tiny_penguin", "green", 1, 1, "Pici pingvin", "Tiny Penguin", [("dmg", E, 2)], "penguin", play_again=True),
    _c("grumpy_troll", "green", 1, 3, "Morcos fórumtroll", "Grumpy Forum Troll",
       [("dmg", E, 4), ("add", S, "bytes", -3)], "troll"),
    _c("rookery", "green", 3, 2, "Költőtelep", "Rookery", [("add", S, "colony", 1)], "egg"),
    _c("scout_penguin", "green", 2, 1, "Felderítő pingvin", "Scout Penguin", [], "binoculars", draw_discard=True),
    _c("spam_flood", "green", 3, 3, "Spamáradat", "Spam Flood", [("dmg", E, 6), ("dmg", S, 3)], "mail"),
    _c("snowball_throwers", "green", 4, 2, "Hógolyózók", "Snowball Throwers",
       [("tdmg", E, 3), ("dmg", S, 1)], "snowball"),
    _c("shadow_daemon", "green", 6, 2, "Árnyékdémon", "Shadow Daemon", [("tdmg", E, 2)], "ghost",
       play_again=True),
    _c("bug_hunter", "green", 3, 3, "Bugvadász", "Bug Hunter", [("dmg", E, 5)], "bug"),
    _c("walrus_guard", "green", 5, 3, "Rozmárőrség", "Walrus Guard", [("dmg", E, 4), ("add", S, "wall", 3)],
       "walrus"),
    _c("python_scripts", "green", 6, 3, "Kígyózó szkriptek", "Slithering Scripts", [("tdmg", E, 4)], "snake"),
    _c("penguin_nursery", "green", 7, 3, "Pingvinóvoda", "Penguin Nursery", [("add", S, "colony", 2)], "nest"),
    _c("gnome_helper", "green", 8, 2, "Kerti törpe segéd", "Garden Gnome Helper",
       [("dmg", E, 2), ("add", S, "tower", 4), ("add", S, "wall", 2)], "gnome"),
    _c("midnight_hackathon", "green", 0, 2, "Éjféli hackathon", "Midnight Hackathon",
       [("add", B, "colony", 1), ("add", S, "penguins", 3)], "pizza"),
    _c("ice_skater", "green", 5, 3, "Jégkorcsolyás", "Ice Skater", [("dmg", E, 6)], "skate"),
    _c("leopard_seal", "green", 6, 3, "Leopárdfóka", "Leopard Seal", [("dmg", E, 7)], "seal"),
    _c("angry_gnu", "green", 6, 3, "Mérges gnú", "Angry Gnu", [("dmg", E, 6), ("add", E, "penguins", -3)], "horns"),
    _c("script_kiddie", "green", 5, 3, "Szkriptkölyök", "Script Kiddie",
       [("dmg", E, 6), ("add", B, "code", -5), ("add", B, "bytes", -5), ("add", B, "penguins", -5)], "hoodie"),
    _c("port_scanner", "green", 8, 2, "Portszkenner", "Port Scanner",
       [("if", ((E, "wall"), "=", 0), [("dmg", E, 10)], [("dmg", E, 6)])], "radar"),
    _c("polar_bear", "green", 9, 2, "Jegesmedve", "Polar Bear", [("dmg", E, 9)], "bear"),
    _c("rootkit", "green", 11, 2, "Rootkit", "Rootkit",
       [("if", ((E, "wall"), ">", 0), [("dmg", E, 10)], [("dmg", E, 7)])], "mask"),
    _c("narwhal", "green", 9, 2, "Narvál", "Narwhal",
       [("if", ((S, "kernel"), ">", (E, "kernel")), [("dmg", E, 12)], [("dmg", E, 8)])], "narwhal"),
    _c("snowball_snipers", "green", 10, 2, "Hógolyó-mesterlövészek", "Snowball Snipers",
       [("if", ((S, "wall"), ">", (E, "wall")), [("tdmg", E, 6)], [("dmg", E, 6)])], "target"),
    _c("phishing_penguin", "green", 14, 2, "Adathalász pingvin", "Phishing Penguin",
       [("tdmg", E, 5), ("add", E, "penguins", -8)], "hook"),
    _c("yeti", "green", 11, 2, "Jeti", "Yeti", [("dmg", E, 8), ("add", E, "compiler", -1)], "footprint"),
    _c("packet_sniffer", "green", 12, 2, "Csomagszimatoló", "Packet Sniffer",
       [("steal", (("bytes", 10), ("code", 5)))], "nose"),
    _c("iceberg_golem", "green", 15, 2, "Jéghegy-gólem", "Iceberg Golem", [("dmg", E, 10), ("add", S, "wall", 4)],
       "iceberg"),
    _c("ransomware", "green", 17, 2, "Zsarolóvírus", "Ransomware",
       [("dmg", E, 10), ("add", E, "penguins", -5), ("add", E, "colony", -1)], "lock"),
    _c("orca_pod", "green", 25, 2, "Kardszárnyú delfinraj", "Orca Pod",
       [("dmg", E, 20), ("add", E, "bytes", -10), ("add", E, "colony", -1)], "orca"),
    _c("penguin_guard", "green", 2, 3, "Pingvinőr", "Penguin Guard",
       [("if", ((S, "wall"), ">", (E, "wall")), [("dmg", E, 3)], [("dmg", E, 2)])], "spear"),
    _c("seal_pup", "green", 2, 3, "Fókakölyök", "Seal Pup", [("dmg", E, 3), ("add", S, "bytes", 1)], "pup"),
    _c("kamikaze_penguin", "green", 4, 3, "Vakmerő pingvin", "Daredevil Penguin",
       [("dmg", E, 8), ("tdmg", S, 3)], "rocket"),
    _c("emperor_penguin", "green", 13, 2, "Császárpingvin", "Emperor Penguin",
       [("dmg", E, 13), ("add", S, "bytes", -3)], "crown"),
    _c("albatross_squadron", "green", 18, 2, "Albatroszraj", "Albatross Squadron", [("tdmg", E, 12)], "bird"),
]

DECK: list[Card] = RED + BLUE + GREEN
BY_ID: dict[str, Card] = {c.id: c for c in DECK}
assert len(BY_ID) == len(DECK), "duplicate card id"


def card(cid: str) -> Card:
    return BY_ID[cid]


# =============================================================== card text
_T = {
    "hu": {
        "enemy": "ellenfél", "both": "mindenki", "dmg": "{n} sebzés", "dmg_self": "{n} sebzés magadnak",
        "dmg_both": "{n} sebzés mindkét félnek", "tdmg": "{n} sebzés az ellenfél tornyára",
        "tdmg_self": "{n} sebzés a saját tornyodra", "tdmg_both": "{n} sebzés minden toronyra",
        "tdmg_it": "{n} toronysebzés", "dmg_it": "{n} sebzés",
        "if": "Ha {c}: {a}", "else": ", különben {b}", "enemy_attr": "ellenfél {a}",
        "max": "Mindkét {a} a nagyobbikkal lesz egyenlő",
        "copy": "Ha a {a} kisebb az ellenfélénél, egyenlő lesz vele",
        "swap": "{a} csere az ellenféllel", "steal": "ellenfél: {lst}; a felét megkapod",
        "lowest": "Akinek a legkisebb a {a}: {ops}",
        "again": "Újra jössz!", "dd": "Húzz egy lapot, dobj el egyet, és újra jössz!",
        "undisc": "Nem dobható el.",
    },
    "en": {
        "enemy": "enemy", "both": "everyone", "dmg": "{n} damage", "dmg_self": "{n} damage to you",
        "dmg_both": "{n} damage to both", "tdmg": "{n} damage to enemy tower",
        "tdmg_self": "{n} damage to your tower", "tdmg_both": "{n} damage to all towers",
        "tdmg_it": "{n} tower damage", "dmg_it": "{n} damage",
        "if": "If {c}: {a}", "else": ", else {b}", "enemy_attr": "enemy {a}",
        "max": "Both {a}s become the higher one",
        "copy": "If your {a} is lower than the enemy's, it becomes equal",
        "swap": "Swap {a} with the enemy", "steal": "enemy: {lst}; you gain half",
        "lowest": "Lowest {a}: {ops}",
        "again": "Play again!", "dd": "Draw a card, discard one, play again!",
        "undisc": "Can't be discarded.",
    },
}


def _signed(n: int) -> str:
    return f"+{n}" if n >= 0 else f"\u2212{-n}"


def _side(term, lang):
    if isinstance(term, int):
        return str(term)
    who, attr = term
    name = NAMES[lang][attr]
    return _T[lang]["enemy_attr"].format(a=name) if who == E else name


def _op_text(op, lang) -> str:
    t, nm = _T[lang], NAMES[lang]
    kind = op[0]
    if kind == "add":
        _, who, attr, n = op
        s = f"{_signed(n)} {nm[attr]}"
        if who == E:
            return f"{t['enemy']}: {s}"
        if who == B:
            return f"{t['both']}: {s}"
        return s
    if kind in ("dmg", "tdmg"):
        _, who, n = op
        key = kind + {S: "", E: "", B: "_both", "it": "_it"}[who] + ("_self" if who == S else "")
        return t[key].format(n=n)
    if kind == "if":
        _, (lhs, cmp, rhs), then, other = op
        cond = f"{_side(lhs, lang)} {cmp} {_side(rhs, lang)}"
        out = t["if"].format(c=cond, a=ops_text(then, lang))
        if other:
            out += t["else"].format(b=ops_text(other, lang))
        return out
    if kind in ("max", "copy", "swap"):
        return t[kind].format(a=nm[op[1]])
    if kind == "steal":
        lst = ", ".join(f"{_signed(-n)} {nm[a]}" for a, n in op[1])
        return t["steal"].format(lst=lst)
    if kind == "lowest":
        return t["lowest"].format(a=nm[op[1]], ops=ops_text(op[2], lang))
    raise ValueError(f"unknown op {op!r}")


def ops_text(ops, lang="hu") -> str:
    return ", ".join(_op_text(o, lang) for o in ops)


def card_text(c: Card, lang: str = "hu") -> str:
    parts = []
    if c.ops:
        parts.append(ops_text(c.ops, lang) + ".")
    t = _T[lang]
    if c.play_again:
        parts.append(t["again"])
    if c.draw_discard:
        parts.append(t["dd"])
    if c.undiscardable:
        parts.append(t["undisc"])
    txt = " ".join(parts)
    return txt[:1].upper() + txt[1:]
