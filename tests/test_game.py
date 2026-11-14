"""Regras de inventário, combate, chefes e interface, sem janela visível."""

import os
import unittest
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Vector2

from goetia.app import Game
from goetia.catalog import BOSS_ATTACKS, CHARACTERS, ELEMENTS, MAPS, PASSIVES, SPELLS
from goetia.entities import Enemy, LightningZone, Pickup, Projectile
from goetia.enemy_attacks import EnemyShot, Hazard
from goetia.progression import apply_upgrade, available_upgrades, draw_upgrades, modifiers, spell_stats, transformation
from goetia.world import World


class RulesTests(unittest.TestCase):
    def setUp(self):
        self.world = World(seed=42)
        self.world.spawn_timer = 999
        self.world.next_boss = 6

    def tick(self, dt=.02, movement=None):
        self.world.update(dt, movement or Vector2(), (1280, 720))

    def test_thirty_entries_and_all_pairs(self):
        self.assertEqual((len(SPELLS), len(PASSIVES)), (15, 15))
        self.assertEqual(len({v['passive'] for v in SPELLS.values()}), 15)
        for element in ELEMENTS:
            self.assertEqual(sum(v['element'] == element for v in SPELLS.values()), 3)

    def test_element_affinity_increases_weight_without_duplicates(self):
        rng = random.Random(300)
        same = 0
        other = 0
        for _ in range(1500):
            cards = draw_upgrades(self.world.player, rng)
            self.assertEqual(len(cards), 4)
            self.assertEqual(len({card.key for card in cards}), 4)
            same += sum(card.element == 'ice' for card in cards)
            other += sum(card.element != 'ice' for card in cards)
        # Seis cartas de gelo entre 30; peso 2x deve superar a taxa uniforme de 20%.
        self.assertGreater(same/(same+other), .28)
        self.assertLess(same/(same+other), .37)
        self.assertGreater(other, same)

    def test_four_choices_even_when_inventory_is_maxed(self):
        player = self.world.player
        player.weapons = {key: 6 for key in list(SPELLS)[:4]}
        player.passives = {key: 5 for key in list(PASSIVES)[:4]}
        cards = draw_upgrades(player, random.Random(1))
        self.assertEqual(len(cards), 4)
        self.assertTrue(all(card.kind == 'heal' for card in cards))
        player.hp = 20
        apply_upgrade(player, cards[3])
        self.assertEqual(player.hp, 50)

    def test_inventory_limits_and_no_duplicate_slots(self):
        player = self.world.player
        player.weapons = {key: 1 for key in list(SPELLS)[:4]}
        player.passives = {key: 1 for key in list(PASSIVES)[:4]}
        for card in available_upgrades(player):
            self.assertIn(card.key, player.weapons if card.kind == "spell" else player.passives)
        card = available_upgrades(player)[0]
        apply_upgrade(player, card)
        apply_upgrade(player, card)
        self.assertEqual(player.weapons[card.key], 2)
        self.assertEqual(len(player.weapons), 4)

    def test_evolution_requires_five_stars_and_matching_passive(self):
        player = self.world.player
        player.weapons['hyorinmaru'] = 5
        self.assertNotIn('hyorinmaru', [c.key for c in available_upgrades(player)])
        player.passives['scarf'] = 1
        card = next(c for c in available_upgrades(player) if c.key == 'hyorinmaru')
        self.assertEqual(card.level, 6)
        apply_upgrade(player, card)
        self.assertEqual(player.weapons['hyorinmaru'], 6)
        self.assertNotIn('hyorinmaru', [c.key for c in available_upgrades(player)])

    def test_all_twenty_five_transformations(self):
        for character in CHARACTERS:
            player = World(character_id=character).player
            for element in ELEMENTS:
                spells = [key for key, value in SPELLS.items() if value['element'] == element]
                player.weapons = {key: 1 for key in spells[:2]}
                self.assertIsNone(transformation(player))
                player.weapons[spells[2]] = 1
                self.assertEqual(transformation(player), element)
                player.weapons[spells[0]] = 6
                self.assertEqual(transformation(player), element)

    def test_character_buff_only_applies_to_signature_spell(self):
        for key, char in CHARACTERS.items():
            player = World(character_id=key).player
            stats = spell_stats(player, char['buff_spell'])
            base = SPELLS[char['buff_spell']]
            self.assertAlmostEqual(stats['damage'], base['damage']*(1+char['damage_bonus']))
            self.assertAlmostEqual(stats['cooldown'], base['cooldown']*(1-char['cooldown_bonus']))
            other = next(s for s in SPELLS if s != char['buff_spell'])
            self.assertEqual(spell_stats(player, other)['damage'], SPELLS[other]['damage'])

    def test_passives_change_configured_stats(self):
        player = self.world.player
        for key, data in PASSIVES.items():
            player.passives = {key: 2}
            self.assertAlmostEqual(modifiers(player)[data['stat']], data['value_per_level']*2)

    def test_movement_normalization_and_pause(self):
        self.tick(.1, Vector2(1, 1))
        self.assertAlmostEqual(self.world.player.pos.length(), 18)
        self.world.toggle_pause()
        before = self.world.elapsed
        self.tick(1, Vector2(1, 0))
        self.assertEqual(self.world.elapsed, before)

    def test_xp_cards_resume_and_healing(self):
        world = self.world
        world.pickups = [Pickup(Vector2(), world.player.xp_required)]
        self.tick()
        self.assertEqual(world.state, 'choice')
        self.assertEqual(len({c.key for c in world.choices}), 4)
        elapsed = world.elapsed
        self.tick(1)
        self.assertEqual(world.elapsed, elapsed)
        world.choose_upgrade(0)
        self.assertEqual(world.state, 'play')
        world.player.hp = 90
        world.pickups = [Pickup(Vector2(), 0)]
        self.tick()
        self.assertEqual(world.player.hp, world.player.max_hp)

    def test_each_spell_can_damage_an_enemy(self):
        for key, data in SPELLS.items():
            with self.subTest(spell=key):
                world = World(seed=1)
                world.player.weapons = {key: 1}
                target = Enemy(1, Vector2(70, 0), 10000, 10000, 0, 25)
                world.enemies = [target]
                for _ in range(180):
                    world.elapsed += 1/60
                    world.combat.update(1/60)
                self.assertLess(target.hp, 10000)

    def test_projectile_hits_once_and_respects_range(self):
        world = self.world
        world.enemies = [Enemy(i, Vector2(60+i*25, 0), 100, 100, 0, 12) for i in range(2)]
        world.projectiles = [Projectile(Vector2(), Vector2(450, 0), damage=23)]
        world.combat.update_projectiles(.2)
        self.assertEqual([e.hp for e in world.enemies], [77, 77])
        world.combat.update_projectiles(.01)
        self.assertEqual([e.hp for e in world.enemies], [77, 77])
        world.combat.update_projectiles(3)
        self.assertFalse(world.projectiles)

    def test_lightning_warning_damage_expiry_and_outside(self):
        world = self.world
        world.lightning_zones = [LightningZone(Vector2())]
        self.tick(1)
        self.assertEqual(world.player.hp, 100)
        self.tick(.5)
        self.assertEqual(world.player.hp, 82)
        world.player.pos = Vector2(400, 0)
        self.tick(2)
        self.assertEqual(world.player.hp, 82)
        self.assertFalse(world.lightning_zones)

    def test_three_attacks_per_boss_and_all_schedule(self):
        for index in range(6):
            keys = [key for key, data in BOSS_ATTACKS.items() if data['boss'] == index]
            self.assertEqual(len(keys), 3)
            for key in keys:
                world = World()
                world.spawn_boss(index, (0, -200))
                world.enemy_attacks.schedule(world.enemies[0], key)
                if key == 'beel_grid':
                    self.assertTrue(world.lightning_zones)
                else:
                    self.assertTrue(world.enemy_attacks.hazards)
                    world.enemy_attacks.update_hazards(BOSS_ATTACKS[key]['warning']+.01)
                    self.assertTrue(all(h.launched for h in world.enemy_attacks.hazards))

    def test_meteor_warns_before_damage(self):
        world = self.world
        world.spawn_boss(2, (0, -200))
        world.enemy_attacks.schedule(world.enemies[0], 'mor_meteor')
        world.enemy_attacks.update_hazards(.5)
        self.assertEqual(world.player.hp, 100)
        world.enemy_attacks.update_hazards(1)
        self.assertEqual(world.player.hp, 100)  # Still falling after the warning.
        world.enemy_attacks.update_hazards(.5)
        self.assertEqual(world.player.hp, 74)

    def test_water_mirror_shoots_between_two_fixed_endpoints(self):
        world = self.world
        world.spawn_boss(5, (-200,0))
        system = world.enemy_attacks
        system.schedule(world.enemies[0], 'foc_mirror')
        hazard = system.hazards[0]
        self.assertEqual(hazard.pos, Vector2(-200,0))
        self.assertEqual(hazard.end_pos, Vector2(0,0))
        system.update_hazards(hazard.stats['warning']-.01)
        self.assertFalse(system.shots)
        system.update_hazards(.02)
        self.assertEqual(len(system.shots),1)
        shot = system.shots[0]
        self.assertEqual(shot.key,'foc_mirror')
        self.assertGreater(shot.velocity.x,0)
        self.assertEqual(shot.velocity.y,0)
        world.player.pos = Vector2(0,100)
        self.assertEqual(hazard.end_pos,Vector2(0,0))
        system.update_shots(2)
        self.assertFalse(system.shots)
        self.assertAlmostEqual(shot.pos.x,0)
        for _ in range(60):
            system.update_hazards(.1)
        self.assertEqual(hazard.shots_fired,4)
        self.assertEqual(len(system.shots),3)  # First shot already reached the endpoint.
        self.assertNotIn(hazard, system.hazards)

    def test_mirrors_close_after_fourth_projectile_travel(self):
        world = self.world
        world.spawn_boss(5,(-200,0))
        system = world.enemy_attacks
        system.schedule(world.enemies[0],'foc_mirror')
        hazard = system.hazards[0]
        while hazard.shots_fired < 4:
            system.update_hazards(.01)
        self.assertIn(hazard,system.hazards)
        travel = 200/hazard.stats['speed']
        system.update_hazards(travel-.01)
        self.assertIn(hazard,system.hazards)
        system.update_hazards(.02)
        self.assertNotIn(hazard,system.hazards)

    def test_common_ranged_and_explosive_enemies(self):
        for kind in ('moth', 'eye', 'bomb'):
            world = World()
            enemy = Enemy(1, Vector2(50, 0), 100, 100, 0, 12, kind=kind, attack_timer=0)
            world.enemy_attacks.update_common(enemy, .02)
            self.assertTrue(world.enemy_attacks.hazards if kind == 'bomb' else world.enemy_attacks.shots)

    def test_victory_and_defeat(self):
        self.world.elapsed = self.world.duration+1
        self.tick()
        self.assertNotEqual(self.world.state, 'victory')
        self.world.defeated_bosses = set(range(6))
        self.tick()
        self.assertEqual(self.world.state, 'victory')
        self.setUp()
        self.world.player.hp = -1
        self.tick()
        self.assertEqual(self.world.state, 'defeat')


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def test_menu_selection_and_start(self):
        game = self.game
        game.handle_action('select')
        game.handle_action('character:flame_pirate')
        game.handle_action('map:caldera')
        game.handle_action('start')
        self.assertEqual(game.world.player.character_id, 'flame_pirate')
        self.assertEqual(game.world.map_id, 'caldera')
        self.assertIn('hiken', game.world.player.weapons)
        game.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertEqual(game.world.state, 'pause')

    def test_character_tabs_and_mode_clicks_at_both_resolutions(self):
        game=self.game
        for size in ((1280,720),(900,600)):
            game.screen=pygame.display.set_mode(size)
            for key in CHARACTERS:
                game.handle_action('select')
                game.ui.draw(game.screen,None)
                rect=next(r for r,a in game.ui.buttons if a=='character:'+key)
                game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))
                self.assertEqual(game.ui.character_id,key)
                game.ui.draw(game.screen,None)
                self.assertGreater(game.ui.menu_theme.info(key).get_width(),0)
            for duration in (300,600,900):
                game.ui.draw(game.screen,None)
                rect=next(r for r,a in game.ui.buttons if a==f'duration:{duration}')
                game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))
                self.assertEqual(game.ui.duration,duration)

    def test_number_four_selects_fourth_card(self):
        game = self.game
        game.handle_action('start')
        game.world.state = 'choice'
        game.world.choices = draw_upgrades(game.world.player, random.Random(4))
        chosen = game.world.choices[3]
        game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_4))
        self.assertEqual(game.world.state, 'play')
        inventory = game.world.player.weapons if chosen.kind == 'spell' else game.world.player.passives
        self.assertEqual(inventory[chosen.key], chosen.level)

    def test_grimoire_element_tabs_and_pagination(self):
        game=self.game
        game.handle_action('book')
        for i,key in enumerate(ELEMENTS):
            game.ui.draw(game.screen,None)
            rect=next(r for r,a in game.ui.buttons if a=='book_element:'+key)
            game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center))
            self.assertEqual(game.ui.book_page,i)
            self.assertEqual(sum(d['element']==key for d in SPELLS.values()),3)
            self.assertEqual(sum(d['element']==key for d in PASSIVES.values()),3)
        game.handle_action('book_next')
        self.assertEqual(game.ui.book_page,0)
        game.handle_action('book_prev')
        self.assertEqual(game.ui.book_page,4)

    def test_all_screens_at_both_sizes(self):
        game = self.game
        for size in ((1280, 720), (900, 600)):
            game.screen = pygame.display.set_mode(size)
            for page in ('home', 'select', 'book', 'options'):
                game.ui.page = page
                game.renderer.draw(game.screen, None)
                game.ui.draw(game.screen, None)
                for rect, _ in game.ui.buttons:
                    self.assertTrue(game.screen.get_rect().contains(rect))
            game.handle_action('start')
            for state in ('play', 'pause', 'victory', 'defeat', 'choice'):
                game.world.state = state
                game.world.choices = available_upgrades(game.world.player)[:4]
                game.renderer.draw(game.screen, game.world)
                game.ui.draw(game.screen, game.world)

    def test_all_art_frames_and_transformations(self):
        assets = self.game.renderer.assets
        for key in list(SPELLS)+list(PASSIVES):
            self.assertEqual(assets.item_icon(key).get_size(), (56, 56))
        for key in BOSS_ATTACKS:
            self.assertEqual(assets.boss_attack(key, (80, 80)).get_size(), (80, 80))
        for key in SPELLS:
            assets.magic(key, (90, 70))
        for character in CHARACTERS:
            for frame in range(4):
                for moving in (True, False):
                    assets.character(character, moving, frame/8)
                for element in ELEMENTS:
                    world = World(character_id=character)
                    world.player.weapons = {k: 1 for k, d in SPELLS.items() if d['element'] == element}
                    self.game.renderer.draw_player(self.game.screen, Vector2(300, 250), frame/5, world.player)

    def test_sustained_combat_with_every_boss(self):
        game = self.game
        for character in CHARACTERS:
            world = World(seed=10, character_id=character)
            world.player.weapons = {key: 3 for key, data in SPELLS.items() if data['element'] == CHARACTERS[character]['element']}
            world.player.max_hp = world.player.hp = 100000
            world.next_boss = 6
            world.spawn_timer = 999
            for index in range(6):
                world.spawn_boss(index, Vector2(1, 0).rotate(index*60)*220)
            for step in range(600):
                if world.state == 'choice':
                    world.choose_upgrade(0)
                world.update(1/60, Vector2(), (1280, 720))
                if step % 60 == 0:
                    game.renderer.draw(game.screen, world)
            self.assertTrue(world.player.hp < 100000)
            self.assertTrue(world.elapsed > 9 or (world.state == 'victory' and len(world.defeated_bosses) == 6))


if __name__ == '__main__':
    unittest.main()
