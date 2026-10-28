"""SHADOW CLASH - Screenshot Capture and Visual Inspection Tool.

Renders each scene (Main Menu, Combat Arena, Dojo Training, Armory Shop, Settings)
and saves full-resolution 1280x720 PNG screenshots for visual quality assurance.
"""

from __future__ import annotations
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pygame

from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT
from game.scene_manager import SceneManager
from game.input_manager import InputManager
from scenes.main_menu import MainMenuScene
from scenes.combat_scene import CombatScene
from scenes.training_scene import TrainingScene
from scenes.shop_scene import ShopScene
from scenes.settings_scene import SettingsScene
from scenes.results_scene import ResultsScene

OUT_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def capture_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pygame.init()
    pygame.font.init()
    window = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    
    scene_mgr = SceneManager()
    
    # 1. Main Menu
    menu = MainMenuScene(scene_mgr)
    scene_mgr.change_scene(menu)
    scene_mgr.update(0.01)
    scene_mgr.render(window)
    pygame.image.save(window, str(OUT_DIR / "01_main_menu.png"))
    print("Saved 01_main_menu.png")
    
    # 2. Combat Arena
    combat = CombatScene(scene_mgr, stage_id=1)
    scene_mgr.change_scene(combat)
    # Simulate a few frames so fighters settle
    for _ in range(30):
        combat.update(1.0 / 60.0)
    scene_mgr.render(window)
    pygame.image.save(window, str(OUT_DIR / "02_combat_arena.png"))
    print("Saved 02_combat_arena.png")

    # 3. Training Dojo
    training = TrainingScene(scene_mgr)
    scene_mgr.change_scene(training)
    for _ in range(15):
        training.update(1.0 / 60.0)
    scene_mgr.render(window)
    pygame.image.save(window, str(OUT_DIR / "03_training_dojo.png"))
    print("Saved 03_training_dojo.png")

    # 4. Armory Shop
    shop = ShopScene(scene_mgr)
    scene_mgr.change_scene(shop)
    scene_mgr.update(0.01)
    scene_mgr.render(window)
    pygame.image.save(window, str(OUT_DIR / "04_armory_shop.png"))
    print("Saved 04_armory_shop.png")

    # 5. Settings
    settings = SettingsScene(scene_mgr)
    scene_mgr.change_scene(settings)
    scene_mgr.update(0.01)
    scene_mgr.render(window)
    pygame.image.save(window, str(OUT_DIR / "05_settings.png"))
    print("Saved 05_settings.png")

    # 6. Victory Results
    results = ResultsScene(
        scene_manager=scene_mgr,
        is_victory=True,
        stage_id=1,
        reward_coins=120,
        reward_exp=100,
        highest_combo=7,
        flawless=True
    )
    scene_mgr.change_scene(results)
    scene_mgr.update(0.01)
    scene_mgr.render(window)
    pygame.image.save(window, str(OUT_DIR / "06_results_victory.png"))
    print("Saved 06_results_victory.png")

    print(f"All screenshots successfully saved to {OUT_DIR}")


if __name__ == "__main__":
    capture_all()
