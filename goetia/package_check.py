"""Headless verification of the packaged executable and its bundled resources."""
import json
from pathlib import Path
import traceback
import pygame
from pygame import Vector2
from .app import Game
from .catalog import CHARACTERS, SPELLS, BOSS_ATTACKS
from .entities import Enemy
from .world import World


def run(report_path):
    report={'ok':False,'menus':0,'characters':0,'spells':0,'boss_attacks':0}
    try:
        game=Game()
        for page in ('home','select','book','options'):
            game.ui.page=page
            game.ui.draw(game.screen,None)
            report['menus']+=1
        for character in CHARACTERS:
            game.ui.character_id=character
            game.ui.page='select'
            game.ui.draw(game.screen,None)
            report['characters']+=1
        for key in SPELLS:
            world=World()
            world.player.weapons={key:1}
            world.enemies=[Enemy(1,Vector2(100,0),10000,10000,0,15)]
            world.combat.update(.02)
            game.renderer.draw(game.screen,world)
            report['spells']+=1
        for key,stats in BOSS_ATTACKS.items():
            world=World()
            world.spawn_boss(stats['boss'],(-150,0))
            world.enemy_attacks.schedule(world.enemies[0],key)
            world.enemy_attacks.update_hazards(stats['warning']+.1)
            game.renderer.draw(game.screen,world)
            report['boss_attacks']+=1
        report['ok']=True
    except Exception:
        report['error']=traceback.format_exc()
    finally:
        pygame.quit()
        Path(report_path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['ok'] else 1
