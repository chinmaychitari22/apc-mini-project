"""SHADOW CLASH - In-Game Toast Notification System.

Animates sliding banners for achievements, unlocks, and milestones.
"""

from __future__ import annotations
from typing import Optional
import pygame

from settings import COLOR_AMBER_GOLD, COLOR_MOONLIGHT, COLOR_BLACK
from game.asset_manager import AssetManager
from ui.typography import Typography


class NotificationToast:
    """Sliding notification banner."""

    def __init__(self) -> None:
        self.queue: list[dict] = []
        self.current_item: Optional[dict] = None
        self.display_timer: float = 0.0
        self.slide_progress: float = 0.0
        
        self.asset_mgr = AssetManager.get_instance()
        self.title_font = self.asset_mgr.get_font(20, bold=True)
        self.desc_font = self.asset_mgr.get_font(16)

    def enqueue(self, title: str, description: str, reward: int = 0) -> None:
        self.queue.append({
            "title": title,
            "description": description,
            "reward": reward
        })

    def update(self, dt: float) -> None:
        if self.current_item is None:
            if self.queue:
                self.current_item = self.queue.pop(0)
                self.display_timer = 3.2
                self.slide_progress = 0.0
        else:
            self.display_timer -= dt
            if self.display_timer > 2.8:
                # Sliding down
                self.slide_progress = min(1.0, self.slide_progress + dt * 4.0)
            elif self.display_timer < 0.4:
                # Sliding up
                self.slide_progress = max(0.0, self.slide_progress - dt * 3.0)
                
            if self.display_timer <= 0.0:
                self.current_item = None
                self.slide_progress = 0.0

    def render(self, surface: pygame.Surface) -> None:
        if not self.current_item or self.slide_progress <= 0.001:
            return
            
        banner_w, banner_h = 480, 64
        # Calculate vertical position based on slide progress
        target_y = 20
        start_y = -banner_h - 10
        curr_y = int(start_y + (target_y - start_y) * self.slide_progress)
        curr_x = (1280 - banner_w) // 2
        
        # Plaque background
        banner_surf = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        banner_surf.fill((16, 20, 30, 245))
        pygame.draw.rect(banner_surf, COLOR_AMBER_GOLD, (0, 0, banner_w, banner_h), 2)
        surface.blit(banner_surf, (curr_x, curr_y))
        
        # Trophy / Coin icon
        coin_icon = self.asset_mgr.get_icon("coin")
        scaled_icon = pygame.transform.smoothscale(coin_icon, (40, 40))
        surface.blit(scaled_icon, (curr_x + 14, curr_y + 12))
        
        # Text
        Typography.draw_text_with_shadow(
            surface=surface,
            text=f"ACHIEVEMENT: {self.current_item['title']}",
            font=self.title_font,
            color=COLOR_AMBER_GOLD,
            x=curr_x + 64,
            y=curr_y + 12
        )
        Typography.draw_text_with_shadow(
            surface=surface,
            text=self.current_item['description'],
            font=self.desc_font,
            color=COLOR_MOONLIGHT,
            x=curr_x + 64,
            y=curr_y + 36
        )
