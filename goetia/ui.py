"""Interface: menu, preparação da partida, grimório, cartas e HUD."""

import math
import pygame

from . import config
from .cards import Cards
from .assets import Assets, BOSS_NAMES
from .catalog import CHARACTERS, ELEMENTS, MAPS, PASSIVES, SPELLS, PROGRESSION
from .progression import passive_description, spell_stats, transformation
from .menu_theme import MenuTheme


class UI:
    def __init__(self):
        self.fonts = {}
        self.buttons = []
        self.assets = Assets()
        self.cards = Cards(self)
        self.page = "home"
        self.character_id = "ice_witch"
        self.map_id = "tundra"
        self.duration = 900
        self.book_page = 0
        self.show_fps = False
        self.menu_theme = MenuTheme(self)

    def text(self, surface, text, pos, size=20, color=config.TEXT, center=False):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("georgia", size)
        image = self.fonts[size].render(str(text), True, color)
        rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        surface.blit(image, rect)
        return rect

    def wrapped_text(self, surface, text, rect, size=18, color=config.MUTED):
        font = self.fonts.setdefault(size, pygame.font.SysFont("georgia", size))
        line, y = "", rect.y
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] > rect.width and line:
                self.text(surface, line, (rect.centerx, y), size, color, True)
                y += size+7
                line = word
            else:
                line = candidate
        if line:
            self.text(surface, line, (rect.centerx, y), size, color, True)

    def frame(self, surface, rect, color=config.GOLD, fill=config.PANEL):
        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, color, rect, 1)
        for x, dx in ((rect.left+4, 1), (rect.right-5, -1)):
            for y, dy in ((rect.top+4, 1), (rect.bottom-5, -1)):
                pygame.draw.lines(surface, color, False, [(x, y+dy*12), (x, y), (x+dx*12, y)], 2)

    def button(self, surface, label, rect, action, primary=False, size=19):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        self.frame(surface, rect, config.GOLD, "#51442b" if hover else "#302a20" if primary else "#162332")
        self.text(surface, label, rect.center, size, config.TEXT, True)
        self.buttons.append((rect, action))

    def action_at(self, pos):
        return next((action for rect, action in reversed(self.buttons) if rect.collidepoint(pos)), None)

    def stars(self, surface, center, level, size=9):
        count = 1 if level == 6 else 5
        for i in range(count):
            x = center[0]+(i-(count-1)/2)*(size*2+4)
            y = center[1]
            points = [(x+math.cos(-math.pi/2+j*math.pi/5)*(size if j%2 == 0 else size*.45),
                       y+math.sin(-math.pi/2+j*math.pi/5)*(size if j%2 == 0 else size*.45)) for j in range(10)]
            pygame.draw.polygon(surface, "#ff575e" if level == 6 else "#ffcf57" if i < level else "#48505b", points)

    def draw(self, surface, world):
        self.buttons = []
        if world is None:
            self.draw_menu(surface)
            return
        self.draw_hud(surface, world)
        if world.state == "play":
            return
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((3, 7, 16, 205))
        surface.blit(shade, (0, 0))
        self.buttons = []
        if world.state == "choice":
            self.draw_cards(surface, world)
            return
        w, h = surface.get_size()
        panel = pygame.Rect(w//2-360, h//2-180, 720, 360)
        self.frame(surface, panel)
        title = "Expedição pausada" if world.state == "pause" else "Você resistiu à horda." if world.state == "victory" else "Uma alma retorna ao gelo."
        self.text(surface, title, (w//2, panel.y+65), 32, center=True)
        if world.state != "pause":
            self.text(surface, f"{int(world.elapsed)} segundos · {world.kills} abates · nível {world.player.level}", (w//2, panel.y+120), 21, config.MUTED, True)
        self.button(surface, "CONTINUAR" if world.state == "pause" else "JOGAR NOVAMENTE", pygame.Rect(w//2-150, panel.y+170, 300, 52), "pause" if world.state == "pause" else "start", True)
        self.button(surface, "MENU INICIAL", pygame.Rect(w//2-150, panel.y+245, 300, 48), "home")

    def draw_menu(self, surface):
        if self.page in ('home','select','book'):
            self.menu_theme.draw(surface,self.page)
            return
        w, h = surface.get_size()
        shade = pygame.Surface((w, h), pygame.SRCALPHA)
        shade.fill((3, 7, 14, 175))
        surface.blit(shade, (0, 0))
        if self.page == "home":
            art_width = int(w*.62)
            image = self.assets.menu_background((art_width, int(h*.76)))
            surface.blit(image, (0, h*.1))
            self.text(surface, "ESCOLHA SEU DESTINO", (int(w*.81), int(h*.19)), 20, config.GOLD, True)
            for i, (name, action) in enumerate((("JOGAR", "select"), ("PERSONAGENS", "select"), ("GRIMÓRIO", "book"), ("OPÇÕES", "options"), ("SAIR", "quit"))):
                self.button(surface, name, pygame.Rect(int(w*.65), int(h*.29)+i*62, int(w*.31), 48), action, i == 0)
            self.text(surface, "Um pacto com o inverno. Uma guerra contra a Goetia.", (w//2, h-27), 17, config.GOLD, True)
        elif self.page == "select":
            self.draw_selection(surface)
        elif self.page == "book":
            self.draw_book(surface)
        else:
            self.text(surface, "OPÇÕES", (w//2, 70), 32, config.GOLD, True)
            self.button(surface, "ALTERNAR TELA CHEIA", pygame.Rect(w//2-180, 160, 360, 52), "fullscreen")
            self.button(surface, f"MOSTRAR FPS: {'SIM' if self.show_fps else 'NÃO'}", pygame.Rect(w//2-180, 235, 360, 52), "fps")
            self.text(surface, "WASD / setas: mover · Esc: pausar · 1 / 2 / 3 / 4: escolher carta", (w//2, 345), 18, config.MUTED, True)
            self.text(surface, "Os ajustes de balanceamento ficam em data/balance.json.", (w//2, 385), 17, config.MUTED, True)
            self.button(surface, "VOLTAR", pygame.Rect(w//2-120, h-90, 240, 48), "home")

    def draw_selection(self, surface):
        w, h = surface.get_size()
        self.text(surface, "ESCOLHA SEU MESTRE ELEMENTAL", (w//2, 28), 24, config.GOLD, True)
        card_w = (w-100)//5
        for i, (key, character) in enumerate(CHARACTERS.items()):
            rect = pygame.Rect(30+i*(card_w+10), 57, card_w, 151)
            selected = key == self.character_id
            self.frame(surface, rect, ELEMENTS[character["element"]]["color"] if selected else "#665c48", "#27384a" if selected else "#121c28")
            portrait = self.assets.portrait(key, (68, 89))
            surface.blit(portrait, portrait.get_rect(midtop=(rect.centerx, rect.y+9)))
            self.wrapped_text(surface, character["name"], pygame.Rect(rect.x+5, rect.y+113, rect.w-10, 40), 17)
            self.buttons.append((rect, "character:"+key))
        left = pygame.Rect(30, 226, int(w*.40), h-318)
        right = pygame.Rect(left.right+20, 226, w-left.right-50, h-318)
        self.frame(surface, left)
        self.frame(surface, right)
        char = CHARACTERS[self.character_id]
        portrait = self.assets.portrait(self.character_id, (106, 140))
        surface.blit(portrait, (left.x+18, left.y+22))
        tx = left.x+142
        self.text(surface, char["name"], (tx, left.y+28), 20, ELEMENTS[char["element"]]["color"])
        self.text(surface, f"Vida: {char['hp']}   Velocidade: {char['speed']}", (tx, left.y+66), 15)
        self.wrapped_text(surface, f"Magia inicial: {SPELLS[char['starting_spell']]['name']}", pygame.Rect(tx, left.y+106, left.right-tx-12, 70), 16)
        bonus = f"+{char['damage_bonus']*100:g}% dano" if char["damage_bonus"] else ""
        if char["cooldown_bonus"]:
            bonus += f"  -{char['cooldown_bonus']*100:g}% recarga"
        self.wrapped_text(surface, f"Bônus exclusivo: {bonus.strip()} em {SPELLS[char['buff_spell']]['name']}.", pygame.Rect(left.x+15, left.y+188, left.w-30, 70), 17, config.GOLD)
        self.text(surface, f"Afinidade elemental: peso {PROGRESSION['same_element_weight']:g}× no sorteio", (left.centerx, left.bottom-22), 14, ELEMENTS[char['element']]['color'], True)
        if h >= 700:
            self.wrapped_text(surface, "3 magias do mesmo elemento ativam: "+ELEMENTS[char["element"]]["form"], pygame.Rect(left.x+20, left.y+285, left.w-40, 75), 18, ELEMENTS[char["element"]]["color"])
        self.text(surface, "ESCOLHER MAPA", (right.centerx, right.y+28), 22, config.GOLD, True)
        map_w = (right.w-40)//3
        for i, (key, data) in enumerate(MAPS.items()):
            rect = pygame.Rect(right.x+12+i*(map_w+7), right.y+60, map_w, 145)
            self.frame(surface, rect, config.GOLD if key == self.map_id else "#465466")
            image = pygame.transform.scale(self.assets.ground(key), (map_w-12, 90))
            surface.blit(image, (rect.x+6, rect.y+6))
            self.wrapped_text(surface, data["name"], pygame.Rect(rect.x+4, rect.y+111, rect.w-8, 40), 14)
            self.buttons.append((rect, "map:"+key))
        mode_w = (right.w-32)//3
        for i, (label, seconds) in enumerate((('RÁPIDO · 5 min', 300), ('MÉDIO · 10 min', 600), ('COMPLETO · 15 min', 900))):
            self.button(surface, label, pygame.Rect(right.x+8+i*(mode_w+8), right.y+220, mode_w, 40),
                        f'duration:{seconds}', self.duration == seconds, size=12 if w < 1100 else 16)
        self.text(surface, 'Vitória: derrotar todos os 6 chefes.', (right.centerx, right.y+278), 15, config.GOLD, True)
        self.button(surface, "VOLTAR", pygame.Rect(30, h-70, 160, 44), "home")
        self.button(surface, "INICIAR PARTIDA", pygame.Rect(w-350, h-70, 320, 44), "start", True)

    def draw_cards(self, surface, world):
        self.cards.draw(surface, world)

    def draw_book(self, surface):
        w, h = surface.get_size()
        self.text(surface, "GRIMÓRIO · 15 MAGIAS + 15 PASSIVAS", (w//2, 35), 26, config.GOLD, True)
        entries = list(SPELLS.items())+list(PASSIVES.items())
        cw = (w-80)//3
        ch = (h-160)//2
        for i, (key, data) in enumerate(entries[self.book_page*6:self.book_page*6+6]):
            rect = pygame.Rect(25+(i%3)*(cw+12), 80+(i//3)*(ch+12), cw, ch)
            element = ELEMENTS[data["element"]]
            self.frame(surface, rect, element["color"], element["dark"])
            icon = self.assets.item_icon(key, (58, 58))
            surface.blit(icon, icon.get_rect(midtop=(rect.centerx, rect.top+12)))
            self.wrapped_text(surface, data["name"], pygame.Rect(rect.x+10, rect.top+91, rect.w-20, 55), 19)
            description = data["description"] if key in SPELLS else passive_description(key)
            self.wrapped_text(surface, description, pygame.Rect(rect.x+12, rect.top+140, rect.w-24, 70), 15)
        self.button(surface, "VOLTAR", pygame.Rect(25, h-55, 150, 38), "home", size=16)
        self.button(surface, "ANTERIOR", pygame.Rect(w//2-170, h-55, 140, 38), "book_prev", size=16)
        self.text(surface, f"{self.book_page+1}/5", (w//2, h-36), 17, center=True)
        self.button(surface, "PRÓXIMA", pygame.Rect(w//2+30, h-55, 140, 38), "book_next", size=16)

    def draw_hud(self, surface, world):
        w, h = surface.get_size()
        p = world.player
        strip = pygame.Surface((w, 75), pygame.SRCALPHA)
        strip.fill((5, 10, 18, 205))
        surface.blit(strip, (0, 0))
        pygame.draw.rect(surface, "#213545", (0, 0, w, 5))
        pygame.draw.rect(surface, config.ICE, (0, 0, w*min(1, p.xp/p.xp_required), 5))
        self.text(surface, MAPS[world.map_id]["name"].upper(), (24, 17), 15, config.GOLD)
        self.text(surface, f"NÍVEL {p.level} · XP {int(p.xp)}/{p.xp_required}", (24, 42), 17)
        seconds = int(world.elapsed)
        self.text(surface, f"{seconds//60:02}:{seconds%60:02} / {world.duration//60} min", (w//2, 25), 24, center=True)
        self.text(surface, f'CHEFES {len(world.defeated_bosses)}/6', (w//2, 53), 14, config.GOLD, True)
        self.text(surface, f"ABATES {world.kills}", (w-180, 24), 19)
        bosses = [enemy for enemy in world.enemies if enemy.boss_index is not None]
        if bosses:
            boss = min(bosses, key=lambda enemy: enemy.pos.distance_squared_to(p.pos))
            self.text(surface, BOSS_NAMES[boss.boss_index].upper(), (w//2, 87), 18, config.GOLD, True)
            pygame.draw.rect(surface, "#281b2e", (w//2-180, 105, 360, 10))
            pygame.draw.rect(surface, "#b74d96", (w//2-180, 105, 360*max(0, boss.hp)/boss.max_hp, 10))
        for row, inventory in enumerate((p.weapons, p.passives)):
            self.text(surface, "MAGIAS" if row == 0 else "PASSIVAS", (22, h-137+row*60), 12, config.MUTED)
            items = list(inventory.items())
            for i in range(4):
                rect = pygame.Rect(95+i*61, h-148+row*60, 54, 54)
                self.frame(surface, rect, "#526276")
                if i < len(items):
                    key, level = items[i]
                    icon = self.assets.item_icon(key, (33, 33))
                    surface.blit(icon, (rect.x+10, rect.y+3))
                    self.stars(surface, (rect.centerx, rect.bottom-9), level, 3)
        self.text(surface, f"VIDA {max(0, int(p.hp))}/{int(p.max_hp)}", (22, h-172), 17)
        form = transformation(p)
        if form:
            self.text(surface, ELEMENTS[form]["form"], (w//2, h-27), 19, ELEMENTS[form]["color"], True)
        if world.state == "play":
            self.button(surface, "Pausar", pygame.Rect(w-140, h-70, 110, 42), "pause", size=17)
