"""SHADOW CLASH - Combat HUD Interface and Dynamic Display Elements.

Renders player & opponent health, energy gauge, battle timer, fighter portraits,
dynamic combo banners, and boss phase counters.
"""

from __future__ import annotations
import math
import pygame

from settings import (
    COLOR_MOONLIGHT, COLOR_AMBER_GOLD, COLOR_CRIMSON_GLOW,
    COLOR_CYAN_ENERGY, COLOR_SILVER_MUTED, LOGICAL_WIDTH
)
from entities.fighter import Fighter
from entities.enemy import EnemyFighter
from combat.combo_system import ComboTracker
from ui.health_bar import HealthBar
from ui.energy_bar import EnergyBar
from ui.typography import Typography
from game.asset_manager import AssetManager


class CombatHUD:
    """Complete in-fight graphical heads-up display."""

    def __init__(self) -> None:
        self.asset_mgr = AssetManager.get_instance()
        
        # Health & Energy components
        self.player_health_bar = HealthBar(x=80, y=42, width=440, height=22, is_opponent=False)
        self.enemy_health_bar = HealthBar(x=760, y=42, width=440, height=22, is_opponent=True)
        self.player_energy_bar = EnergyBar(x=80, y=70, width=340, height=12)
        
        # Fonts
        self.name_font = self.asset_mgr.get_font(20, bold=True)
        self.timer_font = self.asset_mgr.get_font(36, bold=True)
        self.combo_font_large = self.asset_mgr.get_font(42, bold=True)
        self.combo_font_small = self.asset_mgr.get_font(18, bold=True)

    def render(
        self,
        surface: pygame.Surface,
        player: Fighter,
        enemy: Fighter,
        fight_time_remaining: float,
        player_combo: ComboTracker,
        stage_title: str = "BATTLE"
    ) -> None:
        """Render complete HUD frame."""
        # 1. Fighter Names
        Typography.draw_text_with_shadow(
            surface, player.name.upper(), self.name_font, COLOR_MOONLIGHT, 80, 16
        )
        Typography.draw_text_with_shadow(
            surface, enemy.name.upper(), self.name_font, (245, 80, 95), 1200, 16, align="right"
        )
        
        # If enemy is boss, draw boss phase indicators
        if isinstance(enemy, EnemyFighter) and enemy.is_boss:
            phase_text = f"PHASE {enemy.current_phase}/3"
            Typography.draw_text_with_shadow(
                surface, phase_text, self.name_font, COLOR_AMBER_GOLD, 1200, 70, align="right"
            )

        # 2. Health Bars
        self.player_health_bar.render(surface, player.current_health, player.health_delay, player.max_health)
        self.enemy_health_bar.render(surface, enemy.current_health, enemy.health_delay, enemy.max_health)

        # 3. Player Energy Bar
        self.player_energy_bar.render(surface, player.current_energy, player.max_energy)
        
        # Energy label
        Typography.draw_text_with_shadow(
            surface, "SHADOW METER", self.asset_mgr.get_font(14, bold=True), COLOR_CYAN_ENERGY, 80, 86
        )

        # 4. Central Fight Timer
        timer_int = max(0, int(fight_time_remaining))
        timer_col = (255, 75, 75) if timer_int <= 10 else COLOR_MOONLIGHT
        Typography.draw_text_with_shadow(
            surface, f"{timer_int:02d}", self.timer_font, timer_col, 640, 38, align="center"
        )
        
        # Stage Title (Top center)
        Typography.draw_text_with_shadow(
            surface, stage_title, self.asset_mgr.get_font(16), COLOR_SILVER_MUTED, 640, 14, align="center"
        )

        # 5. Dynamic Combo Banner (Left side for Player combos)
        if player_combo.combo_count >= 2:
            scale_pulse = 1.0 + 0.1 * math.sin(player_combo.timer * 12.0)
            cx, cy = 130, 220
            Typography.draw_text_with_shadow(
                surface, f"{player_combo.combo_count}", self.combo_font_large, COLOR_AMBER_GOLD, cx, cy
            )
            Typography.draw_text_with_shadow(
                surface, "HITS COMBO!", self.combo_font_small, COLOR_CRIMSON_GLOW, cx + 55, cy + 8
            )
            Typography.draw_text_with_shadow(
                surface, f"{int(player_combo.combo_damage)} DMG", self.combo_font_small, COLOR_MOONLIGHT, cx + 55, cy + 28
            )
