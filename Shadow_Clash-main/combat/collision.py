"""SHADOW CLASH - Collision Utilities.

Computes geometric intersections and impact contact points between hitboxes and hurtboxes.
"""

from __future__ import annotations
from typing import Optional, Tuple
import pygame
from combat.hitbox import Hitbox, Hurtbox


class CollisionEngine:
    """Evaluates spatial intersections between combat entities."""

    @staticmethod
    def check_hit(hitbox: Hitbox, hurtbox: Hurtbox) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """Check if an active hitbox strikes a vulnerable hurtbox.
        
        Returns:
            Tuple of (hit_occurred, impact_point_or_None)
        """
        if not hitbox.is_active or not hurtbox.is_active:
            return False, None
            
        if hurtbox.is_invulnerable:
            return False, None
            
        if hitbox.has_hit_target(hurtbox.owner_id):
            return False, None
            
        if hitbox.rect.colliderect(hurtbox.rect):
            # Calculate center of intersection rectangle for VFX positioning
            clip_rect = hitbox.rect.clip(hurtbox.rect)
            contact_point = clip_rect.center
            hitbox.register_hit(hurtbox.owner_id)
            return True, contact_point
            
        return False, None
