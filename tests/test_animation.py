import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Vector2
from goetia.animation import ANIMATIONS, frame_index
from goetia.assets import Assets
from goetia.catalog import ELEMENTS, SPELLS
from goetia.entities import Enemy, SpellArea, Footprint
from goetia.progression import spell_stats
from goetia.renderer import Renderer
from goetia.world import World


class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.display.set_mode((640, 480))
        cls.assets = Assets()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_variable_count_and_wrap(self):
        for count in (1, 2, 3, 4, 5, 8):
            self.assertEqual([frame_index(t/10, 10, count) for t in range(count+1)], list(range(count))+[0])
        self.assertEqual(frame_index(500, 0, 3), 0)

    def test_all_sequences_fit_source_and_change_pixels(self):
        for key, sequence in ANIMATIONS.items():
            with self.subTest(key=key):
                count = len(sequence['frames'])
                self.assertEqual(len({tuple(rect) for rect in sequence['frames']}), count)
                bounds = self.assets.sheet(sequence['sheet']).get_rect()
                self.assertTrue(all(bounds.contains(pygame.Rect(rect)) for rect in sequence['frames']))
                frames = [pygame.image.tobytes(self.assets.magic(key, (100, 80), (i+.01)/SPELLS[key]['animation_fps']), 'RGBA') for i in range(count)]
                self.assertGreater(len(set(frames)), 1)

    def test_orb_count_by_level_and_evolution(self):
        world = World()
        area = SpellArea(Vector2(), 'storm_orbs', 20, 1, 10)
        for level, count in [(1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 7)]:
            world.player.weapons = {'storm_orbs': level}
            self.assertEqual(len(world.combat.orbit_points(area)), count)

    def test_orbits_persist_without_targets(self):
        world = World()
        world.player.weapons = {'storm_orbs': 1}
        for _ in range(300):
            world.elapsed += .016
            world.combat.update(.016)
            self.assertEqual(len(world.combat.areas), 1)

    def test_orb_collision_follows_the_orb_not_entire_path(self):
        world = World()
        world.player.weapons = {'storm_orbs': 1}
        stats = spell_stats(world.player, 'storm_orbs')
        area = SpellArea(Vector2(), 'storm_orbs', stats['radius'], 1, 15)
        world.combat.areas = [area]
        point = world.combat.orbit_points(area)[0]
        world.enemies = [Enemy(1, point.copy(), 100, 100, 0, 5), Enemy(2, Vector2(), 100, 100, 0, 5)]
        world.combat.update_areas(.01)
        self.assertEqual(world.enemies[0].hp, 100-stats['damage'])
        self.assertEqual(world.enemies[1].hp, 100)

    def test_each_transformation_changes_across_four_steps(self):
        renderer = Renderer()
        world = World()
        for element in ELEMENTS:
            world.player.weapons = {key: 1 for key, value in SPELLS.items() if value['element'] == element}
            snapshots = []
            for step in range(4):
                surface = pygame.Surface((180, 180))
                surface.fill('#182636')
                if 'trail' in ELEMENTS[element]:
                    footprint = Footprint(Vector2(55,132),element,age=(step+.05)/ELEMENTS[element]['animation_fps'])
                    renderer.transformations.draw_footprint(surface,footprint,Vector2())
                renderer.draw_player(surface, Vector2(90, 110), (step+.05)/ELEMENTS[element]['animation_fps'], world.player)
                snapshots.append(pygame.image.tobytes(surface, 'RGB'))
            self.assertEqual(len(set(snapshots)), 4)

    def test_halos_animate_without_character_or_ground_trail(self):
        renderer = Renderer()
        for element in ('dark','light'):
            snapshots = []
            for step in range(4):
                surface = pygame.Surface((180,180),pygame.SRCALPHA)
                renderer.transformations.draw(surface,element,'ice_witch',Vector2(90,140),
                                              (step+.05)/ELEMENTS[element]['animation_fps'],'front')
                snapshots.append(pygame.image.tobytes(surface,'RGBA'))
            self.assertEqual(len(set(snapshots)),4)


if __name__ == '__main__':
    unittest.main()
