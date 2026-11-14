"""Renderiza o próprio jogo, sem imagens geradas: python tools/render_previews.py."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from pygame import Vector2
from goetia.app import Game
from goetia.catalog import CHARACTERS, ELEMENTS, SPELLS
from goetia.progression import available_upgrades
from goetia.world import World


def main():
    folder = ROOT / "previews"
    folder.mkdir(exist_ok=True)
    game = Game()

    def save_screen(name):
        game.renderer.draw(game.screen, game.world)
        game.ui.draw(game.screen, game.world)
        pygame.image.save(game.screen, str(folder / name))

    save_screen("menu.png")
    game.ui.page = "select"
    save_screen("selecao.png")
    game.handle_action("start")
    world = game.world
    world.state = "choice"
    pool = available_upgrades(world.player)
    world.choices = [next(card for card in pool if card.key == key) for key in ("hyorinmaru", "hiken", "black_hole", "storm_orbs")]
    save_screen("cartas.png")

    sheet = pygame.Surface((1500, 760))
    sheet.fill("#0b1420")
    game.ui.text(sheet, "TRANSFORMAÇÕES · 3 MAGIAS DO MESMO ELEMENTO", (750, 35), 28, "#d2b879", True)
    game.ui.text(sheet, "Renderização real do jogo · sprites ampliados 2× sem suavização", (750, 75), 18, center=True)
    for i, (key, char) in enumerate(CHARACTERS.items()):
        x = i*300
        game.ui.text(sheet, char["name"], (x+150, 120), 21, ELEMENTS[char["element"]]["color"], True)
        for row in range(2):
            sample = pygame.Surface((150, 140))
            sample.fill("#182636")
            preview = World(character_id=key)
            preview.player.moving = False
            if row:
                preview.player.weapons = {spell: 1 for spell, data in SPELLS.items() if data["element"] == char["element"]}
            game.renderer.draw_player(sample, Vector2(75, 90), .42, preview.player)
            sheet.blit(pygame.transform.scale(sample, (300, 280)), (x, 155+row*285))
            game.ui.text(sheet, "TRANSFORMADO" if row else "BASE", (x+150, 176+row*285), 15, center=True)
        game.ui.wrapped_text(sheet, ELEMENTS[char["element"]]["form"], pygame.Rect(x+15, 724, 270, 36), 17, ELEMENTS[char["element"]]["color"])
    pygame.image.save(sheet, str(folder / "transformacoes.png"))

    matrix = pygame.Surface((1200, 1140))
    matrix.fill("#0b1420")
    game.ui.text(matrix, "ENCAIXE DAS CINCO FORMAS NOS CINCO PERSONAGENS", (600, 28), 23, "#d2b879", True)
    for col, element in enumerate(ELEMENTS):
        game.ui.text(matrix, ELEMENTS[element]["name"], (120+240*col, 65), 20, ELEMENTS[element]["color"], True)
        for row, key in enumerate(CHARACTERS):
            sample = pygame.Surface((120, 96))
            sample.fill("#182636")
            preview = World(character_id=key)
            preview.player.moving = True
            preview.player.facing = -1 if row % 2 else 1
            preview.player.weapons = {spell: 1 for spell, data in SPELLS.items() if data["element"] == element}
            game.renderer.draw_player(sample, Vector2(60, 64), .55, preview.player)
            matrix.blit(pygame.transform.scale(sample, (240, 192)), (col*240, 85+row*210))
            game.ui.text(matrix, CHARACTERS[key]["name"], (col*240+120, 282+row*210), 14, center=True)
    pygame.image.save(matrix, str(folder / "todas-combinacoes.png"))
    pygame.quit()
    print(f"Prévias salvas em {folder}")


if __name__ == "__main__":
    main()
