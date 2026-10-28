"""SHADOW CLASH - Main Application Engine.

Manages Pygame lifecycle, resizable window surface, 60 FPS clock timing,
delta-time clamping, and global event dispatching.
"""

from __future__ import annotations
import sys
import time
import pygame

from settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, TARGET_FPS, WINDOW_TITLE
)
from game.scene_manager import SceneManager
from game.input_manager import InputManager
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from scenes.main_menu import MainMenuScene


class Application:
    """Core runtime engine for Shadow Clash."""

    def __init__(self, headless: bool = False) -> None:
        self.headless = headless
        self.is_running: bool = False
        self.clock = pygame.time.Clock()
        
        # Initialize Core Pygame Subsystems
        pygame.init()
        pygame.font.init()
        
        # Window & Display set_mode must happen before surface conversion
        if not self.headless:
            self.window = pygame.display.set_mode(
                (LOGICAL_WIDTH, LOGICAL_HEIGHT), 
                pygame.RESIZABLE | pygame.DOUBLEBUF
            )
            pygame.display.set_caption(WINDOW_TITLE)
        else:
            self.window = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT))

        # Audio, Assets, Input, and Scene Management
        self.audio_mgr = AudioManager.get_instance()
        self.asset_mgr = AssetManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        self.scene_mgr = SceneManager()

        if not self.headless:
            # Set App Window Icon
            coin_icon = self.asset_mgr.get_icon("coin")
            if coin_icon:
                pygame.display.set_icon(coin_icon)

        self.scene_mgr.update_resolution(LOGICAL_WIDTH, LOGICAL_HEIGHT)

    def run(self) -> None:
        """Start and run the main game loop."""
        self.is_running = True
        
        # Launch into Main Menu
        self.scene_mgr.change_scene(MainMenuScene(self.scene_mgr))
        
        last_time = time.perf_counter()

        while self.is_running:
            # High-precision delta time with safety clamping
            now = time.perf_counter()
            raw_dt = now - last_time
            last_time = now
            dt = min(0.05, max(0.001, raw_dt))
            
            # 1. Begin Frame Input Prep
            self.input_mgr.begin_frame(now)

            # 2. Event Dispatching
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                elif event.type == pygame.VIDEORESIZE and not self.headless:
                    w, h = max(640, event.w), max(360, event.h)
                    self.window = pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF)
                    self.scene_mgr.update_resolution(w, h)

                self.input_mgr.process_event(event)
                self.scene_mgr.handle_event(event)

            # 3. Logic Update
            self.scene_mgr.update(dt)

            # 4. Presentation Rendering
            self.scene_mgr.render(self.window)
            if not self.headless:
                pygame.display.flip()

            # 5. Frame Rate Cap (60 FPS)
            self.clock.tick(TARGET_FPS)

    def quit(self) -> None:
        """Terminate game engine cleanly."""
        self.is_running = False
        self.audio_mgr.stop_bgm()
        pygame.quit()
        sys.exit(0)
