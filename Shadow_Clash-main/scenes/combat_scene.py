"""SHADOW CLASH - Main Combat Scene.

Simulates 1-on-1 martial arts bouts with player controls, enemy AI,
collision detection, particle effects, HUD overlays, pause menu, and match resolution.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING, Optional
import pygame

from settings import (
    DATA_DIR, GROUND_Y, COLOR_MOONLIGHT, COLOR_AMBER_GOLD,
    COLOR_CRIMSON_GLOW, LOGICAL_WIDTH, LOGICAL_HEIGHT
)
from scenes.base_scene import BaseScene
from scenes.results_scene import ResultsScene
from entities.player import PlayerFighter
from entities.enemy import EnemyFighter
from ai.enemy_controller import EnemyController
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


class CombatScene(BaseScene):
    """Real-time combat arena simulation."""

    def __init__(self, scene_manager: SceneManager, stage_id: int = 1) -> None:
        super().__init__(scene_manager)
        self.stage_id = stage_id
        
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        
        # Load Stage Configuration
        self.stage_info = self._load_stage_data(stage_id)
        self.arena_name = self.stage_info.get("arena", "abandoned_dojo")
        self.bgm_name = self.stage_info.get("bgm", "bgm_combat")
        self.reward_coins = int(self.stage_info.get("reward_coins", 100))
        self.reward_exp = int(self.stage_info.get("reward_exp", 80))
        
        # Progression & Fighter instantiation
        self.save_mgr = SaveManager()
        self.progression = ProgressionSystem(self.save_mgr)
        
        self.player = PlayerFighter(x=380.0, y=GROUND_Y)
        self.progression.apply_to_player(self.player)
        
        enemy_archetype = self.stage_info.get("enemy_key", "rogue")
        self.enemy = EnemyFighter(archetype_key=enemy_archetype, x=880.0, y=GROUND_Y)
        self.enemy_ai = EnemyController(self.enemy)
        
        # Subsystems
        self.combat_system = CombatSystem()
        self.hud = CombatHUD()
        
        # Match Time & State
        self.time_remaining: float = 99.0
        self.is_paused: bool = False
        self.is_match_over: bool = False
        self.game_over_timer: float = 0.0
        self.winner: Optional[str] = None
        
        # Pause Menu Buttons
        self.pause_buttons: list[Button] = []
        self._init_pause_menu()

    def _load_stage_data(self, s_id: int) -> dict:
        stages_path = DATA_DIR / "stages.json"
        if stages_path.is_file():
            try:
                with open(stages_path, "r", encoding="utf-8") as f:
                    stages = json.load(f)
                    for stg in stages:
                        if stg.get("stage_id") == s_id:
                            return stg
            except Exception as e:
                print(f"[CombatScene] Error loading stage {s_id}: {e}")
        return {
            "stage_id": s_id,
            "title": f"Stage {s_id}",
            "arena": "abandoned_dojo",
            "enemy_key": "rogue",
            "bgm": "bgm_combat",
            "reward_coins": 100,
            "reward_exp": 100
        }

    def _init_pause_menu(self) -> None:
        cx = 640
        btn_w, btn_h = 240, 48
        self.pause_buttons = [
            Button(pygame.Rect(cx - btn_w // 2, 280, btn_w, btn_h), "RESUME", self._toggle_pause),
            Button(pygame.Rect(cx - btn_w // 2, 345, btn_w, btn_h), "RESTART", self._restart_fight),
            Button(pygame.Rect(cx - btn_w // 2, 410, btn_w, btn_h), "MAIN MENU", self._quit_to_menu),
        ]

    def on_enter(self) -> None:
        self.audio_mgr.play_bgm(self.bgm_name, loop=True)

    def on_exit(self) -> None:
        self.audio_mgr.stop_bgm()

    def _toggle_pause(self) -> None:
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.audio_mgr.pause_bgm()
        else:
            self.audio_mgr.unpause_bgm()

    def _restart_fight(self) -> None:
        self.scene_manager.change_scene(CombatScene(self.scene_manager, self.stage_id))

    def _quit_to_menu(self) -> None:
        from scenes.main_menu import MainMenuScene
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
            if not self.is_match_over:
                self._toggle_pause()
                return

        if self.is_paused:
            mouse_pos = self.input_mgr.get_mouse_logical_pos()
            for btn in self.pause_buttons:
                btn.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        if self.is_paused:
            return  # Complete simulation freeze during pause
            
        # 1. Player Input Processing
        if not self.is_match_over:
            self.player.handle_input()
            
        # 2. Advance Entities
        self.player.update(dt, opponent=self.enemy)
        self.enemy.update(dt, opponent=self.player)
        
        # 3. Enemy AI Decisions
        if not self.is_match_over:
            self.enemy_ai.update(dt, self.player)

        # 4. Resolve Combat Interactions
        self.combat_system.update(dt, self.player, self.enemy)

        # 5. Timer Tick & Match Over Evaluation
        if not self.is_match_over:
            self.time_remaining -= dt
            
            # Check Time Out
            if self.time_remaining <= 0.0:
                self.time_remaining = 0.0
                self.is_match_over = True
                p_ratio = self.player.current_health / self.player.max_health
                e_ratio = self.enemy.current_health / self.enemy.max_health
                self.winner = "player" if p_ratio >= e_ratio else "enemy"
                
            # Check Knockout
            elif not self.player.is_alive:
                self.is_match_over = True
                self.winner = "enemy"
            elif not self.enemy.is_alive:
                self.is_match_over = True
                self.winner = "player"
                
        else:
            # Match is over: short delay before showing results
            self.game_over_timer += dt
            if self.game_over_timer >= 1.8:
                is_vic = (self.winner == "player")
                flawless = (self.player.current_health == self.player.max_health)
                self.scene_manager.change_scene(ResultsScene(
                    scene_manager=self.scene_manager,
                    is_victory=is_vic,
                    stage_id=self.stage_id,
                    reward_coins=self.reward_coins,
                    reward_exp=self.reward_exp,
                    highest_combo=self.combat_system.player_combo.max_combo,
                    flawless=flawless
                ))

    def render(self, surface: pygame.Surface) -> None:
        # 1. Arena Background
        arena_bg = self.asset_mgr.get_arena(self.arena_name)
        surface.blit(arena_bg, (0, 0))

        # 2. Render Fighters
        self.enemy.render(surface)
        self.player.render(surface)

        # 3. Combat FX & Damage Numbers
        self.combat_system.particle_sys.render(surface, self.hud.combo_font_small)

        # 4. Combat HUD
        self.hud.render(
            surface=surface,
            player=self.player,
            enemy=self.enemy,
            fight_time_remaining=self.time_remaining,
            player_combo=self.combat_system.player_combo,
            stage_title=self.stage_info.get("title", "BATTLE")
        )

        # 5. Pause Menu Overlay
        if self.is_paused:
            veil = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            veil.fill((8, 10, 16, 210))
            surface.blit(veil, (0, 0))

            cx = 640
            title_font = self.asset_mgr.get_font(48, bold=True)
            Typography.draw_text_with_shadow(
                surface, "GAME PAUSED", title_font, COLOR_MOONLIGHT, cx, 190, align="center"
            )

            for btn in self.pause_buttons:
                btn.render(surface)
