"""SHADOW CLASH - Special Meter / Ki Energy Bar UI.

Renders glowing energy accumulation, special attack threshold marker (60%),
and radiant pulse animation when full.
"""

from __future__ import annotations
import math
import time
import pygame
from settings import (
    COLOR_CYAN_ENERGY, COLOR_VIOLET_GLOW, COLOR_BLACK,
    SPECIAL_COST, MAX_ENERGY
)


class EnergyBar:
    """Special attack energy meter."""

    def __init__(self, x: int, y: int, width: int = 340, height: int = 14) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self, surface: pygame.Surface, current_energy: float, max_energy: float = MAX_ENERGY) -> None:
        """Render energy bar with threshold indicators."""
        ratio = max(0.0, min(1.0, current_energy / max_energy))
        
        # 1. Background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (14, 16, 24), bg_rect)
        
        # 2. Energy Fill
        fill_w = int(self.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_w, self.height)
            # Pulse color if ready for special attack
            is_ready = current_energy >= SPECIAL_COST
            if is_ready:
                pulse = 0.5 + 0.5 * math.sin(time.time() * 8.0)
                col = (
                    int(COLOR_CYAN_ENERGY[0] * (1.0 - pulse) + COLOR_VIOLET_GLOW[0] * pulse),
                    int(COLOR_CYAN_ENERGY[1] * (1.0 - pulse) + COLOR_VIOLET_GLOW[1] * pulse),
                    int(COLOR_CYAN_ENERGY[2] * (1.0 - pulse) + COLOR_VIOLET_GLOW[2] * pulse)
                )
            else:
                col = COLOR_CYAN_ENERGY
            pygame.draw.rect(surface, col, fill_rect)

        # 3. Special Move Required Threshold Marker (at 60%)
        thresh_x = self.x + int(self.width * (SPECIAL_COST / max_energy))
        pygame.draw.line(surface, (255, 235, 120), (thresh_x, self.y - 2), (thresh_x, self.y + self.height + 2), 2)

        # 4. Border
        pygame.draw.rect(surface, (50, 70, 95), bg_rect, 1)
