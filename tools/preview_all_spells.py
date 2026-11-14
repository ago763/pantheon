"""Galeria animada das 15 magias usando simulação e renderização reais."""

import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame import Vector2
from goetia.app import Game
from goetia.animation import ANIMATIONS
from goetia.catalog import CHARACTERS, ELEMENTS, SPELLS
from goetia.entities import Enemy
from goetia.world import World
from preview_animation import save_apng


def main():
    game = Game()
    folder = ROOT / 'previews' / 'magias'
    folder.mkdir(parents=True, exist_ok=True)
    cards = []
    for key, spell in SPELLS.items():
        character = next(k for k, c in CHARACTERS.items() if c['element'] == spell['element'])
        world = World(seed=40, character_id=character)
        world.player.weapons = {key: 1}
        world.spawn_timer = 999
        world.next_boss = 6
        # Alvos de treino imóveis: não lançam ataques que escondam a magia em análise.
        world.enemy_attacks.update = lambda dt: None
        world.enemies = [Enemy(i, Vector2(pos), 100000, 100000, 0, 16, kind='tank', tank=True)
                         for i, pos in enumerate(((110, 0), (-90, 10), (60, 80), (20, -95), (190, -70)))]
        frames = []
        render = pygame.Surface((560, 380))
        for step in range(72*5):
            world.update(1/60, Vector2(), render.get_size())
            if step % 5 == 0:
                game.renderer.draw(render, world)
                frames.append(pygame.transform.scale(render, (420, 285)))
        save_apng(folder/f'{key}.png', frames, 12)
        pygame.image.save(frames[12], str(folder/f'{key}-poster.png'))
        element = ELEMENTS[spell['element']]
        count = len(ANIMATIONS[key]['frames'])
        timing = 'Estágios: 0 s / 0,5 s / 1 s; último mantido' if spell.get('single_group') else 'Sequência de queda e impacto' if key == 'demons_extract' else 'Crescimento e dissipação pela trajetória' if key == 'yami_matoi' else f"{spell['animation_fps']} quadros/s"
        cards.append(f'''<article data-element="{spell['element']}" style="--accent:{element['color']}">
<header><span>{html.escape(element['name'])} · Nível 1</span><h2>{html.escape(spell['name'])}</h2></header>
<div class="player"><img class="poster" src="magias/{key}-poster.png" alt="{html.escape(spell['name'])}">
<img class="motion" src="magias/{key}.png" loading="lazy" alt="Simulação animada de {html.escape(spell['name'])}"></div>
<div class="details"><p>{html.escape(spell['description'])}</p><small>{count} quadros disponíveis · {timing}</small>
<a href="magias/{key}.png" target="_blank">Abrir animação ampliada ↗</a></div></article>''')
        print(f'{key}: {len(frames)} quadros da simulação', flush=True)
    page = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Goetia Survivors · Magias animadas</title><style>
*{box-sizing:border-box}body{margin:0;background:#090f18;color:#edf1f7;font:16px/1.5 Arial,sans-serif}.wrap{max-width:1380px;margin:auto;padding:44px 26px}h1{font-family:Georgia,serif;font-size:clamp(30px,4vw,48px);font-weight:normal;margin:8px 0;color:#e2c58e}.eyebrow{letter-spacing:3px;color:#b7a27b;font-size:12px}p{color:#b1bfd1}.intro{max-width:870px}.toolbar{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:26px 0;position:sticky;top:0;background:#090f18ed;padding:14px 0;z-index:2}select,button{background:#1a2739;color:#fff;padding:11px 17px;border:1px solid #54627b;border-radius:6px;font:inherit;cursor:pointer}button:hover{background:#2d3d55}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}article{background:#111c2a;border:1px solid #29364b;border-top:3px solid var(--accent);border-radius:9px;overflow:hidden}article header{padding:18px 20px}header span{color:var(--accent);text-transform:uppercase;letter-spacing:1px;font-size:11px}h2{font:22px Georgia,serif;margin:5px 0}.player{position:relative;aspect-ratio:420/285;background:#0d1520}.player img{width:100%;height:100%;display:block;image-rendering:pixelated;position:absolute;inset:0}.paused .motion{visibility:hidden}.details{padding:0 20px 20px}.details p{min-height:48px;font-size:14px}.details small{display:block;color:#8fabc8;font-size:12px}a{display:inline-block;color:#e2c58e;margin-top:15px;font-size:13px}.note{padding:17px 20px;border-left:3px solid #bba06a;background:#141e2b;font-size:14px;color:#bdcad9}article[hidden]{display:none}@media(max-width:1050px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.grid{grid-template-columns:1fr}.wrap{padding:28px 16px}}
</style></head><body><main class="wrap"><div class="eyebrow">GOETIA SURVIVORS · PRÉVIA DO JOGO</div>
<h1>As quinze magias, em movimento</h1><p class="intro">Simulações de seis segundos, em repetição, usando o combate e o renderizador do jogo. Cada personagem está equipado apenas com a magia indicada, no nível 1, contra alvos de treino imóveis.</p>
<div class="note">Esta galeria mostra os efeitos já implementados: quadros animados, trajetória, órbitas, áreas e impactos atuais. Efeitos ainda pendentes, como partículas completas, estilhaços e algumas evoluções, não aparecem aqui. A quantidade de quadros do sprite é diferente da quantidade de quadros da simulação.</div>
<div class="toolbar"><label for="element">Elemento</label><select id="element"><option value="all">Todos · 15 magias</option><option value="ice">Gelo</option><option value="dark">Escuridão</option><option value="light">Luz</option><option value="lightning">Raio</option><option value="fire">Fogo</option></select><button id="motion" aria-pressed="true">Mostrar imagens paradas</button><span id="count">15 magias</span></div><section class="grid">CARDS</section>
<p><a href="animacoes.html">Ver também: órbita elétrica no nível 1 e nível 5</a></p></main>
<script>document.getElementById('element').onchange=function(){let count=0;document.querySelectorAll('article').forEach(card=>{card.hidden=this.value!=='all'&&card.dataset.element!==this.value;if(!card.hidden)count++});document.getElementById('count').textContent=count+' magias'};document.getElementById('motion').onclick=function(){const paused=document.body.classList.toggle('paused');this.textContent=paused?'Mostrar animações':'Mostrar imagens paradas';this.setAttribute('aria-pressed',String(!paused))};</script></body></html>'''
    (folder.parent/'todas-magias.html').write_text(page.replace('CARDS', '\n'.join(cards)), encoding='utf-8')
    pygame.quit()
    print('Galeria: previews/todas-magias.html')


if __name__ == '__main__':
    main()
