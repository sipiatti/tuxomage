"""Every card's effect, checked against a hand-written expectation."""
import re

import pytest

from tuxomage.cards import ATTRS, BY_ID, CATEGORIES, DECK, card_text
from tuxomage.engine import Player, play_card_effect


def scenario():
    me = Player(tower=20, wall=10, compiler=3, kernel=3, colony=3, code=30, bytes=30, penguins=30)
    foe = Player(tower=25, wall=8, compiler=2, kernel=2, colony=2, code=20, bytes=20, penguins=20)
    return me, foe


# card id -> "my changes | enemy changes" (cost is checked separately)
EXPECTED = {
    # ---- red
    "code_freeze": "code-8 | code-8",
    "lucky_commit": "code+2 bytes+2 |",
    "hotfix": "wall+1 |",
    "new_contributor": "compiler+1 |",
    "catch_up_merge": "compiler+1 |",                 # 3 >= 2 -> +1
    "intern_squad": "wall+4 compiler+1 |",
    "night_shift": "wall+5 bytes-6 |",
    "fork_it": "|",                                   # mine is not lower
    "iptables_rule": "wall+3 |",
    "packet_filter": "wall+4 |",
    "open_standard": "compiler+1 bytes+4 | compiler+1",
    "clean_install": "wall+3 |",                      # wall is not 0
    "server_quake": "wall-5 | wall-5",
    "hidden_module": "kernel+1 |",
    "dependency_hell": "compiler-1 | compiler-1",
    "firewall_upgrade": "wall+6 |",
    "broken_build": "| compiler-1",
    "new_workstation": "compiler+2 |",
    "big_refactor": "compiler-1 wall+10 bytes+5 |",
    "hardened_firewall": "wall+8 |",
    "dev_camp": "wall+5 colony+1 |",
    "clean_code": "wall+7 bytes+7 |",
    "stable_release": "wall+6 tower+3 |",
    "bastion_wall": "wall+12 |",
    "lts_release": "wall+8 tower+5 |",
    "rock_solid": "wall+15 |",
    "packet_cannon": "wall+6 | wall-8 tower-2",
    "mainframe": "wall+20 tower+8 |",
    "crunch_time": "wall+9 penguins-5 |",
    "starter_repo": "wall+1 tower+1 penguins+2 |",
    "flooded_server": "| colony-1 tower-2",           # enemy wall 8 is the lowest
    "hackerspace": "penguins+6 wall+6 |",             # colony not lower
    "honeypot": "wall+7 | wall-6",
    "config_swap": "wall-2 | wall+2",
    # ---- blue
    "tiny_patch": "tower+1 |",
    "ping": "| tower-1",
    "kernel_module": "tower+3 |",
    "scheduler_tuning": "kernel+1 |",
    "grep": "|",
    "pinned_config": "tower+3 |",
    "overclock_burst": "tower+2 | tower-2",
    "multicore": "kernel+1 tower+3 | tower+1",
    "bit_flip": "| tower-3",
    "swap_partition": "tower+5 |",
    "kernel_panic": "| tower-5",
    "overvolt": "tower-5 kernel+2 |",
    "harmony_build": "kernel+1 tower+3 wall+3 |",
    "gpl_parity": "| kernel+1",
    "ram_upgrade": "tower+8 |",
    "man_pages": "tower+5 kernel+1 |",
    "oom_killer": "kernel-1 | tower-9",
    "ext4_journal": "tower+5 | code-6",
    "ssd": "tower+11 |",
    "fork_bomb": "tower-7 kernel-1 | tower-7 kernel-1",
    "cron_job": "tower+6 | tower-4",
    "bytecode": "tower+7 code-10 |",
    "raid_array": "tower+8 wall+3 |",
    "community_support": "tower+8 colony+1 |",
    "supercomputer": "tower+15 |",
    "snapshot": "tower+10 wall+5 penguins+5 |",
    "live_patch": "tower+12 | wall-6",
    "penguin_datacenter": "tower+20 |",
    "container_image": "tower+11 wall-6 |",
    "goodie_bag": "tower+2 |",                        # 20 < 25
    "open_source_gift": "tower+1 bytes+3 | tower+1",
    "junior_sysadmin": "tower+4 penguins-3 | tower-2",
    "zero_day": "| tower-8",                          # my tower 20 > enemy wall 8
    "release_party": "tower+13 penguins+6 code+6 |",
    # ---- green
    "fish_shortage": "penguins-6 | penguins-6",
    "tiny_penguin": "| wall-2",
    "grumpy_troll": "bytes-3 | wall-4",
    "rookery": "colony+1 |",
    "scout_penguin": "|",
    "spam_flood": "wall-3 | wall-6",
    "snowball_throwers": "wall-1 | tower-3",
    "shadow_daemon": "| tower-2",
    "bug_hunter": "| wall-5",
    "walrus_guard": "wall+3 | wall-4",
    "python_scripts": "| tower-4",
    "penguin_nursery": "colony+2 |",
    "gnome_helper": "tower+4 wall+2 | wall-2",
    "midnight_hackathon": "colony+1 penguins+3 | colony+1",
    "ice_skater": "| wall-6",
    "leopard_seal": "| wall-7",
    "angry_gnu": "| wall-6 penguins-3",
    "script_kiddie": "code-5 bytes-5 penguins-5 | wall-6 code-5 bytes-5 penguins-5",
    "port_scanner": "| wall-6",                       # enemy wall > 0
    "polar_bear": "| wall-8 tower-1",
    "rootkit": "| wall-8 tower-2",                    # enemy wall > 0 -> 10 damage
    "narwhal": "| wall-8 tower-4",                    # my kernel 3 > 2 -> 12 damage
    "snowball_snipers": "| tower-6",                  # my wall 10 > 8
    "phishing_penguin": "| tower-5 penguins-8",
    "yeti": "| wall-8 compiler-1",
    "packet_sniffer": "bytes+5 code+3 | bytes-10 code-5",
    "iceberg_golem": "wall+4 | wall-8 tower-2",
    "ransomware": "| wall-8 tower-2 penguins-5 colony-1",
    "orca_pod": "| wall-8 tower-12 bytes-10 colony-1",
    "penguin_guard": "| wall-3",                      # my wall is higher -> 3
    "seal_pup": "bytes+1 | wall-3",
    "kamikaze_penguin": "tower-3 | wall-8",
    "emperor_penguin": "bytes-3 | wall-8 tower-5",
    "albatross_squadron": "| tower-12",
}


