"""SHADOW CLASH - In-Game Economy and Weapon Marketplace.

Enforces transactional integrity for currency, item purchases, weapon equipping,
and encounter reward distribution.
"""

from __future__ import annotations
from typing import Optional
from systems.save_manager import SaveManager
from entities.weapon import WeaponRegistry


class EconomyManager:
    """Handles weapon store inventory, purchases, and combat earnings."""

    def __init__(self, save_mgr: SaveManager) -> None:
        self.save_mgr = save_mgr

    @property
    def current_coins(self) -> int:
        return int(self.save_mgr.data.get("coins", 0))

    def is_weapon_owned(self, weapon_id: str) -> bool:
        return weapon_id in self.save_mgr.data.get("owned_weapons", [])

    def is_weapon_equipped(self, weapon_id: str) -> bool:
        return self.save_mgr.data.get("equipped_weapon") == weapon_id

    def can_afford(self, amount: int) -> bool:
        return self.current_coins >= max(0, amount)

    def buy_weapon(self, weapon_id: str) -> bool:
        """Purchase weapon if affordable and not already owned."""
        if self.is_weapon_owned(weapon_id):
            return False
            
        weapon = WeaponRegistry.get(weapon_id)
        if not self.can_afford(weapon.price):
            return False
            
        self.save_mgr.data["coins"] = self.current_coins - weapon.price
        owned = self.save_mgr.data.get("owned_weapons", [])
        owned.append(weapon_id)
        self.save_mgr.data["owned_weapons"] = owned
        
        # Auto-equip newly purchased weapon
        self.save_mgr.data["equipped_weapon"] = weapon_id
        self.save_mgr.save()
        return True

    def equip_weapon(self, weapon_id: str) -> bool:
        """Equip an owned weapon."""
        if not self.is_weapon_owned(weapon_id):
            return False
            
        self.save_mgr.data["equipped_weapon"] = weapon_id
        self.save_mgr.save()
        return True

    def award_rewards(self, coins: int, exp: int) -> None:
        """Safely credit player earnings."""
        if coins > 0:
            self.save_mgr.data["coins"] = self.current_coins + coins
        if exp > 0:
            cur_exp = self.save_mgr.data.get("experience", 0)
            self.save_mgr.data["experience"] = cur_exp + exp
        self.save_mgr.save()
