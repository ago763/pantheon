"""Camadas elementais ancoradas nos pés; o sprite-base não é substituído."""

import math
import pygame
from pygame import Vector2

from .catalog import CHARACTERS, ELEMENTS
from .animation import frame_index


class TransformationRenderer:
    def __init__(self, assets):
        self.assets = assets

    def draw_light_trail(self, surface, points, offset, elapsed):
        if len(points) < 2:
            return
        settings = ELEMENTS['light']['trail']
        width = settings.get('ribbon_width',14)
        layer = pygame.Surface(surface.get_size(),pygame.SRCALPHA)
        pulse = .9+.1*math.sin(elapsed*6)
        for size,color,alpha in [(width+10,(255,195,55),65),(width,(255,220,100),210),(max(2,width//3),(255,255,215),255)]:
            for i in range(1,len(points)):
                a,b = points[i-1],points[i]
                fade = min(1,(settings['duration']-a.age)/.6)*min(1,i/6)
                start,end = a.pos+offset,b.pos+offset
                rgba=(*color,round(alpha*fade*pulse))
                pygame.draw.line(layer,rgba,start,end,size)
                pygame.draw.circle(layer,rgba,end,max(1,size//2))
        surface.blit(layer,(0,0))
        # A single animated artwork tip, rather than repeated arrow stamps.
        frame=frame_index(elapsed,ELEMENTS['light']['animation_fps'],4)
        rects=[(22,838,135,94),(174,838,147,94),(333,838,151,94),(497,838,157,94)]
        rect=rects[frame]
        tip=self.assets.crop('references/image13.png',rect,rect[2:],'brightglow')
        tip=pygame.transform.rotate(tip,30)
        tip=pygame.transform.scale(tip,(42,26))
        delta=points[-1].pos-points[-2].pos
        tip=pygame.transform.rotate(tip,-math.degrees(math.atan2(delta.y,delta.x)))
        tip.set_alpha(round(255*min(1,(settings['duration']-points[-1].age)/.6)))
        surface.blit(tip,tip.get_rect(center=points[-1].pos+offset))

    def draw_footprint(self, surface, footprint, offset):
        settings = ELEMENTS[footprint.element]['trail']
        frame = frame_index(footprint.age,ELEMENTS[footprint.element]['animation_fps'],4)
        if footprint.element == 'ice':
            sheet = 'images/form-ice.png'
            rects = [(47,405,195,130),(280,402,222,133),(539,402,218,133),(777,402,218,133)]
        elif footprint.element == 'fire':
            sheet = 'references/image4.jpeg'
            rects = [(442,827,96,55),(568,827,100,55),(442,890,100,65),(568,890,100,65)]
        elif footprint.element == 'light':
            sheet = 'references/image13.png'
            rects = [(22,838,135,94),(174,838,147,94),(333,838,151,94),(497,838,157,94)]
        else:
            sheet = 'images/lightning-afterimages.png'
            rects = [(18,75,58,68),(78,75,58,68),(139,75,58,68),(199,75,58,68)]
        image = self.assets.crop(sheet,rects[frame],(settings['width'],settings['height']),'glow',footprint.facing < 0).copy()
        image.set_alpha(round(255*min(1,(settings['duration']-footprint.age)/.6)))
        rect = image.get_rect(midbottom=footprint.pos+offset) if footprint.element == 'lightning' else image.get_rect(center=footprint.pos+offset)
        surface.blit(image,rect)

    def draw(self, surface, element, character_id, feet, elapsed, layer, sprite=None):
        if element is None:
            return
        character = CHARACTERS[character_id]
        feet = Vector2(feet)
        head = feet+Vector2(character["head_offset"])
        back = feet+Vector2(character["back_offset"])
        ground = feet+Vector2(character["feet_offset"])
        # As sequências de rastro destas folhas possuem quatro recortes reais.
        frame = frame_index(elapsed, ELEMENTS[element]["animation_fps"], 4)
        color = ELEMENTS[element]["color"]

        def blit(sheet, rect, size, center, flip=False, opacity=255):
            mode = "darkglow" if sheet == "image8.png" else "brightglow" if sheet == "image13.png" else "glow"
            source = sheet if "/" in sheet else "references/"+sheet
            image = self.assets.crop(source, rect, size, mode, flip)
            if opacity != 255:
                image = image.copy()
                image.set_alpha(opacity)
            surface.blit(image, image.get_rect(center=center))

        def animated_halo(sheet, rect, size):
            # Animate the supplied single halo artwork; no invented sprite-sheet frames.
            halo_settings = ELEMENTS[element].get('halo', {})
            amplitude = halo_settings.get('float_height', 2)
            center = head+Vector2(0, math.sin(elapsed*3)*amplitude)
            pulse = (0, 1, 2, 1)[frame]
            animated_size = (size[0]+pulse*2, size[1]+pulse)
            blit(sheet, rect, animated_size, center, opacity=(215,235,255,235)[frame])
            for i in range(3):
                angle = elapsed*2+i*math.tau/3
                spark = center+Vector2(math.cos(angle)*animated_size[0]*.55,
                                      math.sin(angle)*animated_size[1]*.4)
                pygame.draw.rect(surface, color, (round(spark.x),round(spark.y),2,2))

        if layer == "back":
            if element == "ice":
                pass  # Persistent ground footprints are rendered by the world.
            elif element == "dark":
                blit("image8.png", (28+frame*134, 838, 120, 98), (86, 42), ground)
            elif element == "light":
                # Asas recortadas separadamente, sem o boneco preto da referência.
                width = 48
                shift = 0
                blit("image13.png", (697, 802, 77, 103), (width, 62), back+(-32, -4+shift))
                blit("image13.png", (697, 802, 77, 103), (width, 62), back+(32, -4+shift), True)
            elif element == "fire":
                height = 69
                blit("image4.jpeg", (730, 791, 59, 126), (33, height), back+(-25, 5))
                blit("image4.jpeg", (730, 791, 59, 126), (33, height), back+(25, 5), True)
            elif element == "lightning":
                pygame.draw.ellipse(surface, color, (ground.x-35, ground.y-9, 70, 18), 1)
        else:
            if element == "ice":
                rects = [(64, 137, 160, 148), (309, 137, 160, 148),
                         (552, 130, 169, 164), (798, 130, 170, 164)]
                blit("images/form-ice.png", rects[frame], (45, 33), head+(0, math.sin(elapsed*3)*2))
            elif element == "dark":
                animated_halo("image8.png", (710, 725, 128, 77), (48, 29))
            elif element == "light":
                animated_halo("image13.png", (760, 768, 78, 39), (37, 18))
            elif element == "lightning" and sprite is not None:
                outline = pygame.mask.from_surface(sprite).connected_component().outline(3)
                top_left = feet-Vector2(32, 64)
                if len(outline) > 2:
                    pygame.draw.lines(surface, color, True, [top_left+Vector2(point) for point in outline], 1)
                for side in (-1, 1):
                    x = back.x+side*30
                    jitter = math.sin(elapsed*16)*3
                    pygame.draw.lines(surface, "#c7faff", False, [(x, back.y-22), (x+side*6, back.y-8),
                        (x-side*4+jitter, back.y+4), (x+side*4, back.y+22)], 2)
            elif element == "fire":
                for i in range(6):
                    angle = elapsed*2+i*math.tau/6
                    pos = back+Vector2(math.cos(angle)*33, math.sin(angle)*24)
                    pygame.draw.rect(surface, color, (*pos, 2, 3))
