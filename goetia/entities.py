"""Dados dos personagens, inimigos, tiros, coletáveis e efeitos."""

from dataclasses import dataclass, field

from pygame import Vector2

from . import config


@dataclass
class Player:
    pos: Vector2 = field(default_factory=Vector2)
    hp: float = config.PLAYER_HEALTH
    max_hp: float = config.PLAYER_HEALTH
    speed: float = config.PLAYER_SPEED
    damage: float = config.PLAYER_DAMAGE
    attack_interval: float = config.PLAYER_ATTACK_INTERVAL
    xp: int = 0
    level: int = 1
    xp_required: int = config.INITIAL_XP_REQUIRED
    weapon_level: int = 1
    invulnerability: float = 0
    facing: int = 1
    moving: bool = False
    character_id: str = "ice_witch"
    weapons: dict[str, int] = field(default_factory=lambda: {"hyorinmaru": 1})
    passives: dict[str, int] = field(default_factory=dict)
    aim: Vector2 = field(default_factory=lambda: Vector2(1, 0))


@dataclass
class Enemy:
    id: int
    pos: Vector2
    hp: float
    max_hp: float
    speed: float
    radius: int
    tank: bool = False
    slow: float = 0
    boss_index: int | None = None
    attack_timer: float = 3.0
    frozen: float = 0
    burn: float = 0
    kind: str = "moth"
    primed: bool = False


@dataclass
class Projectile:
    pos: Vector2
    velocity: Vector2
    life: float = config.PROJECTILE_LIFETIME
    hit_ids: set[int] = field(default_factory=set)
    spell_id: str = "hyorinmaru"
    damage: float = 23
    radius: float = 18
    homing: bool = False
    traveled: float = 0
    max_range: float = 600
    age: float = 0


@dataclass
class SpellArea:
    pos: Vector2
    spell_id: str
    radius: float
    duration: float
    damage: float
    angle: float = 0
    age: float = 0
    tick: float = 0
    impacted: bool = False
    target_id: int | None = None
    combo_hits: set[tuple[int, int]] = field(default_factory=set)


@dataclass
class Footprint:
    pos: Vector2
    element: str
    age: float = 0
    facing: int = 1


@dataclass
class Pickup:
    pos: Vector2
    value: int = 1  # Zero significa poção de cura.


@dataclass
class Effect:
    pos: Vector2
    color: str = config.ICE
    life: float = 0.25


@dataclass
class LightningZone:
    pos: Vector2
    age: float = 0
    warning: float = 1.4
    active: float = 1.1
    damage_timer: float = 0
    scale: float = 1

    def contains(self, pos):
        delta = (pos - self.pos)/self.scale
        # Trapézio que acompanha o piso desenhado, mais estreito no topo.
        half_width = 78 + (delta.y + 42) / 84 * 27
        return -42 <= delta.y <= 42 and abs(delta.x) <= half_width