def parse(spec):
    out = {}
    for tok in spec.split():
        m = re.fullmatch(r"(\w+)([+-]\d+)", tok)
        assert m, tok
        out[m.group(1)] = out.get(m.group(1), 0) + int(m.group(2))
    return out


def test_every_card_has_an_expectation():
    assert set(EXPECTED) == set(BY_ID)


def test_deck_shape():
    assert len(DECK) == 102
    for cat in CATEGORIES:
        assert sum(c.cat == cat for c in DECK) == 34
    assert len({c.name_hu for c in DECK}) == len(DECK)
    assert len({c.name_en for c in DECK}) == len(DECK)


@pytest.mark.parametrize("cid", sorted(BY_ID))
def test_card_effect(cid):
    c = BY_ID[cid]
    me, foe = scenario()
    b_me, b_foe = me.stats(), foe.stats()
    play_card_effect(c, me, foe)
    mine_spec, foe_spec = EXPECTED[cid].split("|")
    exp_me, exp_foe = parse(mine_spec), parse(foe_spec)
    exp_me[c.resource] = exp_me.get(c.resource, 0) - c.cost
    for attr in ATTRS:
        assert me.get(attr) - b_me[attr] == exp_me.get(attr, 0), (cid, "me", attr)
        assert foe.get(attr) - b_foe[attr] == exp_foe.get(attr, 0), (cid, "foe", attr)


