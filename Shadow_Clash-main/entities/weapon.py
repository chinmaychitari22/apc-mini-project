"""SHADOW CLASH - Weapon Configuration and Equipment Logic.

Defines weapon combat modifications (damage multiplier, reach extension,
attack speed factor, guard breaking efficiency, energy siphon).
"""

from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional

from settings import DATA_DIR


@dataclass
class Weapon:
    """Equippable weapon data with combat stat modifiers."""
    id: str
    name: str
    description: str
    price: int
    damage_mult: float
    speed_mult: float
    reach_bonus: float
    guard_damage_bonus: int
    energy_gain_mult: float
    icon: str
    unlocked_by_default: bool

    @classmethod
    def from_dict(cls, weapon_id: str, data: dict) -> Weapon:
        return cls(
            id=weapon_id,
            name=data.get("name", weapon_id.title()),
            description=data.get("description", ""),
            price=int(data.get("price", 0)),
            damage_mult=float(data.get("damage_mult", 1.0)),
            speed_mult=float(data.get("speed_mult", 1.0)),
            reach_bonus=float(data.get("reach_bonus", 0.0)),
            guard_damage_bonus=int(data.get("guard_damage_bonus", 0)),
            energy_gain_mult=float(data.get("energy_gain_mult", 1.0)),
            icon=data.get("icon", f"{weapon_id}.png"),
            unlocked_by_default=bool(data.get("unlocked_by_default", False))
        )


class WeaponRegistry:
    """Provider for all loaded weapons."""
    
    _weapons: dict[str, Weapon] = {}

    @classmethod
    def load_weapons(cls) -> None:
        weapons_path = DATA_DIR / "weapons.json"
        if not weapons_path.is_file():
            print(f"[WeaponRegistry] Missing weapons.json at {weapons_path}")
            return
            
        with open(weapons_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            
        cls._weapons = {
            wid: Weapon.from_dict(wid, wdata)
            for wid, wdata in raw.items()
        }

    @classmethod
    def get(cls, weapon_id: str) -> Weapon:
        if not cls._weapons:
            cls.load_weapons()
        if weapon_id in cls._weapons:
            return cls._weapons[weapon_id]
        # Fallback default training gloves
        return Weapon(
            id="training_gloves",
            name="Training Gloves",
            description="Cloth hand wraps.",
            price=0,
            damage_mult=1.0,
            speed_mult=1.0,
            reach_bonus=0.0,
            guard_damage_bonus=0,
            energy_gain_mult=1.0,
            icon="training_gloves.png",
            unlocked_by_default=True
        )

    @classmethod
    def all_weapons(cls) -> dict[str, Weapon]:
        if not cls._weapons:
            cls.load_weapons()
        return dict(cls._weapons)
