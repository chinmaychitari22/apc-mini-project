"""SHADOW CLASH - Survival Gauntlet Mode Scene.

Spawns consecutive waves of increasingly difficult opponents, partial health
recovery between bouts, wave counter tracking, and high-score persistence.
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING
import pygame

from settings import GROUND_Y, COLOR_AMBER_GOLD, COLOR_MOONLIGHT
from scenes.base_scene import BaseScene
from scenes.results_scene import ResultsScene
from entities.player import PlayerFighter
from entities.enemy import EnemyFighter
from ai.enemy_controller import EnemyController
from combat.combat_system import CombatSystem
from ui.components import CombatHUD
from systems.save_manager import SaveManager
from systems.progression import ProgressionSystem
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class SurvivalScene(BaseScene):
    """Endless wave survival challenge."""

    WAVE_SEQUENCE = ["rogue", "swift_fang", "iron_guard", "night_reaper", "shadow_master"]

    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        
        self.save_mgr = SaveManager()
        self.progression = ProgressionSystem(self.save_mgr)
        
        self.player = PlayerFighter(x=380.0, y=GROUND_Y)
        self.progression.apply_to_player(self.player)
        
        self.current_wave: int = 1
        self.combat_system = CombatSystem()
        self.hud = CombatHUD()
        
        self.enemy: EnemyFighter = self._spawn_wave_enemy(self.current_wave)
        self.enemy_ai: EnemyController = EnemyController(self.enemy, difficulty_scale=1.0)
        
        self.arena_cycle = ["abandoned_dojo", "crimson_forest", "ruined_temple"]
        self.arena_name = self.arena_cycle[0]
        
        self.wave_transition_timer: float = 0.0
        self.is_wave_transitioning: bool = False
        self.is_game_over: bool = False

    def _spawn_wave_enemy(self, wave: int) -> EnemyFighter:
        idx = (wave - 1) % len(self.WAVE_SEQUENCE)
        key = self.WAVE_SEQUENCE[idx]
        diff_scalar = 1.0 + (wave - 1) * 0.15
        return EnemyFighter(archetype_key=key, x=880.0, y=GROUND_Y, difficulty_scale=diff_scalar)

    def on_enter(self) -> None:
        self.audio_mgr.play_bgm("bgm_combat", loop=True)

    def on_exit(self) -> None:
        self.audio_mgr.stop_bgm()

    def update(self, dt: float) -> None:
        if self.is_game_over:
            return
            
        self.player.handle_input()
        self.player.update(dt, opponent=self.enemy)
        self.enemy.update(dt, opponent=self.player)
        
        if not self.is_wave_transitioning:
            self.enemy_ai.update(dt, self.player)
            self.combat_system.update(dt, self.player, self.enemy)

        # Check Player Defeat
        if not self.player.is_alive:
            self.is_game_over = True
            self.scene_manager.change_scene(ResultsScene(
                scene_manager=self.scene_manager,
                is_victory=False,
                stage_id=0,
                reward_coins=0,
                reward_exp=0,
                highest_combo=self.combat_system.player_combo.max_combo,
                flawless=False,
                is_survival=True,
                survival_wave=self.current_wave - 1
            ))
            return

        # Check Enemy Defeat -> Next Wave
        if not self.enemy.is_alive and not self.is_wave_transitioning:
            self.is_wave_transitioning = True
            self.wave_transition_timer = 1.6

        if self.is_wave_transitioning:
            self.wave_transition_timer -= dt
            if self.wave_transition_timer <= 0.0:
                self.is_wave_transitioning = False
                self.current_wave += 1
                
                # Heal player by 35% of max health for surviving wave
                heal_amt = self.player.max_health * 0.35
                self.player.current_health = min(self.player.max_health, self.player.current_health + heal_amt)
                self.player.health_delay = self.player.current_health
                
                # Advance arena
                self.arena_name = self.arena_cycle[(self.current_wave - 1) % len(self.arena_cycle)]
                
                # Spawn next opponent cleanly
                self.enemy = self._spawn_wave_enemy(self.current_wave)
                diff = 1.0 + (self.current_wave - 1) * 0.15
                self.enemy_ai = EnemyController(self.enemy, difficulty_scale=diff)
                self.combat_system.reset()

    def render(self, surface: pygame.Surface) -> None:
        bg = self.asset_mgr.get_arena(self.arena_name)
        surface.blit(bg, (0, 0))

        self.enemy.render(surface)
        self.player.render(surface)
        self.combat_system.particle_sys.render(surface, self.hud.combo_font_small)

        self.hud.render(
            surface=surface,
            player=self.player,
            enemy=self.enemy,
            fight_time_remaining=99.0,
            player_combo=self.combat_system.player_combo,
            stage_title=f"SURVIVAL - WAVE {self.current_wave}"
        )