@pytest.mark.parametrize("cid", sorted(BY_ID))
def test_card_is_well_formed(cid):
    c = BY_ID[cid]
    assert 0 <= c.cost <= 30 and 1 <= c.weight <= 3
    assert c.cat in CATEGORIES
    assert c.ops or c.draw_discard
    for lang in ("hu", "en"):
        txt = card_text(c, lang)
        assert txt and txt[0].isupper() or txt[0].isdigit() or txt[0] in "+\u2212"
        assert "{" not in txt and "}" not in txt
    from tuxomage.resources import ASSETS
    assert (ASSETS / "cardart" / f"{cid}.png").is_file()


def test_card_texts_examples():
    assert card_text(BY_ID["firewall_upgrade"], "hu") == "+6 Tűzfal."
    assert card_text(BY_ID["firewall_upgrade"], "en") == "+6 Firewall."
    assert card_text(BY_ID["tiny_penguin"], "hu") == "2 sebzés. Újra jössz!"
    assert card_text(BY_ID["goodie_bag"], "en") == "If Tower < enemy Tower: +2 Tower, else +1 Tower."
    assert "Nem dobható el" in card_text(BY_ID["pinned_config"], "hu")


# ------------------------------------------------------- conditional branches
def test_other_branches():
    me, foe = scenario()
    me.compiler = 1
    play_card_effect(BY_ID["catch_up_merge"], me, foe)
    assert me.compiler == 3
    me, foe = scenario()
    me.compiler = 1
    play_card_effect(BY_ID["fork_it"], me, foe)
    assert me.compiler == 2
    me, foe = scenario()
    me.wall = 0
    play_card_effect(BY_ID["clean_install"], me, foe)
    assert me.wall == 6
    me, foe = scenario()
    me.colony = 1
    play_card_effect(BY_ID["hackerspace"], me, foe)
    assert me.colony == 2
    me, foe = scenario()
    me.tower = 30
    play_card_effect(BY_ID["goodie_bag"], me, foe)
    assert me.tower == 31
    me, foe = scenario()
    foe.wall = 0
    play_card_effect(BY_ID["port_scanner"], me, foe)
    assert foe.tower == 15
    me, foe = scenario()
    foe.wall = 0
    play_card_effect(BY_ID["rootkit"], me, foe)
    assert foe.tower == 18
    me, foe = scenario()
    me.kernel = 2
    play_card_effect(BY_ID["narwhal"], me, foe)
    assert (foe.wall, foe.tower) == (0, 25)
    me, foe = scenario()
    me.wall = 2
    play_card_effect(BY_ID["snowball_snipers"], me, foe)
    assert (foe.wall, foe.tower) == (2, 25)
    me, foe = scenario()
    me.wall = 2
    play_card_effect(BY_ID["penguin_guard"], me, foe)
    assert foe.wall == 6
    me, foe = scenario()
    foe.wall = 30
    play_card_effect(BY_ID["zero_day"], me, foe)
    assert (foe.wall, foe.tower) == (22, 25)


def test_lowest_hits_both_on_tie_and_self_when_lower():
    me, foe = scenario()
    me.wall = foe.wall = 4
    play_card_effect(BY_ID["flooded_server"], me, foe)
    assert (me.colony, me.tower, foe.colony, foe.tower) == (2, 18, 1, 23)
    me, foe = scenario()
    me.wall = 1
    play_card_effect(BY_ID["flooded_server"], me, foe)
    assert (me.colony, me.tower, foe.colony, foe.tower) == (2, 18, 2, 25)


def test_steal_takes_only_what_exists():
    me, foe = scenario()
    foe.bytes, foe.code = 3, 0
    play_card_effect(BY_ID["packet_sniffer"], me, foe)
    assert (foe.bytes, foe.code) == (0, 0)
    assert (me.bytes, me.code) == (30 - 12 * 0 + 2, 30)   # ceil(3/2) = 2 (cost is penguins)
