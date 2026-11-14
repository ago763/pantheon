"""Preview the five persistent footprints using the real game renderer."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ['SDL_VIDEODRIVER']='dummy'
import pygame
from goetia.app import Game
from goetia.world import World
from goetia.catalog import SPELLS
from preview_animation import save_apng

game = Game()
worlds = [World(character_id=c) for c in ['ice_witch','flame_pirate']]
for world,element in zip(worlds,['ice','fire']):
    world.player.weapons = {k:1 for k,v in SPELLS.items() if v['element']==element}
frames=[]
for step in range(360):
    canvas=pygame.Surface((800,300))
    for i,world in enumerate(worlds):
        world.elapsed += 1/60
        world.player.moving = step < 180
        if world.player.moving:
            world.player.pos.x += 3
        world.update_footprints(1/60)
        panel=pygame.Surface((400,300))
        game.renderer.draw(panel,world)
        game.ui.text(panel,('GELO' if i==0 else 'FOGO')+f' · {len(world.footprints)}/5 pegadas',(12,16),18)
        canvas.blit(panel,(i*400,0))
    if step%5==0:
        frames.append(canvas)
save_apng(ROOT/'previews'/'pegadas.png',frames,12)
pygame.quit()
