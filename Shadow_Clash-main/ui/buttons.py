"""SHADOW CLASH - Interactive Martial UI Button.

Handles hover animations, audio cues, disabled states, and click callbacks.
"""

from __future__ import annotations
from typing import Callable, Optional
import pygame

from settings import (
    COLOR_MOONLIGHT, COLOR_CRIMSON, COLOR_CRIMSON_GLOW,
    COLOR_SILVER_MUTED, COLOR_BLACK
)
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from ui.typography import Typography


class Button:
    """Stylized martial arts interface button."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable[[], None]] = None,
        font_size: int = 24,
        enabled: bool = True
    ) -> None:
        self.rect = rect
        self.text = text
        self.callback = callback
        self.enabled = enabled
        
        self.is_hovered: bool = False
        self.is_pressed: bool = False
        self._prev_hovered: bool = False
        
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.font = self.asset_mgr.get_font(font_size, bold=True)

    def handle_event(self, event: pygame.event.Event, logical_mouse_pos: tuple[int, int]) -> bool:
        """Process mouse interactions in logical space. Returns True if clicked."""
        if not self.enabled:
            self.is_hovered = False
            self.is_pressed = False
            return False

        self.is_hovered = self.rect.collidepoint(logical_mouse_pos)
        
        # Audio cue on cursor enter
        if self.is_hovered and not self._prev_hovered:
            self.audio_mgr.play_sfx("menu_hover")
        self._prev_hovered = self.is_hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered:
                self.is_pressed = False
                self.audio_mgr.play_sfx("menu_click")
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
            
        return False

    def render(self, surface: pygame.Surface) -> None:
        """Render button with themed angled borders and glowing accents."""
        # Determine styling state
        if not self.enabled:
            bg_col = (18, 20, 26, 180)
            border_col = (50, 55, 65)
            text_col = (90, 95, 110)
        elif self.is_pressed:
            bg_col = (38, 16, 24, 245)
            border_col = COLOR_CRIMSON_GLOW
            text_col = COLOR_MOONLIGHT
        elif self.is_hovered:
            bg_col = (28, 22, 34, 240)
            border_col = COLOR_CRIMSON
            text_col = (255, 235, 240)
        else:
            bg_col = (16, 18, 26, 220)
            border_col = (70, 85, 110)
            text_col = COLOR_SILVER_MUTED

        # Draw angled martial polygon button
        x, y, w, h = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        cut = 10
        pts = [
            (x + cut, y), (x + w, y),
            (x + w - cut, y + h), (x, y + h)
        ]
        
        # Fill
        btn_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        rel_pts = [(px - x, py - y) for px, py in pts]
        pygame.draw.polygon(btn_surf, bg_col, rel_pts)
        pygame.draw.polygon(btn_surf, border_col, rel_pts, 2)
        
        # Crimson corner tick when hovered
        if self.is_hovered and self.enabled:
            pygame.draw.line(btn_surf, COLOR_CRIMSON_GLOW, (0, h - 8), (8, h), 3)
            pygame.draw.line(btn_surf, COLOR_CRIMSON_GLOW, (w - 8, 0), (w, 8), 3)
            
        surface.blit(btn_surf, (x, y))

        # Centered Text
        text_y = y + h // 2 + (1 if self.is_pressed else 0)
        Typography.draw_text_with_shadow(
            surface=surface,
            text=self.text,
            font=self.font,
            color=text_col,
            x=x + w // 2,
            y=text_y,
            align="center"
        )
