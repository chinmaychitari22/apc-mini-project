"""SHADOW CLASH - Story Stage and Mission Select Scene.

Displays narrative encounters, locked/unlocked stages, enemy previews,
and arena profiles.
"""

from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional
import pygame

from settings import (
    DATA_DIR, COLOR_MOONLIGHT, COLOR_AMBER_GOLD,
    COLOR_CRIMSON, COLOR_SILVER_MUTED, LOGICAL_WIDTH, LOGICAL_HEIGHT
)
from scenes.base_scene import BaseScene
from scenes.combat_scene import CombatScene
from ui.buttons import Button
from ui.typography import Typography
from systems.save_manager import SaveManager
from systems.progression import ProgressionSystem
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class ModeSelectScene(BaseScene):
    """Stage selection map for Story Mode."""

    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        
        self.save_mgr = SaveManager()
        self.progression = ProgressionSystem(self.save_mgr)
        self.stages = self._load_all_stages()
        
        self.selected_stage_idx: int = 0
        self.stage_buttons: list[Button] = []
        self.fight_button: Optional[Button] = None
        self.back_button = Button(pygame.Rect(80, 630, 200, 48), "MAIN MENU", self._on_back)

        self._init_stage_buttons()
        self._update_fight_button()

    def _load_all_stages(self) -> list[dict]:
        stages_path = DATA_DIR / "stages.json"
        if stages_path.is_file():
            try:
                with open(stages_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ModeSelectScene] Error loading stages: {e}")
        return []

    def _init_stage_buttons(self) -> None:
        self.stage_buttons.clear()
        max_unlocked = self.progression.max_unlocked_stage
        
        start_y = 150
        for i, stg in enumerate(self.stages):
            idx = i
            s_id = stg.get("stage_id", i + 1)
            is_unlocked = (s_id <= max_unlocked)
            label = stg.get("title", f"Stage {s_id}") if is_unlocked else f"Stage {s_id} (LOCKED)"
            btn = Button(
                rect=pygame.Rect(80, start_y + i * 85, 460, 68),
                text=label,
                callback=lambda i=idx: self._select_stage(i),
                font_size=18,
                enabled=is_unlocked
            )
            self.stage_buttons.append(btn)

    def _select_stage(self, idx: int) -> None:
        self.selected_stage_idx = idx
        self._update_fight_button()

    def _update_fight_button(self) -> None:
        """Update the fight button based on selected stage."""
        px, py = 580, 150  # Panel position from render()
        stg = self.stages[self.selected_stage_idx]
        s_id = stg.get("stage_id", 1)
        is_unlocked = (s_id <= self.progression.max_unlocked_stage)

        self.fight_button = Button(
            rect=pygame.Rect(px + 30, py + 370, 260, 52),
            text="FIGHT",
            callback=self._start_fight,
            enabled=is_unlocked
        )

    def _on_back(self) -> None:
        from scenes.main_menu import MainMenuScene
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def _start_fight(self) -> None:
        stg = self.stages[self.selected_stage_idx]
        s_id = stg.get("stage_id", 1)
        self.scene_manager.change_scene(CombatScene(self.scene_manager, stage_id=s_id))

    def on_enter(self) -> None:
        self.audio_mgr.play_bgm("bgm_menu", loop=True)

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse_pos = self.input_mgr.get_mouse_logical_pos()
        for sb in self.stage_buttons:
            sb.handle_event(event, mouse_pos)
        self.back_button.handle_event(event, mouse_pos)
        if self.fight_button:
            self.fight_button.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        bg = self.asset_mgr.get_ui_image("menu_background")
        surface.blit(bg, (0, 0))
        
        veil = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        veil.fill((10, 12, 18, 235))
        surface.blit(veil, (0, 0))

        Typography.draw_text_with_shadow(
            surface, "STORY MODE: SHADOW ASCENT", self.asset_mgr.get_font(38, bold=True), COLOR_MOONLIGHT, 80, 50
        )

        for sb in self.stage_buttons:
            sb.render(surface)
        self.back_button.render(surface)

        # Stage Details Panel
        panel = pygame.Rect(580, 150, 620, 460)
        p_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        p_surf.fill((16, 20, 30, 240))
        pygame.draw.rect(p_surf, (70, 85, 115), (0, 0, panel.width, panel.height), 2)
        surface.blit(p_surf, panel.topleft)

        px, py = panel.x, panel.y
        stg = self.stages[self.selected_stage_idx]
        s_id = stg.get("stage_id", 1)
        is_unlocked = (s_id <= self.progression.max_unlocked_stage)

        f_title = self.asset_mgr.get_font(26, bold=True)
        f_sub = self.asset_mgr.get_font(18)
        f_desc = self.asset_mgr.get_font(18)

        # Enemy portrait
        arch_key = stg.get("enemy_key", "rogue")
        port = self.asset_mgr.get_ui_image(f"portrait_{arch_key}")
        surface.blit(pygame.transform.smoothscale(port, (100, 100)), (px + 30, py + 30))

        Typography.draw_text_with_shadow(surface, stg.get("title", ""), f_title, COLOR_AMBER_GOLD, px + 150, py + 35)
        Typography.draw_text_with_shadow(surface, f"ARENA: {stg.get('arena', '').replace('_', ' ').title()}", f_sub, COLOR_SILVER_MUTED, px + 150, py + 75)
        Typography.draw_text_with_shadow(surface, f"REWARD: +{stg.get('reward_coins', 100)} COINS", f_sub, (120, 230, 160), px + 150, py + 105)

        Typography.draw_text_with_shadow(surface, stg.get("description", ""), f_desc, COLOR_MOONLIGHT, px + 30, py + 170)

        # Fight Button
        if self.fight_button:
            self.fight_button.render(surface)
