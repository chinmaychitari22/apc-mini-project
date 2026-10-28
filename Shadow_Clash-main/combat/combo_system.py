"""SHADOW CLASH - Combo Counter and Tracking System.

Tracks consecutive hit strings, calculates combo multiplier rewards,
and resets when the timeout expires or when the attacker is interrupted.
"""

from __future__ import annotations
from typing import Optional
from settings import COMBO_TIMEOUT


class ComboTracker:
    """Maintains combo state for an attacking fighter."""

    def __init__(self, owner_name: str = "Player") -> None:
        self.owner_name = owner_name
        self.combo_count: int = 0
        self.combo_damage: float = 0.0
        self.timer: float = 0.0
        self.max_combo: int = 0
        self.highest_combo_reached: int = 0

    def register_hit(self, damage: float) -> int:
        """Register a successful offensive strike."""
        self.combo_count += 1
        self.combo_damage += damage
        self.timer = COMBO_TIMEOUT
        
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
            self.highest_combo_reached = self.combo_count
            
        return self.combo_count

    def update(self, dt: float) -> bool:
        """Tick combo timer down. Returns True if combo just expired this tick."""
        if self.combo_count > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.reset()
                return True
        return False

    def reset(self) -> None:
        """Reset current active combo."""
        self.combo_count = 0
        self.combo_damage = 0.0
        self.timer = 0.0

    @property
    def is_active(self) -> bool:
        return self.combo_count > 1 and self.timer > 0.0

    def get_energy_bonus(self) -> float:
        """Bonus energy awarded on combo escalation."""
        if self.combo_count == 3:
            return 8.0
        elif self.combo_count == 5:
            return 14.0
        elif self.combo_count == 8:
            return 22.0
        return 0.0
