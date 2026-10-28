"""SHADOW CLASH - Attack Definitions and Data structures.

Loads attack characteristics (startup, active, recovery, reach, hitbox, knockback,
sound, energy cost) from data/attacks.json.
"""

from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional

from settings import DATA_DIR


@dataclass
class AttackData:
    """Data specification for a combat attack technique."""
    id: str
    name: str
    damage: float
    startup: float
    active: float
    recovery: float
    reach: float
    hitbox_offset_x: float
    hitbox_offset_y: float
    hitbox_width: float
    hitbox_height: float
    knockback_x: float
    knockback_y: float
    stun_duration: float
    block_chip: float
    guard_damage: int
    energy_cost: float
    energy_gain: float
    animation: str
    sound: str

    @property
    def total_duration(self) -> float:
        return self.startup + self.active + self.recovery

    @classmethod
    def from_dict(cls, attack_id: str, data: dict) -> AttackData:
        hb = data.get("hitbox", {})
        kb = data.get("knockback", [200, -80])
        return cls(
            id=attack_id,
            name=data.get("name", attack_id.title()),
            damage=float(data.get("damage", 15)),
            startup=float(data.get("startup", 0.1)),
            active=float(data.get("active", 0.15)),
            recovery=float(data.get("recovery", 0.2)),
            reach=float(data.get("reach", 80)),
            hitbox_offset_x=float(hb.get("offset_x", 40)),
            hitbox_offset_y=float(hb.get("offset_y", -80)),
            hitbox_width=float(hb.get("width", 60)),
            hitbox_height=float(hb.get("height", 40)),
            knockback_x=float(kb[0]),
            knockback_y=float(kb[1]),
            stun_duration=float(data.get("stun_duration", 0.3)),
            block_chip=float(data.get("block_chip", 0.2)),
            guard_damage=int(data.get("guard_damage", 1)),
            energy_cost=float(data.get("energy_cost", 0)),
            energy_gain=float(data.get("energy_gain", 10)),
            animation=data.get("animation", "light_punch"),
            sound=data.get("sound", "light_punch")
        )


class AttackRegistry:
    """Cache and provider of all loaded attack definitions."""
    
    _attacks: dict[str, AttackData] = {}

    @classmethod
    def load_attacks(cls) -> None:
        attacks_file = DATA_DIR / "attacks.json"
        if not attacks_file.is_file():
            print(f"[AttackRegistry] Missing attacks.json at {attacks_file}")
            return
            
        with open(attacks_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        cls._attacks = {
            k: AttackData.from_dict(k, v) 
            for k, v in raw_data.items()
        }

    @classmethod
    def get(cls, attack_id: str) -> Optional[AttackData]:
        if not cls._attacks:
            cls.load_attacks()
        return cls._attacks.get(attack_id)

    @classmethod
    def all_attacks(cls) -> dict[str, AttackData]:
        if not cls._attacks:
            cls.load_attacks()
        return dict(cls._attacks)
