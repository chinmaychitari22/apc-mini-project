"""SHADOW CLASH - State-Driven Tactical Enemy AI Controller.

Evaluates spatial distancing, attack ranges, cooldown periods, player habits,
boss phase transitions, and executes adaptive combat decisions at controlled intervals.
"""

from __future__ import annotations
import random
from typing import Optional

from entities.enemy import EnemyFighter
from entities.fighter import Fighter, FighterState
from combat.attack import AttackRegistry, AttackData
from ai.adaptive_behavior import ShadowResonance


class EnemyController:
    """Tactical AI driver governing an EnemyFighter entity."""

    def __init__(self, enemy: EnemyFighter, difficulty_scale: float = 1.0) -> None:
        self.enemy = enemy
        self.difficulty_scale = difficulty_scale
        self.config = enemy.config
        
        # Archetype parameters
        self.reaction_time = float(self.config.get("reaction_time", 0.22)) / max(0.5, difficulty_scale)
        self.aggression = min(0.95, float(self.config.get("aggression", 0.6)) * difficulty_scale)
        self.base_block_tendency = float(self.config.get("block_tendency", 0.35))
        self.preferred_distance = float(self.config.get("preferred_distance", 85))
        self.retreat_chance = float(self.config.get("retreat_chance", 0.20))
        self.special_capable = bool(self.config.get("special_capable", False))
        
        # Decision Interval Timing
        self.decision_timer: float = 0.0
        self.current_tactical_action: str = "approach"
        self.action_duration: float = 0.25
        
        # Adaptive Behavior Tracker
        self.resonance = ShadowResonance()

    def update(self, dt: float, player: Fighter) -> None:
        """Evaluate AI behavior at controlled intervals."""
        if not self.enemy.is_alive or self.enemy.state == FighterState.DEFEAT:
            return
            
        # Check boss phase transition
        if self.enemy.is_boss:
            new_phase = self.enemy.check_boss_phase_transition()
            if new_phase:
                # Accelerate aggression and decrease decision delay in higher phases
                self.aggression = min(0.98, self.aggression + 0.15)
                self.reaction_time = max(0.08, self.reaction_time * 0.8)

        # Track player actions into resonance
        if player.state in (FighterState.ATTACK, FighterState.SPECIAL) and player.current_attack:
            if "punch" in player.current_attack.id:
                self.resonance.record_player_action("punch")
            elif "kick" in player.current_attack.id:
                self.resonance.record_player_action("kick")
            else:
                self.resonance.record_player_action("special")
        elif player.state == FighterState.BLOCK:
            self.resonance.record_player_action("block")

        # Tick decision interval
        self.decision_timer -= dt
        if self.decision_timer <= 0.0:
            self.decision_timer = self.reaction_time + random.uniform(-0.04, 0.04)
            self._make_tactical_decision(player)

    def _make_tactical_decision(self, player: Fighter) -> None:
        """Select tactical posture and movement/combat action."""
        if self.enemy.state in (FighterState.ATTACK, FighterState.SPECIAL, FighterState.HIT, 
                                FighterState.STUNNED, FighterState.KNOCKBACK):
            return  # Locked in commitment
            
        dx = player.x - self.enemy.x
        distance = abs(dx)
        dir_to_player = 1.0 if dx > 0 else -1.0
        
        # 1. Reactive Defense: Player is mid-attack and in dangerous striking range
        player_is_attacking = (player.state in (FighterState.ATTACK, FighterState.SPECIAL) and 
                               player.attack_phase in ("startup", "active"))
        
        block_chance = self.base_block_tendency
        if self.resonance.player_is_overly_aggressive:
            block_chance += 0.25  # Predict incoming attack and raise guard
            
        if player_is_attacking and distance < 110.0 and random.random() < block_chance:
            self.enemy.start_block()
            return
        else:
            self.enemy.stop_block()

        # 2. In Strikable Range: Select appropriate attack
        if distance <= 115.0:
            if random.random() < self.aggression:
                chosen_attack = self._select_attack(distance, player)
                if chosen_attack and self.enemy.start_attack(chosen_attack):
                    return

        # 3. Tactical Distance Management (Approach or Retreat)
        counter_rec = self.resonance.get_recommended_counter()
        
        if counter_rec == "guard_break" and distance > 85.0:
            # Advance decisively to crush defensive camping
            self.enemy.move(dir_to_player)
        elif distance > self.preferred_distance + 25.0:
            # Too far: Advance towards player
            self.enemy.move(dir_to_player)
        elif distance < self.preferred_distance - 25.0:
            # Too close: Chance to retreat or maintain spacing
            if random.random() < self.retreat_chance:
                self.enemy.move(-dir_to_player)
            else:
                self.enemy.move(0.0)
        else:
            # In sweet spot: circle or prepare strike
            if random.random() < 0.4:
                self.enemy.move(0.0)
            elif random.random() < 0.2:
                # Occasional tactical jump
                self.enemy.jump()

    def _select_attack(self, distance: float, player: Fighter) -> Optional[AttackData]:
        """Choose an optimal attack based on distance, energy, and enemy archetype."""
        # Special attack condition
        if self.special_capable and self.enemy.current_energy >= 60.0:
            if random.random() < 0.45:
                return AttackRegistry.get("special_attack")
                
        # Counter recommendation from Shadow Resonance
        counter_hint = self.resonance.get_recommended_counter()
        if counter_hint == "guard_break":
            # Select heavy straight strike or low sweep against turtling players
            return random.choice([AttackRegistry.get("heavy_punch"), AttackRegistry.get("crouch_attack")])

        # Distance-based selection
        if distance <= 70.0:
            candidates = ["light_punch", "light_kick", "crouch_attack"]
        elif distance <= 95.0:
            candidates = ["heavy_punch", "light_kick", "heavy_kick"]
        else:
            candidates = ["heavy_kick", "heavy_punch"]
            
        # Archetype biases
        arch = self.enemy.archetype
        if arch == "swift_fang":
            candidates.extend(["light_kick", "heavy_kick", "jump_kick"])
        elif arch == "iron_guard":
            candidates.extend(["heavy_punch", "heavy_kick"])
            
        chosen_id = random.choice(candidates)
        return AttackRegistry.get(chosen_id)
