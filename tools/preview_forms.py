"""Five transformations animated with the actual sprites, trails and renderer."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import pygame
from goetia.app import Game
from goetia.world import World
from goetia.catalog import SPELLS, ELEMENTS
from preview_animation import save_apng

game = Game()
entries = [('ice','ice_witch'),('dark','shadow_monarch'),('light','light_elf'),
           ('lightning','lightning_assassin'),('fire','flame_pirate')]
worlds=[]
for element,character in entries:
    world=World(character_id=character)
    world.player.weapons={k:1 for k,v in SPELLS.items() if v['element']==element}
    worlds.append(world)
folder=ROOT/'previews'/'formas'
folder.mkdir(exist_ok=True)
frames=[]
individual=[[] for _ in entries]
for step in range(360):
    canvas=pygame.Surface((1000,580))
    canvas.fill('#0b1420')
    for i,(world,(element,_)) in enumerate(zip(worlds,entries)):
        world.elapsed+=1/60
        world.player.moving=step<180
        if world.player.moving:
            world.player.pos.x+=2.5
        world.update_footprints(1/60)
        panel=pygame.Surface((320,260))
        game.renderer.draw(panel,world)
        game.ui.text(panel,ELEMENTS[element]['name'].upper(),(12,12),18,ELEMENTS[element]['color'])
        if step%5==0:
            individual[i].append(panel.copy())
        x=(i%3)*330+5 if i<3 else (i-3)*330+170
        y=10 if i<3 else 280
        canvas.blit(panel,(x,y))
    game.ui.text(canvas,'3 magias do mesmo elemento · movimento e parada',(500,560),18,center=True)
    if step%5==0:
        frames.append(canvas)
save_apng(ROOT/'previews'/'formas-animadas.png',frames,12)
for (element,_),sequence in zip(entries,individual):
    save_apng(folder/f'{element}.png',sequence,12)
pygame.image.save(frames[28],str(folder/'conferencia.png'))
pygame.quit()
print('previews/formas-animadas.png')
