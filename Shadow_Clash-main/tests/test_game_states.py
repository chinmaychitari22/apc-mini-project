"""Automated Tests - Game Scenes and State Transitions."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from game.scene_manager import SceneManager
from scenes.main_menu import MainMenuScene
from scenes.combat_scene import CombatScene
from scenes.training_scene import TrainingScene
from scenes.survival_scene import SurvivalScene
from scenes.shop_scene import ShopScene
from scenes.settings_scene import SettingsScene
from scenes.results_scene import ResultsScene


class TestGameStates(unittest.TestCase):
    def setUp(self) -> None:
        self.scene_mgr = SceneManager()

    def test_initial_main_menu_transition(self) -> None:
        menu = MainMenuScene(self.scene_mgr)
        self.scene_mgr.change_scene(menu)
        self.assertIs(self.scene_mgr.current_scene, menu)

    def test_combat_scene_lifecycle(self) -> None:
        combat = CombatScene(self.scene_mgr, stage_id=1)
        self.scene_mgr.change_scene(combat)
        self.assertIs(self.scene_mgr.current_scene, combat)

        # Update several frames without errors
        for _ in range(15):
            combat.update(1.0 / 60.0)

        # Pause and Resume
        self.assertFalse(combat.is_paused)
        combat._toggle_pause()
        self.assertTrue(combat.is_paused)
        combat._toggle_pause()
        self.assertFalse(combat.is_paused)

    def test_training_and_survival_scenes(self) -> None:
        training = TrainingScene(self.scene_mgr)
        self.scene_mgr.change_scene(training)
        self.assertIs(self.scene_mgr.current_scene, training)
        training.update(1.0 / 60.0)

        survival = SurvivalScene(self.scene_mgr)
        self.scene_mgr.change_scene(survival)
        self.assertIs(self.scene_mgr.current_scene, survival)
        survival.update(1.0 / 60.0)

    def test_shop_and_settings_scenes(self) -> None:
        shop = ShopScene(self.scene_mgr)
        self.scene_mgr.change_scene(shop)
        self.assertIs(self.scene_mgr.current_scene, shop)
        shop.update(1.0 / 60.0)

        settings = SettingsScene(self.scene_mgr)
        self.scene_mgr.change_scene(settings)
        self.assertIs(self.scene_mgr.current_scene, settings)
        settings.update(1.0 / 60.0)

    def test_results_scene_transition(self) -> None:
        results = ResultsScene(
            scene_manager=self.scene_mgr,
            is_victory=True,
            stage_id=1,
            reward_coins=120,
            reward_exp=100,
            highest_combo=6,
            flawless=True
        )
        self.scene_mgr.change_scene(results)
        self.assertIs(self.scene_mgr.current_scene, results)
        results.update(1.0 / 60.0)


if __name__ == "__main__":
    unittest.main()
