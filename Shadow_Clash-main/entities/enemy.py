"""SHADOW CLASH - Enemy Fighter Entity.

Fighter subclass configured with archetype data (Rogue, Swift Fang, Iron Guard,
Night Reaper, Shadow Master), boss phases, and AI linkage.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from entities.fighter import Fighter
from settings import DATA_DIR, GROUND_Y


class EnemyFighter(Fighter):
    """Computer-controlled martial arts opponent."""

    def __init__(
        self,
        archetype_key: str = "rogue",
        x: float = 880.0,
        y: float = GROUND_Y,
        difficulty_scale: float = 1.0
    ) -> None:
        self.archetype_key = archetype_key
        raw_config = self._load_enemy_config(archetype_key)
        
        name = raw_config.get("name", "Enemy")
        arch = raw_config.get("archetype", archetype_key)
        base_hp = float(raw_config.get("max_health", 200)) * difficulty_scale
        base_spd = float(raw_config.get("speed", 300))
        
        super().__init__(
            entity_id=2,
            name=name,
            archetype=arch,
            x=x,
            y=y,
            facing_right=False,
            max_health=base_hp,
            speed=base_spd,
            is_player=False
        )
        
        self.config = raw_config
        self.is_boss: bool = raw_config.get("is_boss", False)
        self.phases: list[dict] = raw_config.get("phases", [])
        self.current_phase: int = 1
        
        # Apply initial attack/defense scalars
        self.damage_multiplier = float(raw_config.get("attack_power", 1.0)) * difficulty_scale
        self.defense_multiplier = float(raw_config.get("defense", 1.0))

    def _load_enemy_config(self, key: str) -> dict:
        enemies_file = DATA_DIR / "enemies.json"
        if enemies_file.is_file():
            try:
                with open(enemies_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(key, {})
            except Exception as e:
                print(f"[EnemyFighter] Error loading enemy config: {e}")
        return {
            "name": key.title(),
            "archetype": key,
            "max_health": 200,
            "speed": 300,
            "attack_power": 1.0,
            "defense": 1.0
        }

    def check_boss_phase_transition(self) -> Optional[int]:
        """Evaluate boss health percentage and transition to next phase if reached."""
        if not self.is_boss or not self.phases or not self.is_alive:
            return None
            
        health_pct = self.current_health / max(1.0, self.max_health)
        for phase_info in reversed(self.phases):
            threshold = float(phase_info.get("health_threshold", 0.0))
            p_num = int(phase_info.get("phase", 1))
            if health_pct <= threshold and p_num > self.current_phase:
                self.current_phase = p_num
                # Apply phase stat boosts
                self.base_speed *= float(phase_info.get("speed_mult", 1.0))
                self.damage_multiplier *= float(phase_info.get("damage_mult", 1.0))
                return self.current_phase
        return None
