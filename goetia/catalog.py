"""Dados de balanceamento. Edite data/balance.json e reinicie o jogo."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "balance.json"
DATA = json.loads(DATA_PATH.read_text(encoding="utf-8"))
SPELLS = DATA["spells"]
PASSIVES = DATA["passives"]
CHARACTERS = DATA["characters"]
MAPS = DATA["maps"]
ELEMENTS = DATA["elements"]
BOSS_ATTACKS = DATA["boss_attacks"]
ENEMIES = DATA["enemies"]
BOSS_SETTINGS = DATA["boss_settings"]
PROGRESSION = DATA["progression"]

assert len(SPELLS) == 15 and len(PASSIVES) == 15
assert all(spell["passive"] in PASSIVES for spell in SPELLS.values())
