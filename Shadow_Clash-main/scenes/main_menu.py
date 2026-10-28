"""SHADOW CLASH - Main Menu Scene.

Provides gateway to Story Mode, Continue, Training, Survival, Armory Shop,
Audio & Key Settings, and safe application termination.
"""

from __future__ import annotations
import sys
from typing import TYPE_CHECKING
import pygame

from settings import (
    COLOR_MOONLIGHT, COLOR_AMBER_GOLD, COLOR_CRIMSON_GLOW,
    COLOR_SILVER_MUTED, LOGICAL_WIDTH, LOGICAL_HEIGHT
)
from scenes.base_scene import BaseScene
from scenes.mode_select import ModeSelectScene
from scenes.combat_scene import CombatScene
from scenes.training_scene import TrainingScene
from scenes.survival_scene import SurvivalScene
from scenes.shop_scene import ShopScene
from scenes.settings_scene import SettingsScene
from ui.buttons import Button
from ui.typography import Typography
from systems.save_manager import SaveManager
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class MainMenuScene(BaseScene):
    """Primary navigation hub."""

    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        self.save_mgr = SaveManager()
        
        self.has_save: bool = self.save_mgr.has_save_file()
        self.buttons: list[Button] = []
        self._init_buttons()

    def _init_buttons(self) -> None:
        bx = 120
        start_y = 260
        btn_w, btn_h = 280, 50
        spacing = 62
        
        # 1. Play / Story Mode
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y, btn_w, btn_h),
            text="STORY MODE",
            callback=self._on_play
        ))
        
        # 2. Continue (Resumes highest unlocked stage)
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y + spacing, btn_w, btn_h),
            text="CONTINUE",
            callback=self._on_continue,
            enabled=self.has_save
        ))
        
        # 3. Training Mode
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y + spacing * 2, btn_w, btn_h),
            text="TRAINING DOJO",
            callback=self._on_training
        ))
        
        # 4. Survival Mode
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y + spacing * 3, btn_w, btn_h),
            text="SURVIVAL",
            callback=self._on_survival
        ))
        
        # 5. Armory / Shop
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y + spacing * 4, btn_w, btn_h),
            text="ARMORY & UPGRADES",
            callback=self._on_shop
        ))
        
        # 6. Settings
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y + spacing * 5, btn_w, btn_h),
            text="SETTINGS",
            callback=self._on_settings
        ))
        
        # 7. Exit Game
        self.buttons.append(Button(
            rect=pygame.Rect(bx, start_y + spacing * 6, btn_w, btn_h),
            text="EXIT TO DESKTOP",
            callback=self._on_exit
        ))

    def on_enter(self) -> None:
        self.audio_mgr.play_bgm("bgm_menu", loop=True)

    def _on_play(self) -> None:
        self.scene_manager.change_scene(ModeSelectScene(self.scene_manager))

    def _on_continue(self) -> None:
        save_data = self.save_mgr.load()
        highest_stage = save_data.get("max_unlocked_stage", 1)
        self.scene_manager.change_scene(CombatScene(self.scene_manager, stage_id=highest_stage))

    def _on_training(self) -> None:
        self.scene_manager.change_scene(TrainingScene(self.scene_manager))

    def _on_survival(self) -> None:
        self.scene_manager.change_scene(SurvivalScene(self.scene_manager))

    def _on_shop(self) -> None:
        self.scene_manager.change_scene(ShopScene(self.scene_manager))

    def _on_settings(self) -> None:
        self.scene_manager.change_scene(SettingsScene(self.scene_manager))

    def _on_exit(self) -> None:
        pygame.quit()
        sys.exit(0)

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse_pos = self.input_mgr.get_mouse_logical_pos()
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        # 1. Background
        bg = self.asset_mgr.get_ui_image("menu_background")
        surface.blit(bg, (0, 0))

        # 2. Game Logo
        logo = self.asset_mgr.get_ui_image("logo")
        surface.blit(logo, (80, 50))
        
        # Logo Stylized Title
        title_font = self.asset_mgr.get_font(48, bold=True)
        sub_font = self.asset_mgr.get_font(18, bold=True)
        Typography.draw_text_with_shadow(
            surface, "SHADOW CLASH", title_font, COLOR_MOONLIGHT, 170, 75
        )
        Typography.draw_text_with_shadow(
            surface, "MARTIAL ARTS SILHOUETTES", sub_font, COLOR_CRIMSON_GLOW, 175, 130
        )

        # 3. Menu Buttons
        for btn in self.buttons:
            btn.render(surface)

        # 4. Version & Copyright Footer
        footer_font = self.asset_mgr.get_font(14)
        Typography.draw_text_with_shadow(
            surface, "SHADOW CLASH v1.0.0 | PYTHON & PYGAME-CE", footer_font, COLOR_SILVER_MUTED, 1200, 690, align="right"
        )
