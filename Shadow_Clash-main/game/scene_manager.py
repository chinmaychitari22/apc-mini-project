"""SHADOW CLASH - Scene Manager with High-Fidelity Aspect Scaling.

Maintains scene lifecycle stack, renders all gameplay to a fixed 1280x720 canvas,
and scales it seamlessly onto any window resolution with letterboxing.
"""

from __future__ import annotations
from typing import Optional
import pygame

from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT
from scenes.base_scene import BaseScene
from game.input_manager import InputManager


class SceneManager:
    """Manages scene stack, logical render targets, and aspect-correct window presentation."""

    def __init__(self) -> None:
        self.logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        if pygame.display.get_surface():
            try:
                self.logical_surface = self.logical_surface.convert()
            except Exception:
                pass
        self.scene_stack: list[BaseScene] = []
        self.input_manager = InputManager.get_instance()
        
        # Scaling properties
        self.scale: float = 1.0
        self.offset_x: int = 0
        self.offset_y: int = 0
        self.target_rect = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)

    @property
    def current_scene(self) -> Optional[BaseScene]:
        return self.scene_stack[-1] if self.scene_stack else None

    def change_scene(self, new_scene: BaseScene) -> None:
        """Exit all current scenes and switch to new scene."""
        while self.scene_stack:
            old = self.scene_stack.pop()
            old.on_exit()
        self.scene_stack.append(new_scene)
        new_scene.on_enter()

    def push_scene(self, new_scene: BaseScene) -> None:
        """Push scene on top of current scene (e.g. Pause or Settings overlay)."""
        if self.scene_stack:
            self.scene_stack[-1].is_active = False
        self.scene_stack.append(new_scene)
        new_scene.on_enter()

    def pop_scene(self) -> Optional[BaseScene]:
        """Pop top scene and resume previous scene."""
        if not self.scene_stack:
            return None
        popped = self.scene_stack.pop()
        popped.on_exit()
        if self.scene_stack:
            self.scene_stack[-1].is_active = True
        return popped

    def update_resolution(self, window_width: int, window_height: int) -> None:
        """Calculate letterbox/pillarbox aspect scaling for actual window dimensions."""
        scale_x = window_width / LOGICAL_WIDTH
        scale_y = window_height / LOGICAL_HEIGHT
        self.scale = min(scale_x, scale_y)
        
        rendered_w = int(LOGICAL_WIDTH * self.scale)
        rendered_h = int(LOGICAL_HEIGHT * self.scale)
        
        self.offset_x = (window_width - rendered_w) // 2
        self.offset_y = (window_height - rendered_h) // 2
        self.target_rect = pygame.Rect(self.offset_x, self.offset_y, rendered_w, rendered_h)
        
        # Keep input manager in sync
        self.input_manager.set_display_transform(self.scale, self.offset_x, self.offset_y)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Route event to active scene."""
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        """Update active scene."""
        if self.current_scene:
            self.current_scene.update(dt)

    def render(self, window_surface: pygame.Surface) -> None:
        """Render scene onto logical canvas, scale, and present on window surface."""
        # 1. Clear logical surface
        self.logical_surface.fill((10, 10, 15))
        
        # 2. Render active scene(s)
        if self.scene_stack:
            # If overlay, render scenes in stack that need background visibility
            for scene in self.scene_stack:
                scene.render(self.logical_surface)
                
        # 3. Present onto window surface with letterboxing
        window_surface.fill((0, 0, 0))
        if self.scale == 1.0 and self.offset_x == 0 and self.offset_y == 0:
            window_surface.blit(self.logical_surface, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(
                self.logical_surface, 
                (self.target_rect.width, self.target_rect.height)
            )
            window_surface.blit(scaled, self.target_rect)
