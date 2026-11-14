"""Execução das quinze magias com valores vindos do catálogo editável."""

import math

from pygame import Vector2

from .catalog import ELEMENTS, SPELLS
from .entities import Effect, Projectile, SpellArea
from .progression import modifiers, spell_stats, transformation


class Combat:
    def __init__(self, world):
        self.world = world
        self.cooldowns = {}
        self.areas = []

    def hit(self, enemy, key, damage):
        player = self.world.player
        data = SPELLS[key]
        critical = self.world.random.random() < modifiers(player)["critical"]
        enemy.hp -= damage*(2 if critical else 1)
        enemy.slow = max(enemy.slow, data["slow"])
        enemy.burn = max(enemy.burn, data["burn"])
        if key in ("ice_age", "shadow_spikes", "magnetic_field"):
            enemy.frozen = max(enemy.frozen, .45)
        self.world.effects.append(Effect(enemy.pos.copy(), ELEMENTS[data["element"]]["color"]))

    def update(self, dt):
        player = self.world.player
        for key in player.weapons:
            self.cooldowns[key] = self.cooldowns.get(key, 0)-dt
            if self.cooldowns[key] <= 0:
                stats = spell_stats(player, key)
                targets = [e for e in self.world.enemies if e.hp > 0 and e.pos.distance_to(player.pos) <= stats["range"]]
                if targets or stats["mechanic"] == "orbit":
                    self.cast(key, stats, targets)
                    self.cooldowns[key] = stats["cooldown"]
        self.update_projectiles(dt)
        self.update_areas(dt)

    def cast(self, key, stats, targets):
        player = self.world.player
        if stats.get('single_group') and any(s.spell_id == key for s in self.world.projectiles):
            return
        target = min(targets, key=lambda enemy: enemy.pos.distance_squared_to(player.pos), default=player)
        mechanic = stats["mechanic"]
        if mechanic == 'whip' and any(area.spell_id == key for area in self.areas):
            return
        if mechanic == "orbit" and any(area.spell_id == key for area in self.areas):
            return
        if mechanic == "beam":
            ranked = sorted(targets, key=lambda enemy: enemy.hp, reverse=True)
            if not ranked:
                return
            for i in range(stats['projectiles']):
                target = ranked[i % len(ranked)]
                # With fewer enemies than beams, remaining beams cover nearby ground.
                offset = Vector2(0, 0) if i < len(ranked) else Vector2((i-len(ranked)+1)*stats['radius']*2, 0)
                self.areas.append(SpellArea(target.pos+offset, key, stats['radius'], stats['duration'],
                                           stats['damage'], target_id=target.id if i < len(ranked) else None))
            return
        direction = target.pos-player.pos
        direction = direction.normalize() if direction.length_squared() else player.aim.copy()
        if mechanic in ("projectile", "homing", "slash", "fireball"):
            count = 1 if stats.get('single_group') else stats['projectiles']
            for i in range(count):
                heading = direction.rotate((i-(count-1)/2)*12)
                speed = max(1, stats["projectile_speed"])
                self.world.projectiles.append(Projectile(
                    pos=player.pos.copy(), velocity=heading*speed,
                    life=stats["range"]/speed, spell_id=key, damage=stats["damage"],
                    radius=12 if mechanic == "fireball" else stats["radius"],
                    homing=mechanic == "homing" and not stats.get('single_group'), max_range=stats["range"],
                ))
        else:
            centered = mechanic in ("pulse", "orbit", "whip", "cone")
            pos = player.pos.copy() if centered else target.pos.copy()
            duration = math.inf if mechanic == "orbit" else stats["duration"]
            self.areas.append(SpellArea(pos, key, stats["radius"], duration, stats["damage"],
                                        math.atan2(direction.y, direction.x)))

    def update_projectiles(self, dt):
        for shot in self.world.projectiles:
            shot.age += dt
            if shot.homing:
                targets = [enemy for enemy in self.world.enemies if enemy.hp > 0 and enemy.id not in shot.hit_ids]
                if targets:
                    target = min(targets, key=lambda enemy: enemy.pos.distance_squared_to(shot.pos))
                    direction = target.pos-shot.pos
                    if direction.length_squared():
                        shot.velocity = direction.normalize()*shot.velocity.length()
            previous = shot.pos.copy()
            shot.pos += shot.velocity*dt
            shot.traveled += shot.velocity.length()*dt
            shot.life -= dt
            segment = shot.pos-previous
            length_squared = segment.length_squared()
            for enemy in self.world.enemies:
                if enemy.hp <= 0 or enemy.id in shot.hit_ids:
                    continue
                t = (enemy.pos-previous).dot(segment)/length_squared if length_squared else 0
                closest = previous+segment*max(0, min(1, t))
                if closest.distance_to(enemy.pos) < enemy.radius+shot.radius:
                    self.hit(enemy, shot.spell_id, shot.damage)
                    shot.hit_ids.add(enemy.id)
                    stats = spell_stats(self.world.player, shot.spell_id)
                    if stats["mechanic"] == "fireball":
                        self.areas.append(SpellArea(enemy.pos.copy(), shot.spell_id, stats["radius"], .3, shot.damage*.5,
                                                   math.atan2(shot.velocity.y, shot.velocity.x)))
                        shot.life = 0
                        break
                    if shot.homing and not (shot.spell_id == "static_needles" and self.world.player.weapons[shot.spell_id] == 6 and len(shot.hit_ids) < 5):
                        shot.life = 0
                        break
        self.world.projectiles = [shot for shot in self.world.projectiles if shot.life > 0 and shot.traveled < shot.max_range]

    def orbit_points(self, area):
        stats = spell_stats(self.world.player, area.spell_id)
        if area.spell_id == "storm_orbs":
            count = stats["base_orbs"]+(min(5, self.world.player.weapons[area.spell_id])-1)*stats["orbs_per_level"]
            origin = self.world.player.pos+Vector2(0, stats["orbit_center_y"])
            angle = self.world.elapsed*stats["orbit_speed"]
            return [origin+Vector2(math.cos(math.radians(angle+i*360/count))*stats["range"],
                                  math.sin(math.radians(angle+i*360/count))*stats["range"]*stats["orbit_vertical_scale"])
                    for i in range(count)]
        return [self.world.player.pos+Vector2(1, 0).rotate(self.world.elapsed*120+i*120)*stats["range"] for i in range(3)]

    def update_areas(self, dt):
        player = self.world.player
        for area in self.areas:
            area.age += dt
            area.tick -= dt
            stats = spell_stats(player, area.spell_id)
            mechanic = stats["mechanic"]
            if area.age >= area.duration:
                continue
            if mechanic == "orbit":
                area.radius = stats["radius"]
                area.damage = stats["damage"]
            if mechanic in ("pulse", "orbit", "whip", "cone"):
                area.pos = player.pos.copy()
            if mechanic == "beam" and player.weapons.get(area.spell_id) == 6 and self.world.enemies:
                target = next((e for e in self.world.enemies if e.id == area.target_id and e.hp > 0), None)
                if target:
                    area.pos = target.pos.copy()
            for enemy in self.world.enemies:
                if enemy.hp <= 0:
                    continue
                delta = enemy.pos-area.pos
                distance = delta.length()
                inside = distance <= area.radius+enemy.radius
                if mechanic == 'ice_rain':
                    impact = stats['warning']+stats['fall_duration']
                    inside = (not area.impacted and area.age >= impact
                              and (delta.x/max(1, area.radius+enemy.radius))**2
                              + (delta.y/max(1, area.radius*.55+enemy.radius))**2 <= 1)
                if mechanic == "orbit":
                    points = self.orbit_points(area)
                    inside = any(enemy.pos.distance_to(point) <= area.radius+enemy.radius for point in points)
                    if area.spell_id == "storm_orbs" and player.weapons[area.spell_id] == 6:
                        for i, point in enumerate(points):
                            segment = points[(i+1) % len(points)]-point
                            t = (enemy.pos-point).dot(segment)/max(.001, segment.length_squared())
                            if enemy.pos.distance_to(point+segment*max(0, min(1, t))) < 8+enemy.radius:
                                inside = True
                elif mechanic == "cone":
                    heading = Vector2(math.cos(area.angle), math.sin(area.angle))
                    inside = distance <= stats["range"] and (distance == 0 or heading.dot(delta/distance) > .65)
                elif mechanic == "whip":
                    inside = inside and (distance == 0 or math.cos(math.atan2(delta.y, delta.x)-area.angle) > -.3)
                    stage = min(3,int(area.age/(area.duration/4)))
                    inside = inside and (stage,enemy.id) not in area.combo_hits
                if inside:
                    if mechanic == "vortex" and distance:
                        enemy.pos -= delta.normalize()*min(distance, 95*dt)
                    if area.tick <= 0 or mechanic in ('ice_rain','whip'):
                        self.hit(enemy, area.spell_id, area.damage)
                        if mechanic == 'whip':
                            area.combo_hits.add((stage,enemy.id))
            if mechanic == 'ice_rain' and area.age >= stats['warning']+stats['fall_duration']:
                area.impacted = True
            if area.tick <= 0:
                area.tick = max(.05, stats["tick_interval"])
        self.areas = [area for area in self.areas if area.age < area.duration]

    def on_kill(self, enemy):
        form = transformation(self.world.player)
        if form == "dark":
            reduction = ELEMENTS[form]["bonus"]["cooldown_on_kill"]
            for key in self.cooldowns:
                self.cooldowns[key] -= reduction
        if form == "fire":
            radius = ELEMENTS[form]["bonus"]["death_explosion"]
            for other in self.world.enemies:
                if other.id != enemy.id and other.hp > 0 and other.pos.distance_to(enemy.pos) < radius:
                    other.hp -= 12
            self.world.effects.append(Effect(enemy.pos.copy(), ELEMENTS[form]["color"]))
