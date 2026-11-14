"""Três ataques por chefe, projéteis hostis, avisos e ataques comuns."""

from dataclasses import dataclass, field
import math

from pygame import Vector2

from .catalog import BOSS_ATTACKS, ENEMIES
from .entities import Effect, LightningZone
from .progression import modifiers


@dataclass
class Hazard:
    key: str
    pos: Vector2
    direction: Vector2
    stats: dict
    age: float = 0
    launched: bool = False
    tick: float = 0
    end_pos: Vector2 | None = None
    shots_fired: int = 0
    closes_at: float = math.inf


@dataclass
class EnemyShot:
    key: str
    pos: Vector2
    velocity: Vector2
    damage: float
    radius: float
    life: float
    homing: bool = False
    duplicated: bool = False
    age: float = 0


class EnemyAttacks:
    def __init__(self, world):
        self.world = world
        self.timers = {}
        self.hazards = []
        self.shots = []

    def hurt(self, damage, slow=False):
        p = self.world.player
        if p.invulnerability > 0:
            return
        p.hp -= damage*max(.2, 1-modifiers(p)["armor"])
        p.invulnerability = .8
        if slow:
            self.world.snared = max(self.world.snared, 1.2)
        self.world.effects.append(Effect(p.pos.copy(), "#ff8b9b"))

    def schedule(self, enemy, key):
        stats = dict(BOSS_ATTACKS[key])
        player = self.world.player
        direction = player.pos-enemy.pos
        direction = direction.normalize() if direction.length_squared() else Vector2(0, 1)
        kind = stats["mechanic"]
        if kind == 'mirror':
            self.hazards.append(Hazard(key, enemy.pos.copy(), direction, stats, end_pos=player.pos.copy()))
            return
        if kind == "grid":
            self.world.lightning_zones.append(LightningZone(player.pos.copy(), warning=stats["warning"], active=stats["duration"], scale=stats.get('area_scale', 1)))
            return
        if kind == "rain":
            for i in range(stats["count"]):
                offset = Vector2(1, 0).rotate(i*360/stats["count"])*85 if i else Vector2()
                self.hazards.append(Hazard(key, player.pos+offset, direction, stats))
        elif kind in ("lava", "wall"):
            side = Vector2(-direction.y, direction.x)
            for i in range(stats["count"]):
                pos = enemy.pos+direction*(80+i*55) if kind == "lava" else player.pos+direction*55+side*(i-2)*55
                self.hazards.append(Hazard(key, pos, direction, stats))
        else:
            pos = player.pos.copy() if kind in ("meteor", "roots") else enemy.pos.copy()
            self.hazards.append(Hazard(key, pos, direction, stats))

    def update(self, dt):
        live_ids = {enemy.id for enemy in self.world.enemies if enemy.hp > 0}
        self.timers = {key: value for key, value in self.timers.items() if key[0] in live_ids}
        for enemy in self.world.enemies:
            if enemy.hp <= 0:
                continue
            if enemy.boss_index is not None:
                keys = [key for key, stats in BOSS_ATTACKS.items() if stats["boss"] == enemy.boss_index]
                for i, key in enumerate(keys):
                    timer_key = (enemy.id, key)
                    self.timers[timer_key] = self.timers.get(timer_key, 2+i*1.6)-dt
                    if self.timers[timer_key] <= 0:
                        if enemy.pos.distance_to(self.world.player.pos) <= BOSS_ATTACKS[key]["range"]:
                            self.schedule(enemy, key)
                        self.timers[timer_key] = BOSS_ATTACKS[key]["cooldown"]
            else:
                self.update_common(enemy, dt)
        self.update_hazards(dt)
        self.update_shots(dt)

    def update_common(self, enemy, dt):
        stats = ENEMIES[enemy.kind]
        delta = self.world.player.pos-enemy.pos
        if enemy.kind == "bomb":
            if delta.length() < 100 and not enemy.primed:
                enemy.primed = True
                enemy.speed = 0
                self.hazards.append(Hazard("bomb", enemy.pos.copy(), Vector2(0, 1),
                    {"mechanic": "meteor", "warning": stats["warning"], "duration": .4,
                     "radius": stats["attack_radius"], "damage": stats["attack_damage"]}))
                enemy.attack_timer = stats["warning"]+.4
            if enemy.primed:
                enemy.attack_timer -= dt
                if enemy.attack_timer <= 0:
                    enemy.hp = 0
        elif enemy.kind in ("eye", "moth"):
            enemy.attack_timer -= dt
            if enemy.attack_timer <= 0 and 0 < delta.length() < 650:
                self.shots.append(EnemyShot(enemy.kind, enemy.pos.copy(), delta.normalize()*stats["attack_speed"],
                                            stats["attack_damage"], 12, 5))
                enemy.attack_timer = stats["attack_cooldown"]

    def update_hazards(self, dt):
        player = self.world.player
        for hazard in self.hazards:
            hazard.age += dt
            hazard.tick -= dt
            stats = hazard.stats
            kind = stats["mechanic"]
            if hazard.age < stats["warning"]:
                continue
            if kind == 'mirror':
                hazard.launched = True
                if (hazard.tick <= 0 and hazard.end_pos is not None
                        and hazard.shots_fired < stats['count']
                        and hazard.age < stats['warning']+stats['duration']):
                    delta = hazard.end_pos-hazard.pos
                    if delta.length_squared():
                        speed = max(1, stats['speed'])
                        self.shots.append(EnemyShot('foc_mirror', hazard.pos.copy(), delta.normalize()*speed,
                                                   stats['damage'], stats.get('projectile_radius',12), delta.length()/speed))
                        hazard.shots_fired += 1
                        if hazard.shots_fired == stats['count']:
                            hazard.closes_at = hazard.age+delta.length()/speed
                    hazard.tick = stats.get('shot_interval',.55)
                continue
            if not hazard.launched:
                hazard.launched = True
                if kind in ("shot", "radial", "homing", "tornado"):
                    for i in range(stats["count"]):
                        angle = i*360/stats["count"] if kind == "radial" else (i-(stats["count"]-1)/2)*15
                        velocity = hazard.direction.rotate(angle)*stats["speed"]
                        self.shots.append(EnemyShot(hazard.key, hazard.pos.copy(), velocity, stats["damage"],
                                                    stats["radius"], stats["duration"], kind == "homing"))
            if kind in ("shot", "radial", "homing", "tornado", "mirror"):
                continue
            delta = player.pos-hazard.pos
            distance = delta.length()
            active_age = hazard.age-stats["warning"]
            if hazard.key in ('mor_meteor', 'hab_embers') and active_age < stats.get('fall_duration', .55):
                continue
            inside = distance <= stats["radius"]+10
            if kind == "beam":
                along = delta.dot(hazard.direction)
                across = abs(delta.cross(hazard.direction))
                inside = 0 <= along <= stats["range"] and across <= stats["radius"]+10
            elif kind == "ring":
                radius = stats["radius"]*active_age/stats["duration"]
                inside = abs(distance-radius) <= 18
            elif kind == "wall" and inside and distance:
                player.pos = hazard.pos+delta.normalize()*(stats["radius"]+14)
            if inside and hazard.tick <= 0:
                self.hurt(stats["damage"], kind == "roots")
                hazard.tick = .8
        self.hazards = [h for h in self.hazards
                        if h.age < min(h.closes_at, h.stats["warning"]+h.stats["duration"])]

    def update_shots(self, dt):
        extra = []
        for shot in self.shots:
            shot.age += dt
            if shot.homing:
                delta = self.world.player.pos-shot.pos
                if delta.length_squared():
                    shot.velocity = shot.velocity.lerp(delta.normalize()*shot.velocity.length(), min(1, dt*2))
            previous = shot.pos.copy()
            shot.pos += shot.velocity*min(dt,max(0,shot.life))
            shot.life -= dt
            segment = shot.pos-previous
            t = ((self.world.player.pos-previous).dot(segment)/segment.length_squared()) if segment.length_squared() else 0
            closest = previous+segment*max(0, min(1, t))
            if closest.distance_to(self.world.player.pos) <= shot.radius+10:
                self.hurt(shot.damage)
                shot.life = 0
            if shot.key == "bar_tornado":
                for friendly in self.world.projectiles:
                    if friendly.pos.distance_to(shot.pos) < shot.radius+20:
                        friendly.velocity.rotate_ip(100*dt)
        self.shots = [shot for shot in self.shots if shot.life > 0]+extra
