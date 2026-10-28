"""Automated Tests - Progression, Economy, and Weapon Equipment."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
from pathlib import Path
import tempfile
import shutil

from systems.save_manager import SaveManager
from systems.progression import ProgressionSystem
from systems.economy import EconomyManager
from entities.fighter import Fighter


class TestProgression(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.save_mgr = SaveManager(saves_dir=self.temp_dir)
        self.progression = ProgressionSystem(self.save_mgr)
        self.economy = EconomyManager(self.save_mgr)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_stage_unlocking(self) -> None:
        self.assertEqual(self.progression.max_unlocked_stage, 1)
        # Beating stage 1 unlocks stage 2
        new_stage = self.progression.unlock_next_stage(1)
        self.assertEqual(new_stage, 2)
        self.assertEqual(self.progression.max_unlocked_stage, 2)

        # Re-beating stage 1 does not downgrade or corrupt stage 2
        self.progression.unlock_next_stage(1)
        self.assertEqual(self.progression.max_unlocked_stage, 2)

    def test_currency_and_weapon_purchase(self) -> None:
        # Default starting coins 150
        self.save_mgr.data["coins"] = 100
        # Steel knuckles price is 250 -> Cannot afford
        can_buy = self.economy.buy_weapon("steel_knuckles")
        self.assertFalse(can_buy)
        self.assertFalse(self.economy.is_weapon_owned("steel_knuckles"))

        # Credit coins and buy
        self.economy.award_rewards(coins=300, exp=100)
        self.assertEqual(self.economy.current_coins, 400)
        
        success = self.economy.buy_weapon("steel_knuckles")
        self.assertTrue(success)
        self.assertTrue(self.economy.is_weapon_owned("steel_knuckles"))
        self.assertEqual(self.economy.current_coins, 150)
        self.assertEqual(self.save_mgr.data["equipped_weapon"], "steel_knuckles")

    def test_upgrade_limits(self) -> None:
        self.save_mgr.data["coins"] = 10000  # Plenty of coins
        for lvl in range(5):
            self.assertTrue(self.progression.can_purchase_upgrade("vitality"))
            self.progression.purchase_upgrade("vitality")

        # Level reached max (5) -> cannot buy further
        self.assertEqual(self.progression.get_upgrade_level("vitality"), 5)
        self.assertFalse(self.progression.can_purchase_upgrade("vitality"))

    def test_stats_application_to_fighter(self) -> None:
        self.save_mgr.data["upgrades"]["vitality"] = 2   # +50 HP
        self.save_mgr.data["upgrades"]["strength"] = 2   # +16% dmg
        
        player = Fighter(1, "Player", "player", x=400.0)
        self.progression.apply_to_player(player)

        self.assertEqual(player.max_health, 250.0)
        self.assertAlmostEqual(player.damage_multiplier, 1.16, places=2)


if __name__ == "__main__":
    unittest.main()
