"""SHADOW CLASH - Achievement System.

Tracks milestone conditions, distributes bonus currency rewards,
and triggers on-screen celebratory notifications.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from settings import DATA_DIR
from systems.save_manager import SaveManager


class AchievementManager:
    """Manages player milestones, condition checks, and reward unlocks."""

    def __init__(self, save_mgr: SaveManager) -> None:
        self.save_mgr = save_mgr
        self.achievements_dict = self._load_definitions()
        self.recent_unlocks: list[dict] = []

    def _load_definitions(self) -> dict[str, dict]:
        ach_file = DATA_DIR / "achievements.json"
        if ach_file.is_file():
            try:
                with open(ach_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    return {item["id"]: item for item in raw}
            except Exception as e:
                print(f"[AchievementManager] Error loading achievements.json: {e}")
        return {}

    def is_unlocked(self, ach_id: str) -> bool:
        return ach_id in self.save_mgr.data.get("unlocked_achievements", [])

    def unlock(self, ach_id: str) -> bool:
        """Unlock an achievement, grant currency, and save."""
        if ach_id not in self.achievements_dict or self.is_unlocked(ach_id):
            return False
            
        data = self.achievements_dict[ach_id]
        unlocked = self.save_mgr.data.get("unlocked_achievements", [])
        unlocked.append(ach_id)
        self.save_mgr.data["unlocked_achievements"] = unlocked
        
        # Grant reward
        reward = int(data.get("reward_coins", 50))
        cur_coins = int(self.save_mgr.data.get("coins", 0))
        self.save_mgr.data["coins"] = cur_coins + reward
        
        self.save_mgr.save()
        self.recent_unlocks.append(data)
        return True

    def check_combat_milestones(
        self,
        victory: bool,
        highest_combo: int,
        flawless: bool,
        is_boss_defeat: bool = False
    ) -> list[dict]:
        """Check combat-related achievement criteria."""
        newly_unlocked = []
        if victory and self.unlock("first_blood"):
            newly_unlocked.append(self.achievements_dict["first_blood"])
        if highest_combo >= 8 and self.unlock("combo_master"):
            newly_unlocked.append(self.achievements_dict["combo_master"])
        if flawless and self.unlock("flawless_victory"):
            newly_unlocked.append(self.achievements_dict["flawless_victory"])
        if is_boss_defeat and self.unlock("shadow_slayer"):
            newly_unlocked.append(self.achievements_dict["shadow_slayer"])
        return newly_unlocked

    def check_collection_milestones(self) -> list[dict]:
        """Check weapon collection criteria."""
        newly_unlocked = []
        owned = self.save_mgr.data.get("owned_weapons", [])
        if len(owned) >= 3 and self.unlock("weapon_collector"):
            newly_unlocked.append(self.achievements_dict["weapon_collector"])
        return newly_unlocked

    def check_survival_milestone(self, wave_reached: int) -> list[dict]:
        """Check survival wave criteria."""
        newly_unlocked = []
        if wave_reached >= 5 and self.unlock("survival_veteran"):
            newly_unlocked.append(self.achievements_dict["survival_veteran"])
        return newly_unlocked
