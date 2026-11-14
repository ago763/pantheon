"""Inventário 4+4, cartas, cinco estrelas e evoluções com a passiva correta."""

from collections import Counter
from dataclasses import dataclass

from .catalog import CHARACTERS, ELEMENTS, PASSIVES, SPELLS, PROGRESSION


@dataclass(frozen=True)
class Upgrade:
    key: str
    kind: str
    level: int
    name: str
    description: str
    element: str


def transformation(player):
    counts = Counter(SPELLS[key]["element"] for key in player.weapons)
    return next((element for element, count in counts.items() if count >= 3), None)


def modifiers(player):
    result = {key: 0.0 for key in ("damage", "area", "cooldown", "magnet", "projectile_speed",
                                  "critical", "projectiles", "duration", "xp", "armor", "speed", "regen")}
    for key, level in player.passives.items():
        item = PASSIVES[key]
        result[item["stat"]] += item["value_per_level"] * level
    form = transformation(player)
    if form:
        for key, value in ELEMENTS[form]["bonus"].items():
            if key in result:
                result[key] += value
    return result


def spell_stats(player, key):
    data = SPELLS[key]
    level = player.weapons.get(key, 1)
    steps = min(5, level)-1
    stats = dict(data)
    mod = modifiers(player)
    char = CHARACTERS[player.character_id]
    buff = char["buff_spell"] == key
    stats["damage"] *= (1+steps*data["damage_per_level"])*(1+mod["damage"])
    stats["damage"] *= 1+char["damage_bonus"] if buff else 1
    stats["cooldown"] *= max(.2, 1-steps*data["cooldown_per_level"])*max(.2, 1-mod["cooldown"])
    if buff:
        stats["cooldown"] *= 1-char["cooldown_bonus"]
    stats["range"] *= 1+steps*data["range_per_level"]
    stats["radius"] *= 1+mod["area"]
    stats["projectile_speed"] *= 1+mod["projectile_speed"]
    stats["duration"] *= 1+mod["duration"]
    stats["projectiles"] += int(mod["projectiles"])
    if key == 'punishment':
        stats['projectiles'] = data['beams_by_level'][min(5, level)-1]
    if level == 6:
        stats["damage"] *= data["evolution_multiplier"]
        stats["radius"] *= 1.35
        stats["cooldown"] *= .75
    return stats


def available_upgrades(player):
    cards = []
    for key, data in SPELLS.items():
        level = player.weapons.get(key, 0)
        if level == 0 and len(player.weapons) >= 4:
            continue
        if level < 5:
            cards.append(Upgrade(key, "spell", level+1, data["name"], data["description"], data["element"]))
        elif level == 5 and data["passive"] in player.passives:
            cards.append(Upgrade(key, "spell", 6, data["evolution"], "Evolução suprema: amplia dano, área e frequência.", data["element"]))
    for key, data in PASSIVES.items():
        level = player.passives.get(key, 0)
        if level == 0 and len(player.passives) >= 4:
            continue
        if level < data["max_level"]:
            cards.append(Upgrade(key, "passive", level+1, data["name"], passive_description(key), data["element"]))
    if not cards:
        cards.append(Upgrade("heal", "heal", 1, "Recuperar vida", "Recupera 30 de vida. Inventário no máximo.", "light"))
    return cards


def passive_description(key):
    item = PASSIVES[key]
    labels = {"damage": "dano", "area": "área", "cooldown": "redução de recarga", "magnet": "alcance de coleta",
              "projectile_speed": "velocidade dos projéteis", "critical": "chance crítica", "projectiles": "projétil por ataque",
              "duration": "duração", "xp": "XP recebido", "armor": "redução de dano", "speed": "velocidade", "regen": "vida por segundo"}
    value = item["value_per_level"]
    amount = f"{value:g}" if item["stat"] in ("projectiles", "regen") else f"{value*100:g}%"
    return f"+{amount} de {labels[item['stat']]} por estrela."


def apply_upgrade(player, upgrade):
    if upgrade.kind == "heal" and upgrade.key == "heal":
        player.hp = min(player.max_hp, player.hp+30)
        return
    # Valida de novo: evita cartas obsoletas e inventários acima do limite.
    legal = {(card.kind, card.key, card.level) for card in available_upgrades(player)}
    if (upgrade.kind, upgrade.key, upgrade.level) not in legal:
        return
    if upgrade.kind == "spell":
        player.weapons[upgrade.key] = upgrade.level
    elif upgrade.kind == "passive":
        player.passives[upgrade.key] = upgrade.level
    else:
        player.hp = min(player.max_hp, player.hp+30)


def draw_upgrades(player, rng):
    """Afinidade elemental e sorteio sem repetir a mesma melhoria."""
    pool = available_upgrades(player)
    selected = []
    element = CHARACTERS[player.character_id]["element"]
    while pool and len(selected) < PROGRESSION["choices_per_level"]:
        weights = [PROGRESSION["same_element_weight"] if card.element == element else 1 for card in pool]
        index = rng.choices(range(len(pool)), weights=weights, k=1)[0]
        selected.append(pool.pop(index))
    # Quando não restam quatro melhorias legais, preenche com recuperação de vida.
    while len(selected) < PROGRESSION["choices_per_level"]:
        selected.append(Upgrade("heal", "heal", 1, "Recuperar vida", "Recupera 30 de vida.", "light"))
    return selected
