"""SHADOW CLASH - Typography and Text Rendering Utilities.

Provides consistent fonts, drop-shadow text rendering, and centered text layouts.
"""

from __future__ import annotations
import pygame
from game.asset_manager import AssetManager
from settings import COLOR_WHITE, COLOR_BLACK


class Typography:
    """Helper for styled text presentation."""

    @staticmethod
    def draw_text_with_shadow(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        x: int,
        y: int,
        shadow_color: tuple[int, int, int] = COLOR_BLACK,
        shadow_offset: tuple[int, int] = (2, 2),
        align: str = "left"
    ) -> pygame.Rect:
        """Render text with a dark drop shadow for high contrast readability."""
        txt_surf = font.render(text, True, color)
        shd_surf = font.render(text, True, shadow_color)
        
        rect = txt_surf.get_rect()
        if align == "center":
            rect.center = (x, y)
        elif align == "right":
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
            
        # Draw shadow first
        surface.blit(shd_surf, (rect.x + shadow_offset[0], rect.y + shadow_offset[1]))
        # Draw text
        surface.blit(txt_surf, rect)
        return rect
