"""SHADOW CLASH - Combat Health Bar UI Component.

Features smooth trailing delayed damage bars, mirrored orientation for opponents,
and metallic border framing.
"""

from __future__ import annotations
import pygame
from settings import (
    COLOR_HEALTH_GREEN, COLOR_HEALTH_DELAY, COLOR_CRIMSON,
    COLOR_MOONLIGHT, COLOR_BLACK
)


class HealthBar:
    """Fighting game health bar with delayed damage reaction."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 440,
        height: int = 24,
        is_opponent: bool = False
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_opponent = is_opponent

    def render(self, surface: pygame.Surface, current_hp: float, delayed_hp: float, max_hp: float) -> None:
        """Render health bar layers (Background -> Delayed Red -> Active Green -> Frame)."""
        max_h = max(1.0, max_hp)
        curr_ratio = max(0.0, min(1.0, current_hp / max_h))
        delay_ratio = max(0.0, min(1.0, delayed_hp / max_h))

        # 1. Dark Background Slot
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (18, 20, 28), bg_rect)

        # 2. Delayed Damage Bar (Red / Amber)
        delay_w = int(self.width * delay_ratio)
        if self.is_opponent:
            delay_rect = pygame.Rect(self.x + (self.width - delay_w), self.y, delay_w, self.height)
        else:
            delay_rect = pygame.Rect(self.x, self.y, delay_w, self.height)
        pygame.draw.rect(surface, COLOR_HEALTH_DELAY, delay_rect)

        # 3. Active Health Bar (Vibrant Martial Green or Crimson for Boss)
        active_w = int(self.width * curr_ratio)
        health_color = COLOR_HEALTH_GREEN if not self.is_opponent else (215, 45, 60)
        if self.is_opponent:
            active_rect = pygame.Rect(self.x + (self.width - active_w), self.y, active_w, self.height)
        else:
            active_rect = pygame.Rect(self.x, self.y, active_w, self.height)
        pygame.draw.rect(surface, health_color, active_rect)

        # 4. Angled Metallic Frame & Border
        pygame.draw.rect(surface, (70, 85, 115), bg_rect, 2)
        # Accent notches
        for notch in range(self.x + 80, self.x + self.width, 90):
            pygame.draw.line(surface, (30, 36, 50), (notch, self.y), (notch, self.y + self.height), 1)
