"""Janela, eventos e loop principal do Pygame."""

import pygame
from pathlib import Path
from pygame import Vector2

from . import config
from .renderer import Renderer
from .ui import UI
from .world import World


class Game:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        icon_path = Path(__file__).resolve().parent.parent / 'assets/images/ui/pantheon-icon.png'
        pygame.display.set_icon(pygame.image.load(str(icon_path)))
        self.screen = pygame.display.set_mode(config.WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer()
        self.ui = UI()
        self.world = None
        self.running = True

    def handle_action(self, action):
        if action == "start":
            self.world = World(character_id=self.ui.character_id, map_id=self.ui.map_id, duration=self.ui.duration)
        elif action and action.startswith('duration:'):
            self.ui.duration = int(action.split(':')[1])
        elif action in ("home", "select", "book", "options"):
            self.world = None
            self.ui.page = action
        elif action and action.startswith("character:"):
            self.ui.character_id = action.split(":")[1]
        elif action and action.startswith("map:"):
            self.ui.map_id = action.split(":")[1]
        elif action and action.startswith('book_element:'):
            from .catalog import ELEMENTS
            self.ui.book_page = list(ELEMENTS).index(action.split(':')[1])
        elif action == "book_prev":
            self.ui.book_page = (self.ui.book_page-1) % 5
        elif action == "book_next":
            self.ui.book_page = (self.ui.book_page+1) % 5
        elif action == "fps":
            self.ui.show_fps = not self.ui.show_fps
        elif action == "fullscreen":
            if self.screen.get_flags() & pygame.FULLSCREEN:
                self.screen = pygame.display.set_mode(config.WINDOW_SIZE, pygame.RESIZABLE)
            else:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        elif action == "quit":
            self.running = False
        elif action == "pause" and self.world:
            self.world.toggle_pause()
        elif action and action.startswith("choice:") and self.world:
            self.world.choose_upgrade(int(action.split(":")[1]))
        # Não reutilizar áreas clicáveis de uma tela anterior no mesmo quadro.
        self.ui.buttons = []

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            size = (max(config.MIN_WINDOW_SIZE[0], event.w), max(config.MIN_WINDOW_SIZE[1], event.h))
            self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        elif event.type == pygame.WINDOWFOCUSLOST:
            if self.world and self.world.state == "play":
                self.world.toggle_pause()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_action(self.ui.action_at(event.pos))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.handle_action("pause" if self.world else "home")
            elif event.key == pygame.K_RETURN:
                if self.world is None:
                    self.handle_action("start" if self.ui.page == "select" else "select")
                elif self.world.state in ("victory", "defeat"):
                    self.handle_action("start")
                elif self.world.state == "pause":
                    self.handle_action("pause")
            elif self.world and self.world.state == "choice":
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.handle_action(f"choice:{event.key-pygame.K_1}")

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(config.FPS)/1000, 0.035)
                for event in pygame.event.get():
                    self.handle_event(event)
                keys = pygame.key.get_pressed()
                movement = Vector2(
                    int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                    int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]),
                )
                if self.world:
                    self.world.update(dt, movement, self.screen.get_size())
                self.renderer.draw(self.screen, self.world)
                self.ui.draw(self.screen, self.world)
                if self.ui.show_fps:
                    self.ui.text(self.screen, f"{self.clock.get_fps():.0f} FPS", (self.screen.get_width()-95, 60), 14)
                pygame.display.flip()
        finally:
            pygame.quit()
