"""SHADOW CLASH - Post-Battle Results Scene.

Displays encounter outcome (VICTORY or DEFEAT), awards stage currency and exp
(ensuring one-time distribution), evaluates achievements, and offers progression options.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import pygame

from settings import (
    COLOR_AMBER_GOLD, COLOR_CRIMSON_GLOW, COLOR_MOONLIGHT,
    COLOR_SILVER_MUTED, LOGICAL_WIDTH, LOGICAL_HEIGHT
)
from scenes.base_scene import BaseScene
from ui.buttons import Button
from ui.typography import Typography
from ui.notifications import NotificationToast
from systems.save_manager import SaveManager
from systems.progression import ProgressionSystem
from systems.achievements import AchievementManager
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class ResultsScene(BaseScene):
    """End-of-match resolution screen."""

    def __init__(
        self,
        scene_manager: SceneManager,
        is_victory: bool,
        stage_id: int,
        reward_coins: int,
        reward_exp: int,
        highest_combo: int,
        flawless: bool,
        is_survival: bool = False,
        survival_wave: int = 0
    ) -> None:
        super().__init__(scene_manager)
        self.is_victory = is_victory
        self.stage_id = stage_id
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.highest_combo = highest_combo
        self.flawless = flawless
        self.is_survival = is_survival
        self.survival_wave = survival_wave
        
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        
        self.save_mgr = SaveManager()
        self.progression = ProgressionSystem(self.save_mgr)
        self.achievement_mgr = AchievementManager(self.save_mgr)
        self.toast = NotificationToast()
        
        # State tracking to ensure one-time reward awarding
        self.rewards_awarded: bool = False
        
        # Setup UI Buttons
        self.buttons: list[Button] = []
        self._init_buttons()

    def _init_buttons(self) -> None:
        cx = 640
        btn_w, btn_h = 240, 50
        
        if self.is_survival:
            self.buttons.append(Button(
                rect=pygame.Rect(cx - 260, 560, btn_w, btn_h),
                text="TRY AGAIN",
                callback=self._on_retry
            ))
            self.buttons.append(Button(
                rect=pygame.Rect(cx + 20, 560, btn_w, btn_h),
                text="MAIN MENU",
                callback=self._on_main_menu
            ))
        elif self.is_victory:
            # If not final stage, allow Continue to next stage
            if self.stage_id < 5:
                self.buttons.append(Button(
                    rect=pygame.Rect(cx - 380, 560, btn_w, btn_h),
                    text="NEXT STAGE",
                    callback=self._on_next_stage
                ))
            self.buttons.append(Button(
                rect=pygame.Rect(cx - 120, 560, btn_w, btn_h),
                text="REPLAY",
                callback=self._on_retry
            ))
            self.buttons.append(Button(
                rect=pygame.Rect(cx + 140, 560, btn_w, btn_h),
                text="MAIN MENU",
                callback=self._on_main_menu
            ))
        else:
            self.buttons.append(Button(
                rect=pygame.Rect(cx - 260, 560, btn_w, btn_h),
                text="RETRY",
                callback=self._on_retry
            ))
            self.buttons.append(Button(
                rect=pygame.Rect(cx + 20, 560, btn_w, btn_h),
                text="MAIN MENU",
                callback=self._on_main_menu
            ))

    def on_enter(self) -> None:
        """Distribute rewards, check achievements, and play audio sting."""
        if not self.rewards_awarded:
            self.rewards_awarded = True
            
            if self.is_victory and not self.is_survival:
                self.audio_mgr.play_sfx("victory")
                # Credit coins & exp
                self.progression.coins += self.reward_coins
                cur_exp = self.save_mgr.data.get("experience", 0)
                self.save_mgr.data["experience"] = cur_exp + self.reward_exp
                
                # Unlock next stage
                self.progression.unlock_next_stage(self.stage_id)
                
                # Statistics
                stats = self.save_mgr.data["statistics"]
                stats["battles_won"] = stats.get("battles_won", 0) + 1
                if self.flawless:
                    stats["flawless_victories"] = stats.get("flawless_victories", 0) + 1
                    
                # Achievements
                new_achs = self.achievement_mgr.check_combat_milestones(
                    victory=True,
                    highest_combo=self.highest_combo,
                    flawless=self.flawless,
                    is_boss_defeat=(self.stage_id == 5)
                )
                for ach in new_achs:
                    self.toast.enqueue(ach["title"], ach["description"])
            else:
                self.audio_mgr.play_sfx("defeat")
                stats = self.save_mgr.data["statistics"]
                stats["battles_lost"] = stats.get("battles_lost", 0) + 1
                
            if self.is_survival:
                best_wave = self.save_mgr.data["statistics"].get("survival_best_wave", 0)
                if self.survival_wave > best_wave:
                    self.save_mgr.data["statistics"]["survival_best_wave"] = self.survival_wave
                new_achs = self.achievement_mgr.check_survival_milestone(self.survival_wave)
                for ach in new_achs:
                    self.toast.enqueue(ach["title"], ach["description"])

            self.save_mgr.save()

    def _on_next_stage(self) -> None:
        from scenes.combat_scene import CombatScene
        self.scene_manager.change_scene(CombatScene(self.scene_manager, stage_id=self.stage_id + 1))

    def _on_retry(self) -> None:
        if self.is_survival:
            from scenes.survival_scene import SurvivalScene
            self.scene_manager.change_scene(SurvivalScene(self.scene_manager))
        else:
            from scenes.combat_scene import CombatScene
            self.scene_manager.change_scene(CombatScene(self.scene_manager, stage_id=self.stage_id))

    def _on_main_menu(self) -> None:
        from scenes.main_menu import MainMenuScene
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse_pos = self.input_mgr.get_mouse_logical_pos()
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        self.toast.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        # Darkened atmospheric backdrop
        bg = self.asset_mgr.get_ui_image("menu_background")
        surface.blit(bg, (0, 0))
        
        # Dimming veil
        veil = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        veil.fill((8, 10, 16, 215))
        surface.blit(veil, (0, 0))

        # Title Banner
        cx = 640
        title_font = self.asset_mgr.get_font(60, bold=True)
        sub_font = self.asset_mgr.get_font(26, bold=True)
        stat_font = self.asset_mgr.get_font(22)

        if self.is_victory:
            Typography.draw_text_with_shadow(
                surface, "VICTORY", title_font, COLOR_AMBER_GOLD, cx, 140, align="center"
            )
            Typography.draw_text_with_shadow(
                surface, "THE SHADOW HAS PREVAILED", sub_font, COLOR_MOONLIGHT, cx, 210, align="center"
            )
        else:
            Typography.draw_text_with_shadow(
                surface, "DEFEAT", title_font, COLOR_CRIMSON_GLOW, cx, 140, align="center"
            )
            Typography.draw_text_with_shadow(
                surface, "FALLEN IN BATTLE", sub_font, COLOR_SILVER_MUTED, cx, 210, align="center"
            )

        # Statistics Plaque
        plaque_w, plaque_h = 560, 240
        px, py = cx - plaque_w // 2, 270
        p_surf = pygame.Surface((plaque_w, plaque_h), pygame.SRCALPHA)
        p_surf.fill((16, 18, 26, 230))
        pygame.draw.rect(p_surf, (60, 75, 100), (0, 0, plaque_w, plaque_h), 2)
        surface.blit(p_surf, (px, py))

        # Render Stats Rows
        if self.is_survival:
            Typography.draw_text_with_shadow(
                surface, f"SURVIVAL WAVES CLEARED: {self.survival_wave}", stat_font, COLOR_AMBER_GOLD, cx, py + 45, align="center"
            )
            Typography.draw_text_with_shadow(
                surface, f"MAX COMBO CHAIN: {self.highest_combo} HITS", stat_font, COLOR_MOONLIGHT, cx, py + 95, align="center"
            )
        else:
            reward_str = f"+{self.reward_coins} COINS" if self.is_victory else "+0 COINS"
            Typography.draw_text_with_shadow(
                surface, f"REWARD: {reward_str}", stat_font, COLOR_AMBER_GOLD, cx, py + 40, align="center"
            )
            Typography.draw_text_with_shadow(
                surface, f"MAX COMBO: {self.highest_combo} HITS", stat_font, COLOR_MOONLIGHT, cx, py + 85, align="center"
            )
            if self.flawless and self.is_victory:
                Typography.draw_text_with_shadow(
                    surface, "FLAWLESS VICTORY BONUS ACHIEVED!", stat_font, (120, 230, 160), cx, py + 130, align="center"
                )

        # Buttons
        for btn in self.buttons:
            btn.render(surface)

        # Toasts
        self.toast.render(surface)
