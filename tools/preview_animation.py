"""Prévias com o renderizador real. APNG usa apenas a biblioteca padrão."""

import os
import sys
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Vector2
from goetia.app import Game
from goetia.catalog import SPELLS
from goetia.animation import ANIMATIONS
from goetia.world import World


def save_apng(path, frames, fps):
    def chunk(kind, data):
        return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff)
    width, height = frames[0].get_size()
    output = bytearray(b'\x89PNG\r\n\x1a\n')
    output += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    output += chunk(b'acTL', struct.pack('>II', len(frames), 0))
    sequence = 0
    for i, frame in enumerate(frames):
        output += chunk(b'fcTL', struct.pack('>IIIIIHHBB', sequence, width, height, 0, 0, 1, fps, 0, 0))
        sequence += 1
        pixels = pygame.image.tobytes(frame, 'RGBA')
        filtered = b''.join(b'\x00'+pixels[y*width*4:(y+1)*width*4] for y in range(height))
        data = zlib.compress(filtered)
        if i == 0:
            output += chunk(b'IDAT', data)
        else:
            output += chunk(b'fdAT', struct.pack('>I', sequence)+data)
            sequence += 1
    output += chunk(b'IEND', b'')
    path.write_bytes(output)


def main():
    game = Game()
    folder = ROOT/'previews'
    folder.mkdir(exist_ok=True)
    sheet = pygame.Surface((1200, 800))
    sheet.fill('#152333')
    for i, (key, spell) in enumerate(SPELLS.items()):
        x, y = (i % 3)*400, (i//3)*160
        game.ui.text(sheet, spell['name'], (x+200, y+22), 19, center=True)
        count = len(ANIMATIONS[key]['frames'])
        cell_w = 400//count
        for frame in range(count):
            image = game.renderer.assets.magic(key, (cell_w-10, 80), (frame+.05)/spell['animation_fps'])
            sheet.blit(image, (x+frame*cell_w+5, y+48))
            game.ui.text(sheet, str(frame+1), (x+frame*cell_w+cell_w//2, y+145), 14, center=True)
    pygame.image.save(sheet, str(folder/'magias-quadros-disponiveis.png'))

    worlds = [World(), World()]
    for world, level in zip(worlds, (1, 5)):
        world.player.weapons = {'storm_orbs': level}
        world.combat.update(.001)
    frames = []
    for frame in range(36):
        result = pygame.Surface((900, 330))
        for i, world in enumerate(worlds):
            world.elapsed = frame/12
            canvas = pygame.Surface((450, 330))
            game.renderer.draw(canvas, world)
            game.ui.text(canvas, f"NÍVEL {1 if i == 0 else 5} · {3 if i == 0 else 7} ORBES", (225, 30), 24, center=True)
            result.blit(canvas, (i*450, 0))
        frames.append(result)
    save_apng(folder/'orbes-animados.png', frames, 12)
    pygame.image.save(frames[0], str(folder/'orbes-niveis.png'))
    (folder/'animacoes.html').write_text('<!doctype html><meta charset="utf-8"><title>Orbes animados</title><body style="background:#0b1420;color:white;font-family:Arial;text-align:center"><h1>Órbita real · nível 1 e nível 5</h1><img src="orbes-animados.png" style="max-width:100%"><p>Três e sete esferas independentes, animadas em quatro quadros.</p></body>', encoding='utf-8')
    pygame.quit()
    print('Prévias de animação salvas em previews/')


if __name__ == '__main__':
    main()
