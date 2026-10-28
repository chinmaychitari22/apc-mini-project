"""SHADOW CLASH - Player Progression and Upgrades System.

Computes upgraded statistics for the player fighter, manages stage unlock progression,
and synchronizes with local persistence.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from settings import DATA_DIR
from systems.save_manager import SaveManager
from entities.fighter import Fighter
from entities.weapon import WeaponRegistry


class ProgressionSystem:
    """Manages player leveling, purchased stat bonuses, and stage unlocking."""

    def __init__(self, save_mgr: Optional[SaveManager] = None) -> None:
        self.save_mgr = save_mgr if save_mgr else SaveManager()
        self.save_data = self.save_mgr.load()
        self.upgrades_config = self._load_upgrades_config()

    def _load_upgrades_config(self) -> dict:
        cfg_file = DATA_DIR / "upgrades.json"
        if cfg_file.is_file():
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ProgressionSystem] Error loading upgrades.json: {e}")
        return {}

    @property
    def coins(self) -> int:
        return self.save_data.get("coins", 0)

    @coins.setter
    def coins(self, value: int) -> None:
        self.save_data["coins"] = max(0, value)

    @property
    def max_unlocked_stage(self) -> int:
        return self.save_data.get("max_unlocked_stage", 1)

    def unlock_next_stage(self, completed_stage: int) -> int:
        """Unlock subsequent stage if not already unlocked."""
        current_max = self.save_data.get("max_unlocked_stage", 1)
        if completed_stage >= current_max:
            new_max = min(5, completed_stage + 1)
            self.save_data["max_unlocked_stage"] = new_max
            self.save_mgr.save()
            return new_max
        return current_max

    def get_upgrade_level(self, upgrade_key: str) -> int:
        return self.save_data.get("upgrades", {}).get(upgrade_key, 0)

    def get_upgrade_cost(self, upgrade_key: str) -> int:
        """Calculate coin cost for the next upgrade rank."""
        info = self.upgrades_config.get(upgrade_key, {})
        base = int(info.get("base_cost", 100))
        mult = float(info.get("cost_multiplier", 1.5))
        current_lvl = self.get_upgrade_level(upgrade_key)
        return int(base * (mult ** current_lvl))

    def can_purchase_upgrade(self, upgrade_key: str) -> bool:
        info = self.upgrades_config.get(upgrade_key, {})
        max_lvl = int(info.get("max_level", 5))
        current_lvl = self.get_upgrade_level(upgrade_key)
        if current_lvl >= max_lvl:
            return False
        return self.coins >= self.get_upgrade_cost(upgrade_key)

    def purchase_upgrade(self, upgrade_key: str) -> bool:
        """Buy upgrade, deduct coins, and persist."""
        if not self.can_purchase_upgrade(upgrade_key):
            return False
            
        cost = self.get_upgrade_cost(upgrade_key)
        self.coins -= cost
        self.save_data["upgrades"][upgrade_key] = self.get_upgrade_level(upgrade_key) + 1
        self.save_mgr.save()
        return True

    def apply_to_player(self, player: Fighter) -> None:
        """Inject calculated upgrade bonuses and equipped weapon into Player entity."""
        upgrades = self.save_data.get("upgrades", {})
        
        # Vitality -> +25 Max Health per level
        vit_lvl = upgrades.get("vitality", 0)
        player.max_health = 200.0 + vit_lvl * 25.0
        player.current_health = player.max_health
        player.health_delay = player.max_health
        
        # Strength -> +8% strike damage per level
        str_lvl = upgrades.get("strength", 0)
        player.damage_multiplier = 1.0 + str_lvl * 0.08
        
        # Defense -> +6% damage mitigation per level
        def_lvl = upgrades.get("defense", 0)
        player.defense_multiplier = 1.0 + def_lvl * 0.06
        
        # Special Efficiency -> +10% energy regen bonus per level
        sp_lvl = upgrades.get("special_efficiency", 0)
        player.energy_regen_bonus = sp_lvl * 0.10
        
        # Equip weapon
        eq_weapon_id = self.save_data.get("equipped_weapon", "training_gloves")
        player.equip_weapon(WeaponRegistry.get(eq_weapon_id))
