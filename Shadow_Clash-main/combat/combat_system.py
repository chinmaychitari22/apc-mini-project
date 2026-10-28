"""SHADOW CLASH - Unified Combat System Coordinator.

Coordinates hit detection between fighters, resolves damage calculations,
block reductions, combo increments, energy accumulation, and visual feedback.
"""

from __future__ import annotations
from typing import Optional
from entities.fighter import Fighter
from combat.collision import CollisionEngine
from combat.combo_system import ComboTracker
from systems.particles import ParticleSystem
from game.audio_manager import AudioManager


class CombatSystem:
    """Manages offensive and defensive interactions between fighters in battle."""

    def __init__(self) -> None:
        self.player_combo = ComboTracker("Player")
        self.enemy_combo = ComboTracker("Enemy")
        self.particle_sys = ParticleSystem.get_instance()
        self.audio_mgr = AudioManager.get_instance()

    def reset(self) -> None:
        """Reset combos and clear lingering effects."""
        self.player_combo.reset()
        self.enemy_combo.reset()
        self.particle_sys.clear()

    def update(self, dt: float, player: Fighter, enemy: Fighter) -> None:
        """Process combat collisions and advance combo counters."""
        # Update combo timers
        self.player_combo.update(dt)
        self.enemy_combo.update(dt)
        
        # Advance particle simulations
        self.particle_sys.update(dt)

        # 1. Check Player attacking Enemy
        if player.active_hitbox and enemy.is_alive:
            hit, contact_pt = CollisionEngine.check_hit(player.active_hitbox, enemy.hurtbox)
            if hit:
                self._resolve_attack_hit(
                    attacker=player,
                    defender=enemy,
                    combo=self.player_combo,
                    contact_point=contact_pt
                )

        # 2. Check Enemy attacking Player
        if enemy.active_hitbox and player.is_alive:
            hit, contact_pt = CollisionEngine.check_hit(enemy.active_hitbox, player.hurtbox)
            if hit:
                self._resolve_attack_hit(
                    attacker=enemy,
                    defender=player,
                    combo=self.enemy_combo,
                    contact_point=contact_pt
                )

    def _resolve_attack_hit(
        self,
        attacker: Fighter,
        defender: Fighter,
        combo: ComboTracker,
        contact_point: Optional[tuple[int, int]]
    ) -> None:
        """Calculate and apply strike resolution."""
        atk = attacker.current_attack
        if not atk:
            return
            
        # Calculate base strike damage with weapon and strength modifiers
        raw_damage = atk.damage * attacker.damage_multiplier * attacker.weapon.damage_mult
        
        # Calculate knockback vector
        kb = (atk.knockback_x, atk.knockback_y)
        
        # Apply hit to defender
        effective_dmg, was_blocked = defender.take_hit(
            damage=raw_damage,
            knockback=kb,
            stun_duration=atk.stun_duration,
            attacker_facing_right=attacker.facing_right,
            guard_damage=atk.guard_damage + attacker.weapon.guard_damage_bonus,
            particles=self.particle_sys
        )
        
        # If not blocked (or chipped), increment attacker combo
        if not was_blocked and defender.is_alive:
            combo.register_hit(effective_dmg)
            # Energy reward for successful hit
            gain = atk.energy_gain * attacker.weapon.energy_gain_mult
            attacker.add_energy(gain)
            
            # Additional bonus energy on combo streaks
            streak_bonus = combo.get_energy_bonus()
            if streak_bonus > 0:
                attacker.add_energy(streak_bonus)
                
            # Intercept defender's combo if defender was hit cleanly
            if attacker.is_player:
                self.enemy_combo.reset()
            else:
                self.player_combo.reset()
        elif was_blocked:
            # Chip energy gain
            attacker.add_energy(atk.energy_gain * 0.4)
