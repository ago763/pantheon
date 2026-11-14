import unittest
from pygame import Vector2
from goetia.world import World
from goetia.catalog import SPELLS
from goetia.entities import Enemy


class FootprintTests(unittest.TestCase):
    def world(self, element):
        w = World()
        w.player.weapons = {k:1 for k,v in SPELLS.items() if v['element']==element}
        w.player.moving = True
        return w

    def test_five_max_and_fixed_positions(self):
        for element in ('ice','fire','lightning'):
            w = self.world(element)
            for i in range(20):
                w.player.pos.x = i*40
                w.update_footprints(.05)
                self.assertLessEqual(len(w.footprints),5)
            self.assertEqual(len(w.footprints),5)
            positions = [p.pos.copy() for p in w.footprints]
            w.player.moving = False
            w.update_footprints(.1)
            self.assertEqual([p.pos for p in w.footprints],positions)
            w.update_footprints(3)
            self.assertFalse(w.footprints)

    def test_effects_on_enemies_and_no_trail_without_form(self):
        for element in ('ice','fire'):
            w = self.world(element)
            e = Enemy(1,Vector2(),100,100,0,12)
            w.enemies = [e]
            w.update_footprints(.01)
            self.assertGreater(e.slow if element=='ice' else e.burn,0)
        w = World()
        w.player.moving = True
        w.update_footprints(.1)
        self.assertFalse(w.footprints)

    def test_light_is_one_bounded_path_that_follows_turns(self):
        w=self.world('light')
        for i in range(30):
            w.player.pos=Vector2(i*5,0)
            w.update_footprints(.01)
        for i in range(20):
            w.player.pos=Vector2(145,i*5)
            w.update_footprints(.01)
        self.assertFalse(w.footprints)
        self.assertGreater(len(w.light_trail),5)
        self.assertTrue(any(p.pos.y==22 for p in w.light_trail))
        self.assertTrue(any(p.pos.y>22 for p in w.light_trail))
        length=sum(a.pos.distance_to(b.pos) for a,b in zip(w.light_trail,w.light_trail[1:]))
        self.assertLessEqual(length,220)
        w.player.moving=False
        w.update_footprints(3)
        self.assertFalse(w.light_trail)
