"""SHADOW CLASH - Adaptive AI System: Shadow Resonance.

Maintains bounded memory of the player's recent combat habits (attack frequency,
block tendencies, jumping habits) to adapt enemy decision weights dynamically.
"""

from __future__ import annotations
from collections import deque
from typing import Optional


class ShadowResonance:
    """Tracks player habit patterns to dynamically influence enemy tactical decisions."""

    def __init__(self, history_size: int = 12) -> None:
        self.history_size = history_size
        self.player_actions: deque[str] = deque(maxlen=history_size)
        self.consecutive_player_attacks: int = 0
        self.consecutive_player_blocks: int = 0

    def record_player_action(self, action_type: str) -> None:
        """Record player combat action ('punch', 'kick', 'block', 'special', 'jump', 'idle')."""
        self.player_actions.append(action_type)
        if action_type in ("punch", "kick", "special"):
            self.consecutive_player_attacks += 1
            self.consecutive_player_blocks = 0
        elif action_type == "block":
            self.consecutive_player_blocks += 1
            self.consecutive_player_attacks = 0
        else:
            self.consecutive_player_attacks = max(0, self.consecutive_player_attacks - 1)
            self.consecutive_player_blocks = max(0, self.consecutive_player_blocks - 1)

    @property
    def player_is_overly_aggressive(self) -> bool:
        """Player spamming attacks without defending."""
        return self.consecutive_player_attacks >= 3

    @property
    def player_is_turtling(self) -> bool:
        """Player camping in defensive block."""
        return self.consecutive_player_blocks >= 2

    def get_recommended_counter(self) -> Optional[str]:
        """Suggest tactical counter move based on observed pattern."""
        if self.player_is_turtling:
            # Guard break or low sweep recommended against defensive camping
            return "guard_break"
        elif self.player_is_overly_aggressive:
            # Counter-hit or block-and-punish recommended
            return "block_and_punish"
        return None
