"""SHADOW CLASH - Abstract Base Scene.

All game scenes (Menu, Combat, Shop, Settings, Survival, Training, Results)
inherit from BaseScene.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class BaseScene(ABC):
    """Abstract interface defining scene lifecycle, update, and rendering."""

    def __init__(self, scene_manager: SceneManager) -> None:
        self.scene_manager = scene_manager
        self.is_active: bool = True

    def on_enter(self) -> None:
        """Called immediately when scene becomes active."""
        pass

    def on_exit(self) -> None:
        """Called immediately before scene is transitioned out."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle individual raw events if needed."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance scene logic by elapsed time delta dt (in seconds)."""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render scene elements onto the 1280x720 logical canvas surface."""
        pass
