"""Carrega as folhas originais e recorta quadros em memória, sem alterá-las."""

from pathlib import Path
import math

import pygame
from .catalog import CHARACTERS, MAPS, PASSIVES, SPELLS
from .animation import ANIMATIONS, frame_index

ROOT = Path(__file__).resolve().parent.parent / "assets"
BOSS_NAMES = ("Belzebu", "Barbatos", "Morax", "Buer", "Haborym", "Focalors")


class Assets:
    def __init__(self):
        self.sheets = {}
        self.cache = {}

    def sheet(self, name):
        if name not in self.sheets:
            self.sheets[name] = pygame.image.load(str(ROOT / name)).convert_alpha()
        return self.sheets[name]

    def crop(self, name, rect, size, checker=False, flip=False):
        key = (name, tuple(rect), tuple(size), checker, flip)
        if key not in self.cache:
            image = self.sheet(name).subsurface(rect).copy()
            if checker:
                # As folhas do DOCX têm um xadrez cinza incorporado, sem alpha.
                # Chave de cor apenas no recorte; preserva as cores dos sprites.
                for y in range(image.get_height()):
                    for x in range(image.get_width()):
                        color = image.get_at((x, y))
                        high = max(color.r, color.g, color.b)
                        low = min(color.r, color.g, color.b)
                        if checker in ("glow", "darkglow", "brightglow"):
                            alpha = max(0, min(255, (high-85)*3))
                            if checker == "darkglow":
                                alpha = max(0, min(255, (high-low-10)*6))
                            if checker == "brightglow":
                                alpha = max(0, min(255, (high-155)*3))
                            if high-low < 8 and high < 150:
                                alpha = 0
                            edge = min(x, y, image.get_width()-1-x, image.get_height()-1-y)
                            alpha = int(alpha*min(1, edge/6))
                            image.set_at((x, y), (color.r, color.g, color.b, alpha))
                        elif name.endswith("image10.png"):
                            # Não confundir o sobretudo azul quase preto com o xadrez neutro.
                            if high-low < 5 and 25 <= high < 105:
                                image.set_at((x, y), (0, 0, 0, 0))
                        elif high-low < (5 if checker == "darkmask" else 17) and high < 105:
                            image.set_at((x, y), (0, 0, 0, 0))
            image = pygame.transform.scale(image, size)
            if flip:
                image = pygame.transform.flip(image, True, False)
            self.cache[key] = image
        return self.cache[key]

    def witch(self, moving, elapsed, facing):
        frames = [(24, 265, 88, 98), (121, 265, 88, 98)]
        if moving:
            frames = [(252, 265, 82, 98), (341, 265, 78, 98),
                      (426, 265, 83, 98), (517, 265, 82, 98)]
        rect = frames[int(elapsed * (8 if moving else 3)) % len(frames)]
        return self.crop("references/image10.png", rect, (64, 72), True, facing < 0)

    def enemy(self, tank, elapsed):
        frames = ([(231, 299, 137, 137), (458, 299, 134, 137), (684, 299, 139, 137)]
                  if tank else [(62, 137, 175, 117), (314, 137, 163, 117),
                                (559, 125, 146, 131), (785, 150, 180, 106)])
        return self.crop("references/image12.png", frames[int(elapsed*7) % len(frames)],
                         (68, 72) if tank else (52, 40), True)

    def common_enemy(self, kind, elapsed):
        if kind in ("moth", "tank"):
            return self.enemy(kind == "tank", elapsed)
        if kind == "eye":
            rect = (231+int(elapsed*5)%3*215, 474, 150, 90)
            size = (53, 36)
        else:
            rect = (76+int(elapsed*5)%2*196, 628, 116, 110)
            size = (40, 40)
        return self.crop("references/image12.png", rect, size, True)

    def boss_attack(self, key, size=None):
        keys = ["beel_slash", "beel_grid", "beel_swarm", "bar_tornado", "bar_spiral", "bar_sound",
                "mor_meteor", "mor_wall", "mor_spears", "buer_roots", "buer_spores", "buer_laser",
                "hab_embers", "hab_lava", "hab_fireballs", "foc_mirror", "foc_jet", "foc_bubbles"]
        if key in ("moth", "eye"):
            return self.crop("references/image12.png", (159 if key == "moth" else 388, 877, 85, 85), size or (85,85), True)
        if key == "bomb":
            return self.crop("references/image12.png", (817, 603, 190, 145), size or (190,145), True)
        index = keys.index(key)
        rects = [
            (166, 67, 94, 87), (281, 67, 85, 87), (390, 67, 90, 87),
            (674, 67, 82, 87), (780, 67, 96, 87), (895, 67, 113, 87),
            (170, 225, 89, 90), (275, 225, 94, 90), (397, 225, 86, 90),
            (674, 225, 100, 90), (783, 225, 97, 90), (900, 225, 108, 90),
            (166, 403, 89, 101), (271, 403, 107, 101), (389, 403, 97, 101),
            (674, 403, 99, 101), (786, 403, 96, 101), (904, 403, 104, 101),
        ]
        # Recorta apenas os efeitos; as colunas dos corpos dos chefes são ignoradas.
        return self.crop("images/boss-attacks.png", rects[index], size or rects[index][2:], True)

    def boss(self, index, elapsed, side=False, flip=False):
        name = "images/bosses-side.png" if side else "images/bosses-front.png"
        return self.crop(name, (int(elapsed*6) % 4*256, index*256, 256, 256), (144, 144), flip=flip)

    def zone(self, stage, elapsed):
        sheet = self.sheet("images/beelzebul-lightning-zone.png")
        # Folha: quatro colunas, três faixas (piso, raio, impacto).
        boundaries = [0, round(sheet.get_height()*.36), round(sheet.get_height()*.76), sheet.get_height()]
        col = int(elapsed*9) % 4
        x1, x2 = round(col*sheet.get_width()/4), round((col+1)*sheet.get_width()/4)
        rect = (x1, boundaries[stage], x2-x1, boundaries[stage+1]-boundaries[stage])
        size = ((220, 145), (90, 156), (104, 70))[stage]
        return self.crop("images/beelzebul-lightning-zone.png", rect, size)

    def ground(self, map_id="tundra"):
        return self.crop("references/image3.png", MAPS[map_id]["rect"], (384, 384))

    def portrait(self, character_id="ice_witch", size=(152, 200)):
        x = (72, 337, 604, 870, 1137)[CHARACTERS[character_id]["portrait_index"]]
        return self.crop("references/image11.png", (x, 414, 240, 316), size)

    def character(self, character_id, moving, elapsed, facing=1):
        if character_id == "ice_witch":
            return pygame.transform.scale(self.witch(moving, elapsed, facing), (64, 64))
        strips = {
            "shadow_monarch": ([(730, 266, 85, 101), (825, 266, 86, 101)],
                               [(950, 266, 78, 101), (1040, 266, 77, 101), (1125, 266, 76, 101), (1213, 266, 79, 101)]),
            "light_elf": ([(25, 420, 85, 91), (123, 420, 84, 91)],
                          [(254, 420, 79, 91), (342, 420, 78, 91), (428, 420, 80, 91), (518, 420, 77, 91)]),
            "flame_pirate": ([(24, 546, 86, 85), (124, 546, 83, 85)],
                             [(254, 546, 80, 85), (344, 546, 78, 85), (430, 546, 77, 85), (519, 546, 76, 85)]),
            "lightning_assassin": ([(25, 669, 83, 85), (125, 669, 82, 85)],
                                   [(254, 669, 79, 85), (342, 669, 78, 85), (430, 669, 77, 85), (519, 669, 76, 85)]),
        }
        frames = strips[character_id][int(moving)]
        rect = frames[int(elapsed*(8 if moving else 3)) % len(frames)]
        return self.crop("references/image10.png", rect, (64, 64), True, facing < 0)

    def item_icon(self, key, size=(56, 56)):
        if key in SPELLS:
            element_order = ("ice", "dark", "light", "lightning", "fire")
            row = element_order.index(SPELLS[key]["element"])
            column = [k for k, value in SPELLS.items() if value["element"] == SPELLS[key]["element"]].index(key)
            x = (185, 340, 500)[column]
            y = (60, 209, 355, 480, 632)[row]
            return self.crop("references/image9.png", (x, y, 100, 78 if row == 2 else 100), size, True)
        if key == "heal":
            return self.crop("references/image7.png", (80, 530, 120, 173), size, True)
        item = PASSIVES[key]
        x = (41, 205, 380)[item["icon_column"]]
        y = (92, 232, 370, 509, 640)[item["icon_row"]]
        return self.crop("references/image5.png", (x, y, 100, 96), size, True)

    def magic(self, key, size, age=0, frame=None):
        sequence = ANIMATIONS[key]
        if frame is None:
            frame = frame_index(age, SPELLS[key]["animation_fps"], len(sequence["frames"]))
        if sequence.get("erase_labels"):
            # Remove somente o número impresso no canto do recorte, antes de escalar.
            rect = sequence["frames"][frame]
            cache_key = ("animation", key, frame, tuple(size))
            if cache_key not in self.cache:
                image = self.crop(sequence["sheet"], rect, rect[2:], sequence.get("checker", True)).copy()
                for mask in sequence["erase_labels"][frame]:
                    image.fill((0, 0, 0, 0), mask)
                image = pygame.transform.scale(image, size)
                if sequence.get("flip", False):
                    image = pygame.transform.flip(image, True, False)
                self.cache[cache_key] = image
            return self.cache[cache_key]
        return self.crop(sequence["sheet"], sequence["frames"][frame], size,
                         sequence.get("checker", True), sequence.get("flip", False))

    def directed_magic(self, key, size, angle, age=0, frame=None):
        sequence = ANIMATIONS[key]
        if frame is None:
            frame = frame_index(age, SPELLS[key]['animation_fps'], len(sequence['frames']))
        rect = sequence['frames'][frame]
        image = self.magic(key, rect[2:], age, frame)
        native = sequence.get('native_angles', [0]*len(sequence['frames']))[frame]
        if key == 'static_needles' and frame == 0:
            # A primeira referência tem duas agulhas em sentidos opostos.
            # Alinhe cada uma antes de montar o conjunto, preservando ambas.
            image = pygame.Surface((150, 86), pygame.SRCALPHA)
            for source, rotation, y in (((0, 18, 83, 78), 140, 0), ((83, 18, 94, 88), -40, 43)):
                part = self.crop(sequence['sheet'], source, source[2:], True)
                part = pygame.transform.rotate(part, rotation)
                part = part.subsurface(part.get_bounding_rect())
                image.blit(pygame.transform.scale(part, (150, 36)), (0, y))
            native = 0
        image = pygame.transform.rotate(image, native)
        bounds = image.get_bounding_rect()
        if bounds.width and bounds.height:
            image = image.subsurface(bounds)
        image = pygame.transform.scale(image, size)
        return pygame.transform.rotate(image, -angle)

    def directed_boss(self, key, size, angle, preserve_aspect=False):
        native = {'beel_slash': 35, 'mor_meteor': 45, 'mor_spears': 45,
                  'buer_laser': 32, 'hab_embers': 50, 'hab_fireballs': 45,
                  'foc_jet': 40}.get(key, 0)
        image = pygame.transform.rotate(self.boss_attack(key), native)
        bounds = image.get_bounding_rect()
        if bounds.width and bounds.height:
            image = image.subsurface(bounds)
        if preserve_aspect:
            size = (size[0], max(1, round(image.get_height()*size[0]/image.get_width())))
        image = pygame.transform.scale(image, size)
        return pygame.transform.rotate(image, -angle)

    def orbit_path(self, size, age):
        frames = [(52, 580, 540, 240), (614, 567, 549, 253)]
        index = frame_index(age, SPELLS["storm_orbs"]["animation_fps"], len(frames))
        return self.crop("images/storm-orbs.png", frames[index], size)

    def ice_marker(self, size, age):
        rects = [(14, 7, 91, 87), (8, 129, 111, 113)]
        return self.crop('images/ice-marker.png', rects[frame_index(age, 6, 2)], size, True)

    def water_mirror(self, size, age, projectile=False, flip=False):
        frame = frame_index(age, 8, 4)
        x1, x2 = round(frame*1774/4), round((frame+1)*1774/4)
        rect = (x1, 660 if projectile else 50, x2-x1, 170 if projectile else 520)
        return self.crop('images/focalors-mirrors.png', rect, size, flip=flip)

    def ice_ring(self, size, age):
        frame = frame_index(age, SPELLS['ice_age']['animation_fps'], len(ANIMATIONS['ice_age']['frames']))
        thickness = max(.1, min(1, SPELLS['ice_age'].get('ring_thickness', .45)))
        key = ('thin_ice_ring', tuple(size), frame, thickness)
        if key not in self.cache:
            source = self.magic('ice_age', size, age, frame)
            result = pygame.Surface(size, pygame.SRCALPHA)
            cx, cy = (size[0]-1)/2, (size[1]-1)/2
            # Compress radial thickness toward the outer edge without shrinking diameter.
            for y in range(size[1]):
                for x in range(size[0]):
                    dx, dy = (x-cx)/cx, (y-cy)/cy
                    radius = math.hypot(dx, dy)
                    original_radius = 1-(1-radius)/thickness
                    if radius == 0 or original_radius < 0:
                        continue
                    sx = round(cx+dx/radius*original_radius*cx)
                    sy = round(cy+dy/radius*original_radius*cy)
                    if 0 <= sx < size[0] and 0 <= sy < size[1]:
                        result.set_at((x,y), source.get_at((sx,sy)))
            self.cache[key] = result
        return self.cache[key]

    def orbit_link(self, size, age):
        rects = [(31, 397, 269, 76), (328, 397, 269, 76),
                 (623, 397, 269, 76), (910, 397, 269, 76)]
        index = frame_index(age, SPELLS["storm_orbs"]["animation_fps"], len(rects))
        return self.crop("images/storm-orbs.png", rects[index], size)

    def menu_background(self, size):
        # Título e ilustração da referência, sem seus botões impressos.
        return self.crop("images/menu-reference.png", (38, 49, 664, 415), size)

    def dragon(self):
        return self.crop("references/image1.jpeg", (40, 99, 905, 144), (156, 30), True, True)

    def pickup(self, value):
        rect = (80, 530, 120, 173) if value == 0 else (651, 151, 104, 148) if value >= 5 else (125, 176, 74, 99)
        return self.crop("references/image7.png", rect, (20, 27) if value == 0 else (15, 22), True)

    def card_icon(self, key):
        if key == "weapon":
            return self.crop("references/image1.jpeg", (42, 102, 240, 140), (72, 42), True)
        if key == "health":
            return self.crop("references/image7.png", (80, 530, 120, 173), (37, 52), True)
        rect = {"damage": (48, 94, 84, 96), "speed": (219, 513, 88, 87),
                "cooldown": (390, 93, 70, 98)}[key]
        return self.crop("references/image5.png", rect, (48, 52), True)
