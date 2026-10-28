"""SHADOW CLASH - Hitbox and Hurtbox Collision Boundaries.

Provides spatial volumes for hit detection, tracking targets hit during
individual attack activations to prevent repeated multi-frame damage.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from combat.attack import AttackData


class Hitbox:
    """An active damage-dealing spatial volume."""

    def __init__(
        self,
        owner_id: int,
        attack_data: AttackData,
        x: float,
        y: float,
        width: float,
        height: float,
        facing_right: bool,
        reach_bonus: float = 0.0
    ) -> None:
        self.owner_id = owner_id
        self.attack_data = attack_data
        self.facing_right = facing_right
        
        # Apply weapon reach bonus
        effective_width = width + reach_bonus
        if facing_right:
            effective_x = x
        else:
            effective_x = x - effective_width
            
        self.rect = pygame.Rect(int(effective_x), int(y), int(effective_width), int(height))
        self.is_active: bool = True
        self.targets_hit: set[int] = set()

    def has_hit_target(self, target_id: int) -> bool:
        return target_id in self.targets_hit

    def register_hit(self, target_id: int) -> None:
        self.targets_hit.add(target_id)

    def intersects(self, hurtbox: Hurtbox) -> bool:
        if not self.is_active or not hurtbox.is_active:
            return False
        return self.rect.colliderect(hurtbox.rect)


class Hurtbox:
    """A vulnerable receiver volume attached to a fighter."""

    def __init__(self, owner_id: int, x: float, y: float, width: float, height: float) -> None:
        self.owner_id = owner_id
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.is_active: bool = True
        self.is_invulnerable: bool = False

    def update_position(self, center_x: float, baseline_y: float, width: float, height: float) -> None:
        """Update world space hurtbox bounds matching current stance."""
        self.rect.width = int(width)
        self.rect.height = int(height)
        self.rect.centerx = int(center_x)
        self.rect.bottom = int(baseline_y)
