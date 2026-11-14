"""Isolated attacks using the game's real simulation and renderer; no invented frames."""
import os
import sys
import html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame import Vector2
from goetia.app import Game
from goetia.assets import BOSS_NAMES
from goetia.catalog import BOSS_ATTACKS, ENEMIES
from goetia.entities import Enemy
from goetia.world import World
from goetia.progression import spell_stats
from preview_animation import save_apng


def main():
    game = Game()
    folder = ROOT/'previews'/'ataques'
    folder.mkdir(exist_ok=True)
    cards = []
    cases = [(k, f'{BOSS_NAMES[v["boss"]]} · {v["name"]}', 'boss') for k,v in BOSS_ATTACKS.items()]
    cases += [(k, n, 'common') for k,n in [('moth','Mariposa · Projétil'),('eye','Olho · Projétil'),('bomb','Explosivo · Detonação'),('tank','Tanque · Dano de contato')]]
    cases += [(f'punishment-{level}', f'Ray of Punishment · Nível {level}', 'light') for level in (1,3,5)]
    if len(sys.argv) > 1:
        cases = [case for case in cases if case[0] in sys.argv[1:]]
    for key, name, group in cases:
        world = World(seed=14)
        world.player.hp = world.player.max_hp = 100000
        world.player.weapons = {}
        world.next_boss = 6
        world.spawn_timer = 999
        if group == 'boss':
            world.spawn_boss(BOSS_ATTACKS[key]['boss'], (-170,-25))
            enemy = world.enemies[0]
        elif group == 'common':
            stats = ENEMIES[key]
            enemy = Enemy(1, Vector2(-65 if key == 'bomb' else -170, 0), 10000,10000,
                          stats['speed'], stats['radius'], kind=key, attack_timer=0)
            world.enemies = [enemy]
        else:
            world.player.character_id = 'light_elf'
            world.player.weapons = {'punishment': int(key[-1])}
            world.enemies = [Enemy(i,Vector2(x,y),100000,100000,0,20,kind='tank')
                             for i,(x,y) in enumerate([(-120,65),(0,95),(125,65)])]
        frames=[]
        surface=pygame.Surface((640,440))
        for step in range(8*60):
            dt=1/60
            world.elapsed += dt
            world.player.invulnerability = max(0, world.player.invulnerability-dt)
            if step == 24:
                if group == 'boss': world.enemy_attacks.schedule(enemy,key)
                elif group == 'light': world.combat.cast('punishment',spell_stats(world.player,'punishment'),world.enemies)
            if group == 'common':
                if key == 'tank': world.move_enemies(dt)
                else: world.enemy_attacks.update_common(enemy,dt)
            world.enemy_attacks.update_hazards(dt)
            world.enemy_attacks.update_shots(dt)
            world.update_bosses(dt)
            world.combat.update_areas(dt)
            world.effects = [e for e in world.effects if e.life > dt]
            for e in world.effects: e.life -= dt
            if step%5 == 0:
                game.renderer.draw(surface,world)
                frames.append(pygame.transform.scale(surface,(480,330)))
        save_apng(folder/f'{key}.png',frames,12)
        pygame.image.save(frames[18],str(folder/f'{key}-poster.png'))
        note = 'Dois espelhos animados: na origem e no alvo. Projéteis viajam entre eles.' if key == 'foc_mirror' else 'Este inimigo ataca por contato; não possui projétil.' if key == 'tank' else ''
        cards.append(f'<article data-group="{group}"><h2>{html.escape(name)}</h2><a href="ataques/{key}.png"><img src="ataques/{key}.png" loading="lazy" alt="{html.escape(name)}"></a><p>{note}</p></article>')
        print(key,flush=True)
    page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Ataques dos chefes e inimigos</title>
<style>body{background:#0b1420;color:#e4e9f0;font:16px Georgia;margin:30px}h1{color:#e6c481}p{line-height:1.6}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}article{background:#152334;border:1px solid #59637a;border-radius:8px;overflow:hidden}h2{font-size:20px;padding:0 18px}article p{padding:0 18px}img{width:100%;image-rendering:pixelated}button{margin:8px;padding:12px;background:#24364c;color:white;border:1px solid #ceb985;cursor:pointer}a{color:#e6c481}</style>
<h1>Chefes, inimigos e feixes de luz</h1><p>18 ataques dos seis chefes + 4 tipos de inimigos + Ray of Punishment nos níveis 1, 3 e 5. Simulações de 8 segundos usando o código do jogo. Clique em uma animação para ampliar.</p>
<p>As artes dos ataques de chefes desta folha têm um desenho por ataque, exceto a grade elétrica e os novos espelhos/projéteis de água. A animação mostra movimento, avisos, duração e colisões reais; não representa novos quadros desenhados.</p>
<nav><button onclick="filter('all')">Todos</button><button onclick="filter('boss')">Chefes · 18</button><button onclick="filter('common')">Inimigos · 4</button><button onclick="filter('light')">Ray of Punishment · 3 níveis</button></nav><section>CARDS</section>
<p><a href="todas-magias.html">Ver todas as magias do jogador</a></p><script>function filter(g){document.querySelectorAll('article').forEach(x=>x.style.display=g==='all'||x.dataset.group===g?'':'none')}</script></html>'''
    if len(sys.argv) == 1:
        (folder.parent/'ataques-inimigos.html').write_text(page.replace('CARDS','\n'.join(cards)),encoding='utf-8')
    pygame.quit()


if __name__ == '__main__':
    main()
