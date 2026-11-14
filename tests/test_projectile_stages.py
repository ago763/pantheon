import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import unittest
from pygame import Vector2
from goetia.animation import projectile_frame
from goetia.entities import Enemy
from goetia.world import World
from goetia.progression import spell_stats


class StagesTests(unittest.TestCase):
    def test_light_whip_four_hits_without_loop_or_overlap(self):
        w = World()
        w.player.weapons = {'light_whip':1}
        enemy = Enemy(1,Vector2(50,0),10000,10000,0,10)
        w.enemies=[enemy]
        stats=spell_stats(w.player,'light_whip')
        hits=[]
        w.combat.hit=lambda enemy,key,damage: hits.append(enemy.id)
        w.combat.cast('light_whip',stats,[enemy])
        w.combat.cast('light_whip',stats,[enemy])
        self.assertEqual(len(w.combat.areas),1)
        for _ in range(150):
            w.combat.update_areas(.01)
        self.assertEqual(hits,[1,1,1,1])
        self.assertFalse(w.combat.areas)

    def test_morax_meteor_damage_waits_for_landing(self):
        w = World()
        w.spawn_boss(2, (-200,0))
        w.enemy_attacks.schedule(w.enemies[0], 'mor_meteor')
        hazard = w.enemy_attacks.hazards[0]
        self.assertEqual(hazard.direction, Vector2(1,0))
        hp = w.player.hp
        w.enemy_attacks.update_hazards(hazard.stats['warning']+hazard.stats['fall_duration']-.01)
        self.assertEqual(w.player.hp,hp)
        w.enemy_attacks.update_hazards(.02)
        self.assertLess(w.player.hp,hp)

    def test_ember_rain_waits_for_landing(self):
        w = World()
        w.spawn_boss(4,(-200,0))
        w.enemy_attacks.schedule(w.enemies[0],'hab_embers')
        stats = w.enemy_attacks.hazards[0].stats
        hp = w.player.hp
        w.enemy_attacks.update_hazards(stats['warning']+stats['fall_duration']-.01)
        self.assertEqual(w.player.hp,hp)
        w.enemy_attacks.update_hazards(.02)
        self.assertLess(w.player.hp,hp)

    def test_morax_spears_point_toward_target(self):
        for pos in [(-200,0),(200,0),(0,-200),(0,200)]:
            w = World()
            w.spawn_boss(2,pos)
            w.enemy_attacks.schedule(w.enemies[0],'mor_spears')
            h = w.enemy_attacks.hazards[0]
            w.enemy_attacks.update_hazards(h.stats['warning']+.01)
            for shot in w.enemy_attacks.shots:
                self.assertGreater(shot.velocity.dot(-Vector2(pos)),0)

    def test_punishment_level_counts_and_independent_targets(self):
        for level, count in [(1,1),(2,1),(3,2),(4,2),(5,3),(6,3)]:
            w = World(character_id='light_elf')
            w.player.weapons = {'punishment': level}
            w.enemies = [Enemy(i,Vector2(100+i*60,0),100+i,100+i,0,10) for i in range(3)]
            w.combat.cast('punishment',spell_stats(w.player,'punishment'),w.enemies)
            self.assertEqual(len(w.combat.areas),count)
            self.assertEqual(len({a.target_id for a in w.combat.areas}),count)
            w.combat.update_areas(.1)
            self.assertEqual(len({tuple(a.pos) for a in w.combat.areas}),count)

    def test_punishment_three_beams_with_one_enemy(self):
        w = World(character_id='light_elf')
        w.player.weapons = {'punishment': 5}
        target = Enemy(1,Vector2(100,0),1000,1000,0,10)
        w.combat.cast('punishment',spell_stats(w.player,'punishment'),[target])
        self.assertEqual(len(w.combat.areas),3)
        self.assertEqual(len({tuple(a.pos) for a in w.combat.areas}),3)

    def test_ice_rain_hits_once_at_impact(self):
        w = World()
        w.player.weapons = {'demons_extract': 1}
        e = Enemy(100, Vector2(200, 0), 10000, 10000, 0, 10)
        w.enemies = [e]
        stats = spell_stats(w.player, 'demons_extract')
        w.combat.cast('demons_extract', stats, [e])
        area = w.combat.areas[0]
        w.combat.update_areas(stats['warning']+stats['fall_duration']-.01)
        self.assertEqual(e.hp, 10000)
        w.combat.update_areas(.02)
        damaged_hp = e.hp
        self.assertLess(damaged_hp, 10000)
        w.combat.update_areas(.1)
        self.assertEqual(e.hp, damaged_hp)
        self.assertTrue(area.impacted)

    def test_stages_hold_last(self):
        for key, frames in [('static_needles', [0, 1, 2]), ('judgement', [0, 2, 3])]:
            self.assertEqual([projectile_frame(key, t, 0) for t in [0, .499, .5, .999, 1, 8]],
                             [frames[0], frames[0], frames[1], frames[1], frames[2], frames[2]])

    def test_slash_finishes_without_loop(self):
        self.assertEqual([projectile_frame('yami_matoi', 1, p) for p in [0, .2, .75, .95]], [0,1,2,3])

    def test_one_group_and_straight_aim(self):
        for key in ['static_needles', 'judgement', 'yami_matoi']:
            w = World()
            w.player.weapons = {key: 5}
            target = Enemy(100, Vector2(-200, 0), 10000, 10000, 0, 10)
            w.enemies = [target]
            stats = spell_stats(w.player, key)
            w.combat.cast(key, stats, [target])
            self.assertLess(w.projectiles[0].velocity.x, 0)
            if key != 'yami_matoi':
                w.combat.cast(key, stats, [target])
                self.assertEqual(len(w.projectiles), 1)
                target.pos.y = 200
                w.combat.update_projectiles(.1)
                self.assertEqual(w.projectiles[0].velocity.y, 0)

    def test_modes_schedule_all_six_and_wait_for_deaths(self):
        for duration in [300, 600, 900]:
            w = World(duration=duration)
            for i in range(6):
                w.elapsed = duration*(i+1)/6
                w.update_bosses(0)
                self.assertEqual(w.next_boss, i+1)
            self.assertEqual({e.boss_index for e in w.enemies}, set(range(6)))
            for e in w.enemies[:5]:
                e.hp = 0
            w.remove_defeated_enemies()
            self.assertEqual(len(w.defeated_bosses), 5)
            w.enemies[0].hp = 0
            w.remove_defeated_enemies()
            self.assertEqual(len(w.defeated_bosses), 6)
