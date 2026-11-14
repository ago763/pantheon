"""Simulação da partida. Não cria janelas nem lê teclado ou mouse."""

import math
import random

from pygame import Vector2

from . import config
from .entities import Effect, Enemy, LightningZone, Pickup, Player, Projectile, Footprint
from .progression import apply_upgrade, draw_upgrades
from .progression import modifiers, transformation
from .catalog import BOSS_ATTACKS, BOSS_SETTINGS, CHARACTERS, ELEMENTS, ENEMIES
from .combat import Combat
from .enemy_attacks import EnemyAttacks


class World:
    def __init__(self, seed: int | None = None, character_id="ice_witch", map_id="tundra", duration=900):
        self.duration = duration
        self.defeated_bosses = set()
        self.random = random.Random(seed)
        self.player = Player()
        character = CHARACTERS[character_id]
        self.player.character_id = character_id
        self.player.hp = self.player.max_hp = character["hp"]
        self.player.speed = character["speed"]
        self.player.weapons = {character["starting_spell"]: 1}
        self.map_id = map_id
        self.combat = Combat(self)
        self.enemy_attacks = EnemyAttacks(self)
        self.snared = 0
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.pickups: list[Pickup] = []
        self.effects: list[Effect] = []
        self.elapsed = 0.0
        self.kills = 0
        self.spawn_timer = 0.0
        self.attack_timer = 0.0
        self.next_enemy_id = 0
        self.state = "play"
        self.choices = []
        self.lightning_zones: list[LightningZone] = []
        self.next_boss = 0
        self.footprints = []
        self.trail_anchor = None
        self.light_trail = []

    def toggle_pause(self):
        if self.state == "play":
            self.state = "pause"
        elif self.state == "pause":
            self.state = "play"

    def choose_upgrade(self, index: int):
        if self.state != "choice" or not 0 <= index < len(self.choices):
            return
        apply_upgrade(self.player, self.choices[index])
        self.choices = []
        self.state = "play"

    def update(self, dt: float, movement: Vector2, viewport: tuple[int, int]):
        if self.state != "play":
            return
        self.elapsed += dt
        self.snared = max(0, self.snared-dt)
        player = self.player
        player.invulnerability = max(0, player.invulnerability - dt)
        mod = modifiers(player)
        player.hp = min(player.max_hp, player.hp+mod["regen"]*dt)
        player.moving = movement.length_squared() > 0
        if player.moving:
            player.aim = movement.normalize()
            player.pos += player.aim * player.speed * (1+mod["speed"]) * (.35 if self.snared else 1) * dt
            if movement.x:
                player.facing = 1 if movement.x > 0 else -1

        self.update_footprints(dt)
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy(viewport)
            self.spawn_timer = max(0.2, 1 - self.elapsed / 210)
        self.move_enemies(dt)
        self.update_bosses(dt)
        self.enemy_attacks.update(dt)
        self.combat.update(dt)
        self.remove_defeated_enemies()
        self.collect_pickups(dt)
        for effect in self.effects:
            effect.life -= dt
        self.effects = [effect for effect in self.effects if effect.life > 0]

        if player.hp <= 0:
            player.hp = 0
            self.state = "defeat"
        elif len(self.defeated_bosses) == 6:
            self.state = "victory"
        elif player.xp >= player.xp_required:
            player.xp -= player.xp_required
            player.level += 1
            player.xp_required = math.ceil(player.xp_required * 1.28)
            self.choices = draw_upgrades(player, self.random)
            self.state = "choice"

    def update_footprints(self, dt):
        light_settings = ELEMENTS['light']['trail']
        for point in self.light_trail:
            point.age += dt
        self.light_trail = [point for point in self.light_trail if point.age < light_settings['duration']]
        if transformation(self.player) == 'light' and self.player.moving:
            feet = self.player.pos+Vector2(0,22)
            if not self.light_trail or feet.distance_to(self.light_trail[-1].pos) >= 2:
                self.light_trail.append(Footprint(feet.copy(),'light'))
            length = 0
            for i in range(len(self.light_trail)-1,0,-1):
                length += self.light_trail[i].pos.distance_to(self.light_trail[i-1].pos)
                if length > light_settings.get('max_length',220):
                    self.light_trail = self.light_trail[i:]
                    break
        self.footprints = [p for p in self.footprints if p.age+dt < ELEMENTS[p.element]['trail']['duration']]
        for footprint in self.footprints:
            footprint.age += dt
        element = transformation(self.player)
        if element not in ('ice','fire','lightning') or not self.player.moving:
            self.trail_anchor = None
        else:
            settings = ELEMENTS[element]['trail']
            feet = self.player.pos+Vector2(0,22)
            if self.trail_anchor is None or feet.distance_to(self.trail_anchor) >= settings['spacing']:
                self.footprints.append(Footprint(feet.copy(),element,facing=self.player.facing))
                self.footprints = self.footprints[-min(5,max(1,settings['max_count'])):]
                self.trail_anchor = feet.copy()
        for footprint in self.footprints:
            if footprint.element not in ('ice','fire'):
                continue
            settings = ELEMENTS[footprint.element]['trail']
            for enemy in self.enemies:
                delta = enemy.pos+Vector2(0,enemy.radius)-footprint.pos
                if enemy.hp > 0 and (delta.x/(settings['width']/2+enemy.radius))**2+(delta.y/(settings['height']/2+enemy.radius))**2 <= 1:
                    if footprint.element == 'ice':
                        enemy.slow = max(enemy.slow,settings['effect_duration'])
                    else:
                        enemy.burn = max(enemy.burn,settings['effect_duration'])

    def spawn_enemy(self, viewport):
        angle = self.random.uniform(0, math.tau)
        radius = math.hypot(*viewport) / 2 + 50
        pos = self.player.pos + Vector2(math.cos(angle), math.sin(angle)) * radius
        kind = self.random.choices(["moth", "tank", "eye", "bomb"], [55, 20, 18, 7])[0]
        stats = ENEMIES[kind]
        hp = stats["hp"]+self.elapsed*stats["hp_per_second"]
        self.enemies.append(Enemy(
            id=self.next_enemy_id, pos=pos, hp=hp, max_hp=hp,
            speed=stats["speed"]+self.elapsed*stats["speed_per_second"],
            radius=stats["radius"], tank=kind == "tank", kind=kind,
        ))
        self.next_enemy_id += 1

    def spawn_boss(self, index, pos=None):
        hp = BOSS_SETTINGS["base_hp"]+index*BOSS_SETTINGS["hp_per_boss"]
        self.enemies.append(Enemy(
            id=self.next_enemy_id,
            pos=Vector2(pos) if pos is not None else self.player.pos + Vector2(0, -300),
            hp=hp, max_hp=hp, speed=BOSS_SETTINGS["speed"], radius=BOSS_SETTINGS["radius"], tank=True, boss_index=index,
        ))
        self.next_enemy_id += 1

    def update_bosses(self, dt):
        if self.next_boss < 6 and self.elapsed >= self.duration*(self.next_boss+1)/6:
            self.spawn_boss(self.next_boss)
            self.next_boss += 1
        for zone in self.lightning_zones:
            zone.age += dt
            zone.damage_timer = max(0, zone.damage_timer-dt)
            if zone.warning <= zone.age < zone.warning + zone.active:
                if zone.contains(self.player.pos) and zone.damage_timer == 0 and self.player.invulnerability == 0:
                    self.player.hp -= BOSS_ATTACKS["beel_grid"]["damage"]*max(.2, 1-modifiers(self.player)["armor"])
                    self.player.invulnerability = config.INVULNERABILITY_DURATION
                    zone.damage_timer = 0.8
                    self.effects.append(Effect(self.player.pos.copy(), "#c66bff"))
        self.lightning_zones = [zone for zone in self.lightning_zones
                                if zone.age < zone.warning + zone.active + 0.4]

    def move_enemies(self, dt):
        for enemy in self.enemies:
            if enemy.hp <= 0:
                continue
            enemy.frozen = max(0, enemy.frozen-dt)
            if enemy.burn > 0:
                enemy.burn -= dt
                enemy.hp -= 5*dt
            if transformation(self.player) == "ice" and enemy.pos.distance_to(self.player.pos) < ELEMENTS["ice"]["bonus"]["slow_aura"]:
                enemy.slow = max(enemy.slow, .5)
            enemy.slow = max(0, enemy.slow - dt)
            direction = self.player.pos - enemy.pos
            if direction.length_squared():
                speed = enemy.speed * (0 if enemy.frozen else 0.45 if enemy.slow else 1)
                enemy.pos += direction.normalize() * min(speed * dt, direction.length())
            if (enemy.pos.distance_to(self.player.pos) < enemy.radius + config.PLAYER_RADIUS
                    and self.player.invulnerability == 0):
                dodge = ELEMENTS["dark"]["bonus"]["dodge"] if transformation(self.player) == "dark" else 0
                if self.random.random() < dodge:
                    self.player.invulnerability = .3
                    continue
                damage = BOSS_SETTINGS["contact_damage"] if enemy.boss_index is not None else ENEMIES[enemy.kind]["contact_damage"]
                self.player.hp -= damage*max(.2, 1-modifiers(self.player)["armor"])
                self.player.invulnerability = config.INVULNERABILITY_DURATION
                self.effects.append(Effect(self.player.pos.copy(), "#ff8b9b"))

    def remove_defeated_enemies(self):
        survivors = []
        for enemy in self.enemies:
            if enemy.hp > 0:
                survivors.append(enemy)
                continue
            self.kills += 1
            if enemy.boss_index is not None:
                self.defeated_bosses.add(enemy.boss_index)
            self.combat.on_kill(enemy)
            self.pickups.append(Pickup(enemy.pos.copy(), 25 if enemy.boss_index is not None else 5 if enemy.tank else 1))
            if self.random.random() < 0.035:
                self.pickups.append(Pickup(enemy.pos + Vector2(10, 0), 0))
        self.enemies = survivors

    def collect_pickups(self, dt):
        remaining = []
        for pickup in self.pickups:
            distance = pickup.pos.distance_to(self.player.pos)
            if distance < config.PICKUP_RADIUS*(1+modifiers(self.player)["magnet"]):
                pickup.pos += (self.player.pos - pickup.pos) * min(1, dt * 7)
            if pickup.pos.distance_to(self.player.pos) < 18:
                if pickup.value:
                    self.player.xp += pickup.value*(1+modifiers(self.player)["xp"])
                else:
                    self.player.hp = min(self.player.max_hp, self.player.hp + 20)
            else:
                remaining.append(pickup)
        self.pickups = remaining
