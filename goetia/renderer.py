"""Desenha a arena usando as artes do documento e as folhas enviadas."""

import math

import pygame
from pygame import Vector2

from . import config
from .assets import Assets
from .animation import projectile_frame
from .catalog import SPELLS, BOSS_ATTACKS
from .progression import transformation
from .progression import spell_stats
from .transformations import TransformationRenderer


def diamond(surface, color, pos, radius):
    x, y = pos
    pygame.draw.polygon(surface, color, [
        (x, y - radius), (x + radius * 0.65, y),
        (x, y + radius), (x - radius * 0.65, y),
    ])


class Renderer:
    def __init__(self):
        self.assets = Assets()
        self.transformations = TransformationRenderer(self.assets)

    def draw(self, surface, world):
        surface.fill(config.BACKGROUND)
        width, height = surface.get_size()
        center = Vector2(width / 2, height / 2)
        camera = world.player.pos if world else Vector2()
        offset = center - camera
        self.draw_ground(surface, camera, offset, world.map_id if world else "tundra")
        if world is None:
            return

        self.draw_hostile_attacks(surface, world, offset)
        self.transformations.draw_light_trail(surface,world.light_trail,offset,world.elapsed)
        for footprint in world.footprints:
            self.transformations.draw_footprint(surface,footprint,offset)

        for area in world.combat.areas:
            key = area.spell_id
            mechanic = SPELLS[key]["mechanic"]
            if mechanic == 'beam':
                continue  # These effects are drawn in front of enemy sprites below.
            pos = area.pos+offset
            if mechanic == 'ice_rain':
                stats = spell_stats(world.player, key)
                radius = max(12, int(area.radius))
                marker = self.assets.ice_marker((radius*2, max(1, int(radius*1.1))), area.age)
                surface.blit(marker, marker.get_rect(center=pos))
                falling_age = area.age-stats['warning']
                if falling_age >= 0:
                    progress = min(1, falling_age/stats['fall_duration'])
                    # Four authored frames: launch, descent, contact, dissipation.
                    frame = min(3, int(progress*3))
                    if progress == 1:
                        frame = 3
                    image = self.assets.directed_magic(key, (88, 30), 90, area.age, frame)
                    if progress == 1:
                        fade = max(0, 1-(falling_age-stats['fall_duration'])/stats['impact_duration'])
                        image.set_alpha(int(255*fade))
                    height = stats['fall_height']*(1-progress)
                    for dx, dy in ((-.5, -.1), (0, .2), (.5, -.1)):
                        anchor = pos+Vector2(dx*radius, dy*radius-height)
                        surface.blit(image, image.get_rect(midbottom=anchor))
                continue
            if mechanic == "orbit":
                points = world.combat.orbit_points(area)
                if key == "storm_orbs":
                    stats = spell_stats(world.player, key)
                    path_size = (int(stats["range"]*2), int(stats["range"]*stats["orbit_vertical_scale"]*2))
                    path = self.assets.orbit_path(path_size, world.elapsed)
                    origin = world.player.pos+Vector2(0, stats["orbit_center_y"])+offset
                    surface.blit(path, path.get_rect(center=origin))
                    if world.player.weapons[key] == 6:
                        for i, point in enumerate(points):
                            other = points[(i+1)%len(points)]
                            delta = other-point
                            link = self.assets.orbit_link((max(1, int(delta.length())), 12), world.elapsed)
                            link = pygame.transform.rotate(link, -math.degrees(math.atan2(delta.y, delta.x)))
                            surface.blit(link, link.get_rect(center=(point+other)/2+offset))
                for point in points:
                    image = self.assets.magic(key, (36, 36), world.elapsed if key == "storm_orbs" else area.age)
                    surface.blit(image, image.get_rect(center=point+offset))
                continue
            radius = max(12, int(area.radius))
            size = (radius*2, radius*2)
            if mechanic == "beam":
                size = (radius*2, radius*3)
            if mechanic == "cone":
                size = (int(SPELLS[key]["range"]), radius*2)
                pos += Vector2(math.cos(area.angle), math.sin(area.angle))*size[0]/2
            image = self.assets.magic(key, size, area.age)
            if key == 'ice_age':
                image = self.assets.ice_ring(size, area.age)
            if mechanic in ("cone", "whip", "fireball"):
                image = self.assets.directed_magic(key, size, math.degrees(area.angle), area.age)
            if mechanic == 'whip':
                frame = min(3,int(area.age/(area.duration/4)))
                image = self.assets.directed_magic(key,(radius*2,int(radius*1.2)),math.degrees(area.angle),area.age,frame)
            surface.blit(image, image.get_rect(midbottom=pos+(0, radius/2)) if mechanic == "beam" else image.get_rect(center=pos))

        for zone in world.lightning_zones:
            pos = zone.pos + offset
            image = self.assets.zone(0, zone.age)
            image = pygame.transform.scale_by(image, zone.scale)
            surface.blit(image, image.get_rect(center=pos))
            if zone.age < zone.warning:
                points = [pos+Vector2(p)*zone.scale for p in [(-78, -42), (78, -42), (105, 42), (-105, 42)]]
                pygame.draw.polygon(surface, "#efb4ff", points, 2)
            elif zone.age < zone.warning + zone.active:
                for dx, dy in ((-60, -15), (0, 0), (60, 15)):
                    ray = self.assets.zone(1, zone.age)
                    ray = pygame.transform.scale_by(ray, zone.scale)
                    surface.blit(ray, ray.get_rect(midbottom=pos+Vector2(dx, dy+20)*zone.scale))
            else:
                impact = self.assets.zone(2, zone.age)
                impact = pygame.transform.scale_by(impact, zone.scale)
                surface.blit(impact, impact.get_rect(center=pos))

        for pickup in world.pickups:
            image = self.assets.pickup(pickup.value)
            surface.blit(image, image.get_rect(center=pickup.pos+offset))
        for enemy in world.enemies:
            pos = enemy.pos + offset
            x, y = pos
            radius = enemy.radius
            pygame.draw.ellipse(surface, "#09121c", (x-radius, y+radius-5, radius*2, 10))
            if enemy.boss_index is not None:
                image = self.assets.boss(enemy.boss_index, world.elapsed)
                rect = image.get_rect(midbottom=(x, y+38))
            else:
                image = self.assets.common_enemy(enemy.kind, world.elapsed)
                rect = image.get_rect(midbottom=(x, y+radius))
            surface.blit(image, rect)
            if enemy.hp < enemy.max_hp and enemy.boss_index is None:
                pygame.draw.rect(surface, "#ef8b9c", (x-radius, y-radius-12, radius*2*max(0, enemy.hp)/enemy.max_hp, 2))

        for area in world.combat.areas:
            if SPELLS[area.spell_id]['mechanic'] == 'beam':
                scale = SPELLS[area.spell_id].get('visual_scale', 1.4)
                radius = max(12, int(area.radius))
                image = self.assets.magic(area.spell_id, (int(radius*2*scale), int(radius*3*scale)), area.age)
                surface.blit(image, image.get_rect(midbottom=area.pos+offset+Vector2(0, radius/2)))

        for shot in world.projectiles:
            pos = shot.pos + offset
            angle = math.degrees(math.atan2(shot.velocity.y, shot.velocity.x))
            size = SPELLS[shot.spell_id].get('visual_size', (156, 30) if shot.spell_id == 'hyorinmaru' else (70, 46))
            progress = min(1, shot.traveled/max(1, shot.max_range))
            frame = projectile_frame(shot.spell_id, shot.age, progress)
            if shot.spell_id == 'yami_matoi' and frame == 0:
                size = (int(size[0]*.45), int(size[1]*.45))
            image = self.assets.directed_magic(shot.spell_id, size, angle, shot.age, frame)
            if shot.spell_id == 'yami_matoi' and progress > .72:
                image.set_alpha(int(255*(1-progress)/.28))
            surface.blit(image, image.get_rect(center=pos))

        player = world.player
        self.draw_player(surface, center, world.elapsed, player)
        for hazard in world.enemy_attacks.hazards:
            if hazard.stats['mechanic'] == 'mirror' and hazard.end_pos is not None:
                for i, point in enumerate((hazard.pos, hazard.end_pos)):
                    image = self.assets.water_mirror((74,104),hazard.age,flip=bool(i))
                    if hazard.age < hazard.stats['warning']:
                        image = image.copy()
                        image.set_alpha(110)
                    surface.blit(image,image.get_rect(center=point+offset))

        pygame.draw.rect(surface, "#080d16", (center.x-24, center.y+28, 48, 7))
        pygame.draw.rect(surface, "#92d5cc", (center.x-23, center.y+29, 46*player.hp/player.max_hp, 5))
        for effect in world.effects:
            pygame.draw.circle(surface, effect.color, effect.pos+offset, max(1, int(30*(1-effect.life))), 2)

    def draw_ground(self, surface, camera, offset, map_id="tundra"):
        width, height = surface.get_size()
        tile = self.assets.ground(map_id)
        step = tile.get_width()
        start_x = math.floor((camera.x-width/2)/step)*step
        start_y = math.floor((camera.y-height/2)/step)*step
        for x in range(start_x, start_x+width+step*2, step):
            for y in range(start_y, start_y+height+step*2, step):
                surface.blit(tile, (round(x+offset.x), round(y+offset.y)))

    def draw_player(self, surface, center, elapsed, player):
        x, y = center
        pygame.draw.ellipse(surface, "#080e18", (x-22, y+10, 44, 16))
        if player.invulnerability > 0 and int(elapsed*15) % 2:
            return
        image = self.assets.character(player.character_id, player.moving, elapsed, player.facing)
        form = transformation(player)
        feet = Vector2(x, y+22)
        self.transformations.draw(surface, form, player.character_id, feet, elapsed, "back", image)
        surface.blit(image, image.get_rect(midbottom=(x, y+22)))
        self.transformations.draw(surface, form, player.character_id, feet, elapsed, "front", image)

    def draw_hostile_attacks(self, surface, world, offset):
        for hazard in world.enemy_attacks.hazards:
            pos = hazard.pos+offset
            stats = hazard.stats
            kind = stats["mechanic"]
            radius = max(12, int(stats["radius"]))
            warning = hazard.age < stats["warning"]
            if kind == 'mirror':
                continue
            color = "#ffce78" if warning else "#ef6b9c"
            if hazard.key in ('mor_meteor', 'hab_embers'):
                pygame.draw.ellipse(surface, '#ffb34d', (pos.x-radius, pos.y-radius*.55, radius*2, radius*1.1), 2)
                if not warning:
                    active_age = hazard.age-stats['warning']
                    fall = max(.01, stats.get('fall_duration', .55))
                    progress = min(1, active_age/fall)
                    # Ground projection goes from Morax toward the target, while height falls to zero.
                    air_pos = pos-hazard.direction*stats.get('fall_travel',160)*(1-progress)
                    air_pos.y -= stats.get('fall_height',240)*(1-progress)
                    size = stats.get('visual_size', 110)
                    angle = math.degrees(math.atan2(hazard.direction.y, hazard.direction.x))
                    image = self.assets.directed_boss(hazard.key, (size,size), angle)
                    if progress == 1:
                        image.set_alpha(int(255*max(0,1-(active_age-fall)/max(.01,stats['duration']-fall))))
                        pygame.draw.ellipse(surface, '#ffcf75', (pos.x-radius, pos.y-radius*.55, radius*2, radius*1.1), 3)
                    surface.blit(image,image.get_rect(center=air_pos))
                continue
            if kind == "beam":
                end = pos+hazard.direction*stats["range"]
                if warning:
                    pygame.draw.line(surface, color, pos, end, 2)
                if not warning:
                    image = self.assets.directed_boss(hazard.key, (int(stats['range']), radius*2),
                                                     math.degrees(math.atan2(hazard.direction.y, hazard.direction.x)), preserve_aspect=True)
                    surface.blit(image, image.get_rect(center=(pos+end)/2))
                continue
            if kind in ("shot", "homing", "radial", "tornado"):
                if warning:
                    pygame.draw.circle(surface, color, pos, 32, 2)
                continue
            if warning:
                pygame.draw.circle(surface, color, pos, radius, 2)
                pygame.draw.circle(surface, color, pos, max(1, int(radius*hazard.age/max(.01, stats["warning"]))), 1)
            else:
                if kind == "ring":
                    radius = max(12, int(radius*(hazard.age-stats["warning"])/stats["duration"]))
                image = self.assets.boss_attack(hazard.key, (radius*2, radius*2))
                surface.blit(image, image.get_rect(center=pos))
        for shot in world.enemy_attacks.shots:
            size = max(40, int(shot.radius*2))
            size = BOSS_ATTACKS.get(shot.key, {}).get('visual_size', size)
            angle = math.degrees(math.atan2(shot.velocity.y, shot.velocity.x))
            if shot.key == 'foc_mirror':
                image = pygame.transform.rotate(self.assets.water_mirror((60,26),shot.age,projectile=True),-angle)
                surface.blit(image,image.get_rect(center=shot.pos+offset))
                continue
            image = (self.assets.boss_attack(shot.key, (size, size)) if shot.key == 'bar_tornado'
                     else self.assets.directed_boss(shot.key, (size, size), angle))
            surface.blit(image, image.get_rect(center=shot.pos+offset))
