"""SHADOW CLASH - Training and Dojo Practice Scene.

Provides an interactive sandbox to test combos, practice blocking, observe
damage outputs, and toggle dummy behaviors without altering story progress.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from settings import GROUND_Y, COLOR_MOONLIGHT, COLOR_AMBER_GOLD, COLOR_CRIMSON_GLOW
from scenes.base_scene import BaseScene
from entities.player import PlayerFighter
from entities.enemy import EnemyFighter
from combat.combat_system import CombatSystem
from ui.components import CombatHUD
from ui.buttons import Button
from ui.typography import Typography
from systems.save_manager import SaveManager
from systems.progression import ProgressionSystem
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class TrainingScene(BaseScene):
    """Practice dojo mode."""

    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        
        self.save_mgr = SaveManager()
        self.progression = ProgressionSystem(self.save_mgr)
        
        self.player = PlayerFighter(x=380.0, y=GROUND_Y)
        self.progression.apply_to_player(self.player)
        
        self.dummy = EnemyFighter(archetype_key="rogue", x=880.0, y=GROUND_Y)
        self.dummy.name = "Practice Dummy"
        
        self.combat_system = CombatSystem()
        self.hud = CombatHUD()
        
        # Training dummy modes: "STAND", "GUARD", "ATTACK"
        self.dummy_modes = ["STAND", "GUARD", "ATTACK"]
        self.mode_index = 0
        self.dummy_attack_timer = 0.0
        
        # Buttons
        self.buttons: list[Button] = []
        self._init_buttons()

    def _init_buttons(self) -> None:
        self.buttons = [
            Button(pygame.Rect(80, 115, 140, 36), "RESET", self._reset_dummy, font_size=18),
            Button(pygame.Rect(230, 115, 180, 36), f"MODE: {self.dummy_modes[self.mode_index]}", self._toggle_dummy_mode, font_size=18),
            Button(pygame.Rect(1060, 115, 140, 36), "MAIN MENU", self._quit_to_menu, font_size=18)
        ]

    def _reset_dummy(self) -> None:
        """Reset fighter positions, fill health, reset combos."""
        self.player.x = 380.0
        self.player.y = GROUND_Y
        self.player.current_health = self.player.max_health
        self.player.health_delay = self.player.max_health
        self.player.current_energy = self.player.max_energy  # Full energy for testing specials
        
        self.dummy.x = 880.0
        self.dummy.y = GROUND_Y
        self.dummy.current_health = self.dummy.max_health
        self.dummy.health_delay = self.dummy.max_health
        self.dummy.set_state(self.dummy.state.IDLE)
        
        self.combat_system.reset()

    def _toggle_dummy_mode(self) -> None:
        self.mode_index = (self.mode_index + 1) % len(self.dummy_modes)
        mode = self.dummy_modes[self.mode_index]
        self.buttons[1].text = f"MODE: {mode}"
        if mode == "GUARD":
            self.dummy.start_block()
        else:
            self.dummy.stop_block()

    def _quit_to_menu(self) -> None:
        from scenes.main_menu import MainMenuScene
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def on_enter(self) -> None:
        self.audio_mgr.play_bgm("bgm_menu", loop=True)

    def on_exit(self) -> None:
        self.audio_mgr.stop_bgm()

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse_pos = self.input_mgr.get_mouse_logical_pos()
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        self.player.handle_input()
        
        # Execute Dummy Mode logic
        mode = self.dummy_modes[self.mode_index]
        if mode == "GUARD":
            self.dummy.start_block()
        elif mode == "ATTACK":
            self.dummy_attack_timer += dt
            if self.dummy_attack_timer >= 1.6:
                self.dummy_attack_timer = 0.0
                from combat.attack import AttackRegistry
                atk = AttackRegistry.get("light_punch")
                if atk:
                    self.dummy.start_attack(atk)
                    
        # Regenerate dummy health continuously so it never dies
        if self.dummy.current_health < self.dummy.max_health * 0.3:
            self.dummy.current_health = self.dummy.max_health
            self.dummy.health_delay = self.dummy.max_health

        self.player.update(dt, opponent=self.dummy)
        self.dummy.update(dt, opponent=self.player)
        self.combat_system.update(dt, self.player, self.dummy)

    def render(self, surface: pygame.Surface) -> None:
        bg = self.asset_mgr.get_arena("abandoned_dojo")
        surface.blit(bg, (0, 0))

        self.dummy.render(surface)
        self.player.render(surface)
        self.combat_system.particle_sys.render(surface, self.hud.combo_font_small)

        # HUD
        self.hud.render(
            surface=surface,
            player=self.player,
            enemy=self.dummy,
            fight_time_remaining=99.0,
            player_combo=self.combat_system.player_combo,
            stage_title="DOJO TRAINING MODE"
        )

        for btn in self.buttons:
            btn.render(surface)

        # Controls reference hint
        hint_font = self.asset_mgr.get_font(16)
        Typography.draw_text_with_shadow(
            surface,
            "CONTROLS: A/D - Move  |  W - Jump  |  S - Crouch  |  J - Light Punch  |  U - Heavy Punch  |  K - Light Kick  |  I - Heavy Kick  |  L - Block  |  O - Shadow Burst",
            hint_font,
            COLOR_MOONLIGHT,
            640,
            695,
            align="center"
        )
