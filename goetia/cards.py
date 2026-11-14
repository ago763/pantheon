"""Cartas no estilo das referências: moldura chanfrada, ícone, estrelas e atributos."""

from copy import copy

import pygame

from .catalog import CHARACTERS, ELEMENTS, PASSIVES, SPELLS
from .progression import spell_stats


class Cards:
    def __init__(self, ui):
        self.ui = ui
        self.fonts = {}

    def label(self, surface, text, center, size=18, color="#ffffff", max_width=None):
        while True:
            font = self.fonts.setdefault(size, pygame.font.SysFont("arial", size, bold=True))
            if max_width is None or font.size(text)[0] <= max_width or size <= 11:
                break
            size -= 1
        shadow = font.render(text, True, "#05070c")
        image = font.render(text, True, color)
        surface.blit(shadow, shadow.get_rect(center=(center[0]+1, center[1]+2)))
        surface.blit(image, image.get_rect(center=center))

    def box(self, surface, rect, color, fill):
        pygame.draw.rect(surface, "#080c13", rect.inflate(5, 5), border_radius=9)
        pygame.draw.rect(surface, color, rect, border_radius=7)
        pygame.draw.rect(surface, pygame.Color(color).lerp("white", .32), rect.inflate(-4, -4), 2, border_radius=5)
        pygame.draw.rect(surface, fill, rect.inflate(-10, -10), border_radius=3)
        pygame.draw.line(surface, pygame.Color(color).lerp("white", .6), (rect.x+10, rect.y+5), (rect.right-10, rect.y+5), 1)

    def stats(self, player, choice):
        if choice.kind == "heal":
            return ["VIDA +30", "ATÉ A VIDA MÁXIMA"]
        if choice.kind == "passive":
            item = PASSIVES[choice.key]
            labels = {"damage": "DANO", "area": "ÁREA", "cooldown": "REDUÇÃO DE RECARGA", "magnet": "COLETA",
                      "projectile_speed": "VELOCIDADE DOS TIROS", "critical": "CRÍTICO", "projectiles": "PROJÉTEIS",
                      "duration": "DURAÇÃO", "xp": "EXPERIÊNCIA", "armor": "ARMADURA", "speed": "MOVIMENTO", "regen": "REGENERAÇÃO"}
            value = item["value_per_level"]
            suffix = "" if item["stat"] == "projectiles" else " HP/s" if item["stat"] == "regen" else "%"
            scale = 1 if item["stat"] in ("projectiles", "regen") else 100
            return [labels[item["stat"]], f"+{value*scale:g}{suffix} POR ESTRELA", f"TOTAL +{value*scale*choice.level:g}{suffix}"]
        proposed = copy(player)
        proposed.weapons = dict(player.weapons, **{choice.key: choice.level})
        new = spell_stats(proposed, choice.key)
        if choice.key in player.weapons:
            old = spell_stats(player, choice.key)
            return [f"DANO {old['damage']:.0f} → {new['damage']:.0f}",
                    f"RECARGA {old['cooldown']:.2f} → {new['cooldown']:.2f}s",
                    f"ALCANCE {old['range']:.0f} → {new['range']:.0f}"]
        return [f"DANO {new['damage']:.0f}", f"RECARGA {new['cooldown']:.2f}s", f"ALCANCE {new['range']:.0f}"]

    def draw(self, surface, world):
        w, h = surface.get_size()
        self.label(surface, "SUBIU DE NÍVEL!", (w//2, 39), 38, "#ffce43")
        self.label(surface, "ESCOLHA UMA CARTA · 1 / 2 / 3 / 4", (w//2, 78), 17)
        element = ELEMENTS[CHARACTERS[world.player.character_id]["element"]]
        self.label(surface, f"AFINIDADE: {element['name'].upper()}", (w//2, 103), 13, element["color"])
        count = len(world.choices)
        gap = 16
        cw = min(258, (w-60-gap*(count-1))//count)
        ch = min(440, h-152)
        start = (w-count*cw-(count-1)*gap)//2
        for i, choice in enumerate(world.choices):
            rect = pygame.Rect(start+i*(cw+gap), 128, cw, ch)
            palette = ELEMENTS[choice.element]
            color = palette["color"]
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            self.box(surface, rect, color, "#283446" if hovered else "#1c2431")
            cx, y = rect.centerx, rect.y
            header = pygame.Rect(rect.x+10, y+10, cw-20, 34)
            pygame.draw.rect(surface, palette["dark"], header)
            title = f"{choice.name.upper()} ({'MAX' if choice.level == 6 else 'NV '+str(choice.level)})"
            self.label(surface, title, header.center, 19, max_width=cw-28)
            kind = "MAGIA ATIVA" if choice.kind == "spell" else "ITEM PASSIVO" if choice.kind == "passive" else "RECUPERAÇÃO"
            self.label(surface, kind, (cx, y+61), 15, "#f3db8a")
            panel = pygame.Rect(rect.x+15, y+80, cw-30, 122)
            self.box(surface, panel, color, palette["dark"])
            icon = self.ui.assets.item_icon(choice.key, (96, 96))
            surface.blit(icon, icon.get_rect(center=panel.center))
            self.ui.stars(surface, (cx, y+222), choice.level, 12)
            stats_panel = pygame.Rect(rect.x+12, y+244, cw-24, 89)
            pygame.draw.rect(surface, "#101722", stats_panel)
            pygame.draw.line(surface, "#475467", stats_panel.topleft, stats_panel.topright, 2)
            for line, text in enumerate(self.stats(world.player, choice)):
                self.label(surface, text, (cx, stats_panel.y+17+line*26), 17, max_width=cw-32)
            footer = pygame.Rect(rect.x+12, y+345, cw-24, ch-357)
            pygame.draw.rect(surface, "#121a27", footer)
            if choice.level == 6:
                self.label(surface, "FORMA EVOLUÍDA!", footer.center, 19, "#ff5f67", max_width=cw-32)
            elif choice.kind in ("spell", "passive"):
                partner = (SPELLS[choice.key]["passive"] if choice.kind == "spell" else
                           next(key for key, data in SPELLS.items() if data["passive"] == choice.key))
                partner_name = (PASSIVES if choice.kind == "spell" else SPELLS)[partner]["name"]
                self.label(surface, "EVO:", (cx-36, footer.y+24), 20)
                icon = self.ui.assets.item_icon(partner, (34, 34))
                icon_rect = pygame.Rect(cx+2, footer.y+7, 38, 38)
                self.box(surface, icon_rect, color, palette["dark"])
                surface.blit(icon, icon.get_rect(center=icon_rect.center))
                self.label(surface, partner_name, (cx, footer.bottom-14), 13, max_width=cw-32)
            else:
                self.label(surface, "RECUPERA VIDA", footer.center, 17, max_width=cw-32)
            self.ui.buttons.append((rect, f"choice:{i}"))
