"""SHADOW CLASH - Base Martial Arts Fighter Entity and State Machine.

Implements realistic martial arts physics, animation timing, hitboxes/hurtboxes,
guard breaking, damage mitigation, knockback, and defeat handling.
"""

from __future__ import annotations
from enum import Enum, auto
import math
from typing import Optional, TYPE_CHECKING
import pygame

from settings import (
    GRAVITY, GROUND_Y, ARENA_LEFT, ARENA_RIGHT,
    MAX_ENERGY, ENERGY_PASSIVE_REGEN,
    BLOCK_DAMAGE_REDUCTION, BLOCK_KNOCKBACK_FACTOR, GUARD_BREAK_THRESHOLD
)
from combat.hitbox import Hitbox, Hurtbox
from combat.attack import AttackData
from entities.weapon import Weapon, WeaponRegistry
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager

if TYPE_CHECKING:
    from systems.particles import ParticleSystem


class FighterState(Enum):
    """Fighter state machine states."""
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()
    LAND = auto()
    CROUCH = auto()
    ATTACK = auto()
    BLOCK = auto()
    HIT = auto()
    STUNNED = auto()
    KNOCKBACK = auto()
    SPECIAL = auto()
    VICTORY = auto()
    DEFEAT = auto()


class Fighter:
    """Core martial arts fighter entity."""

    def __init__(
        self,
        entity_id: int,
        name: str,
        archetype: str,
        x: float,
        y: float = GROUND_Y,
        facing_right: bool = True,
        max_health: float = 200.0,
        speed: float = 320.0,
        is_player: bool = False
    ) -> None:
        self.entity_id = entity_id
        self.name = name
        self.archetype = archetype
        self.is_player = is_player
        
        # Position & Physics
        self.x: float = x
        self.y: float = y
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.base_speed: float = speed
        self.jump_velocity: float = -780.0
        self.is_grounded: bool = (self.y >= GROUND_Y)
        self.facing_right: bool = facing_right
        
        # Health & Energy
        self.max_health: float = max_health
        self.current_health: float = max_health
        self.health_delay: float = max_health  # Smooth trailing red bar in HUD
        self.max_energy: float = MAX_ENERGY
        self.current_energy: float = 0.0
        
        # Defense & Guard
        self.is_blocking: bool = False
        self.consecutive_blocks: int = 0
        self.defense_multiplier: float = 1.0  # From upgrades/archetype
        self.damage_multiplier: float = 1.0
        self.energy_regen_bonus: float = 0.0
        
        # Weapon
        self.weapon: Weapon = WeaponRegistry.get("training_gloves")
        
        # State Machine & Animation
        self.state: FighterState = FighterState.IDLE
        self.current_anim: str = "idle"
        self.frame_index: int = 0
        self.frame_timer: float = 0.0
        self.frame_duration: float = 0.12
        
        # Attack Execution
        self.current_attack: Optional[AttackData] = None
        self.attack_phase: str = "none"  # "startup", "active", "recovery"
        self.attack_timer: float = 0.0
        self.active_hitbox: Optional[Hitbox] = None
        
        # Hit Stun & Incapacitation
        self.stun_timer: float = 0.0
        
        # Hurtbox Geometry (width 60, height 135)
        self.hurtbox = Hurtbox(
            owner_id=self.entity_id,
            x=self.x - 30,
            y=self.y - 135,
            width=60,
            height=135
        )
        
        # Subsystem references
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0.0

    @property
    def effective_speed(self) -> float:
        return self.base_speed * self.weapon.speed_mult

    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip new weapon and apply its modifiers."""
        self.weapon = weapon

    def face_towards(self, target_x: float) -> None:
        """Face towards target if not locked in an attack or hit animation."""
        if self.state not in (FighterState.ATTACK, FighterState.SPECIAL, FighterState.HIT, FighterState.KNOCKBACK, FighterState.DEFEAT):
            self.facing_right = (target_x >= self.x)

    def set_state(self, new_state: FighterState, anim_override: Optional[str] = None) -> None:
        """Transition fighter state and synchronize animation."""
        if self.state == FighterState.DEFEAT:
            return  # Dead fighters cannot leave defeat state
            
        self.state = new_state
        anim_name = anim_override if anim_override else new_state.name.lower()
        
        # Map state names to animation names
        state_anim_map = {
            "attack": self.current_attack.animation if self.current_attack else "light_punch",
            "special": "special",
            "hit": "hit",
            "stunned": "hit",
            "knockback": "knockback",
            "block": "block",
            "crouch": "crouch",
            "idle": "idle",
            "walk": "walk",
            "run": "run",
            "jump": "jump",
            "fall": "fall",
            "land": "land",
            "victory": "victory",
            "defeat": "defeat"
        }
        
        target_anim = anim_override or state_anim_map.get(anim_name, "idle")
        if target_anim != self.current_anim:
            self.current_anim = target_anim
            self.frame_index = 0
            self.frame_timer = 0.0

    def move(self, direction: float) -> None:
        """Apply horizontal walking movement."""
        if self.state in (FighterState.ATTACK, FighterState.SPECIAL, FighterState.HIT, 
                          FighterState.STUNNED, FighterState.KNOCKBACK, FighterState.BLOCK, 
                          FighterState.DEFEAT, FighterState.CROUCH):
            return
            
        if abs(direction) > 0.01:
            self.vx = direction * self.effective_speed
            if self.is_grounded:
                self.set_state(FighterState.WALK)
        else:
            self.vx = 0.0
            if self.is_grounded and self.state in (FighterState.WALK, FighterState.RUN):
                self.set_state(FighterState.IDLE)

    def jump(self) -> bool:
        """Initiate jump if grounded."""
        if not self.is_grounded or self.state in (
            FighterState.ATTACK, FighterState.SPECIAL, FighterState.HIT,
            FighterState.STUNNED, FighterState.KNOCKBACK, FighterState.BLOCK, FighterState.DEFEAT
        ):
            return False
            
        self.vy = self.jump_velocity
        self.is_grounded = False
        self.set_state(FighterState.JUMP)
        self.audio_mgr.play_sfx("jump")
        return True

    def crouch(self) -> None:
        """Enter low crouching stance."""
        if self.is_grounded and self.state in (FighterState.IDLE, FighterState.WALK):
            self.vx = 0.0
            self.set_state(FighterState.CROUCH)

    def uncrouch(self) -> None:
        """Release crouch."""
        if self.state == FighterState.CROUCH:
            self.set_state(FighterState.IDLE)

    def start_block(self) -> None:
        """Raise defensive guard."""
        if self.is_grounded and self.state in (FighterState.IDLE, FighterState.WALK):
            self.vx = 0.0
            self.is_blocking = True
            self.set_state(FighterState.BLOCK)

    def stop_block(self) -> None:
        """Lower guard."""
        if self.is_blocking:
            self.is_blocking = False
            self.consecutive_blocks = 0
            if self.state == FighterState.BLOCK:
                self.set_state(FighterState.IDLE)

    def start_attack(self, attack_data: AttackData) -> bool:
        """Initiate attack sequence if fighter is in a valid state."""
        if self.state in (FighterState.HIT, FighterState.STUNNED, FighterState.KNOCKBACK, 
                          FighterState.DEFEAT, FighterState.VICTORY):
            return False
            
        if self.state in (FighterState.ATTACK, FighterState.SPECIAL):
            return False  # Already in attack commitment
            
        # Check energy requirement for special attack
        if attack_data.energy_cost > 0:
            if self.current_energy < attack_data.energy_cost:
                return False
            self.current_energy -= attack_data.energy_cost
            self.audio_mgr.play_sfx("special_charge")
            
        self.current_attack = attack_data
        self.attack_phase = "startup"
        self.attack_timer = 0.0
        self.active_hitbox = None
        self.is_blocking = False
        
        # Slight forward momentum step on heavy attacks
        if attack_data.id == "heavy_punch":
            self.vx = (140.0 if self.facing_right else -140.0)
        elif attack_data.id == "heavy_kick":
            self.vx = (180.0 if self.facing_right else -180.0)
            
        new_state = FighterState.SPECIAL if attack_data.id == "special_attack" else FighterState.ATTACK
        self.set_state(new_state, attack_data.animation)
        return True

    def take_hit(
        self,
        damage: float,
        knockback: tuple[float, float],
        stun_duration: float,
        attacker_facing_right: bool,
        guard_damage: int = 1,
        particles: Optional[ParticleSystem] = None
    ) -> tuple[float, bool]:
        """Process incoming strike. Returns (actual_damage_taken, was_blocked)."""
        if not self.is_alive:
            return 0.0, False
            
        # Blocking check: Must be in block state AND facing towards the attacker
        is_facing_attacker = (self.facing_right != attacker_facing_right)
        blocked = (self.is_blocking and is_facing_attacker and self.is_grounded)
        
        if blocked:
            self.consecutive_blocks += guard_damage
            effective_damage = damage * (1.0 - BLOCK_DAMAGE_REDUCTION) / self.defense_multiplier
            # Apply blocked knockback
            kb_x = (knockback[0] if attacker_facing_right else -knockback[0]) * BLOCK_KNOCKBACK_FACTOR
            self.vx = kb_x
            
            # Sound & Particles
            self.audio_mgr.play_sfx("block")
            if particles:
                bx = self.x + (15 if self.facing_right else -15)
                by = self.y - 85
                particles.spawn_block_barrier(bx, by)
                particles.spawn_damage_number(f"-{int(effective_damage)}", bx, by - 20, (120, 210, 255))
                
            # Guard Break Check
            if self.consecutive_blocks >= GUARD_BREAK_THRESHOLD:
                self.consecutive_blocks = 0
                self.is_blocking = False
                self.stun_timer = 0.65
                self.set_state(FighterState.STUNNED)
                if particles:
                    particles.spawn_damage_number("GUARD BREAK!", self.x, self.y - 110, (255, 75, 95))
        else:
            effective_damage = damage / self.defense_multiplier
            self.consecutive_blocks = 0
            self.is_blocking = False
            
            # Cancel active attack if struck
            self.current_attack = None
            self.active_hitbox = None
            
            # Apply full knockback
            kb_x = (knockback[0] if attacker_facing_right else -knockback[0])
            self.vx = kb_x
            self.vy = knockback[1]
            if knockback[1] < -50:
                self.is_grounded = False
                
            self.stun_timer = stun_duration
            
            # Decide between Hit and Knockback states
            if abs(kb_x) > 350 or knockback[1] < -100:
                self.set_state(FighterState.KNOCKBACK)
            else:
                self.set_state(FighterState.HIT)
                
            if particles:
                contact_x = self.x - (10 if attacker_facing_right else -10)
                contact_y = self.y - 80
                particles.spawn_hit_sparks(contact_x, contact_y, is_critical=(damage >= 30))
                particles.spawn_damage_number(f"-{int(effective_damage)}", contact_x, contact_y - 25, (255, 230, 80))
                
        # Apply health reduction
        self.current_health = max(0.0, self.current_health - effective_damage)
        
        # Energy gain from taking damage
        self.add_energy(8.0)
        
        # Check Defeat
        if self.current_health <= 0.0:
            self.current_health = 0.0
            self.set_state(FighterState.DEFEAT)
            self.vx = 0.0
            self.vy = 0.0
            self.audio_mgr.play_sfx("defeat")
            
        return effective_damage, blocked

    def add_energy(self, amount: float) -> None:
        """Gain special meter energy."""
        self.current_energy = min(self.max_energy, self.current_energy + amount * (1.0 + self.energy_regen_bonus))

    def update(self, dt: float, opponent: Optional[Fighter] = None) -> None:
        """Advance physics, animation, and combat state machine."""
        # Smooth trailing health bar transition
        if self.health_delay > self.current_health:
            self.health_delay = max(self.current_health, self.health_delay - dt * 60.0)
            
        # Passive energy regeneration for living fighters
        if self.is_alive and self.state != FighterState.DEFEAT:
            self.add_energy(ENERGY_PASSIVE_REGEN * dt)
            
        # 1. Physics & Ground Collision
        if not self.is_grounded:
            self.vy += GRAVITY * dt
            self.y += self.vy * dt
            
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.vy = 0.0
                self.is_grounded = True
                self.audio_mgr.play_sfx("land")
                
                # Landing recovery transition
                if self.state in (FighterState.FALL, FighterState.JUMP):
                    self.set_state(FighterState.LAND)
            else:
                if self.vy > 0 and self.state == FighterState.JUMP:
                    self.set_state(FighterState.FALL)
                    
        # Apply horizontal velocity & friction
        self.x += self.vx * dt
        if self.is_grounded:
            self.vx *= (0.82 ** (dt * 60.0))
            if abs(self.vx) < 5.0:
                self.vx = 0.0
                
        # Arena boundary clamping
        if self.x < ARENA_LEFT:
            self.x = ARENA_LEFT
            self.vx = 0.0
        elif self.x > ARENA_RIGHT:
            self.x = ARENA_RIGHT
            self.vx = 0.0

        # Auto-face opponent when in neutral states
        if opponent and self.is_alive:
            self.face_towards(opponent.x)

        # 2. Update Hurtbox geometry
        hurtbox_h = 80.0 if self.state == FighterState.CROUCH else 135.0
        self.hurtbox.update_position(self.x, self.y, width=54.0, height=hurtbox_h)

        # 3. Handle Attack Sequence Progression
        if self.state in (FighterState.ATTACK, FighterState.SPECIAL) and self.current_attack:
            atk = self.current_attack
            self.attack_timer += dt * self.weapon.speed_mult
            
            # Phase 1: Startup
            if self.attack_timer < atk.startup:
                self.attack_phase = "startup"
                self.active_hitbox = None
                
            # Phase 2: Active Hit Window
            elif self.attack_timer < (atk.startup + atk.active):
                if self.attack_phase != "active":
                    self.attack_phase = "active"
                    # Play attack impact whoosh sound
                    self.audio_mgr.play_sfx(atk.sound)
                    
                    # Spawn active hitbox
                    hx = self.x + (atk.hitbox_offset_x if self.facing_right else -atk.hitbox_offset_x)
                    hy = self.y + atk.hitbox_offset_y
                    self.active_hitbox = Hitbox(
                        owner_id=self.entity_id,
                        attack_data=atk,
                        x=hx,
                        y=hy,
                        width=atk.hitbox_width,
                        height=atk.hitbox_height,
                        facing_right=self.facing_right,
                        reach_bonus=self.weapon.reach_bonus
                    )
            # Phase 3: Recovery
            elif self.attack_timer < atk.total_duration:
                self.attack_phase = "recovery"
                self.active_hitbox = None
            else:
                # Attack complete - return to neutral
                self.current_attack = None
                self.attack_phase = "none"
                self.active_hitbox = None
                self.set_state(FighterState.IDLE)

        # 4. Handle Stun / Hit Recovery
        elif self.state in (FighterState.HIT, FighterState.STUNNED, FighterState.KNOCKBACK):
            self.stun_timer -= dt
            if self.stun_timer <= 0.0 and self.is_alive and self.is_grounded:
                self.stun_timer = 0.0
                self.set_state(FighterState.IDLE)

        # 5. Handle Land State Recovery
        elif self.state == FighterState.LAND:
            if self.frame_index >= 2:
                self.set_state(FighterState.IDLE)

        # 6. Advance Sprite Animation Frames
        self._update_animation(dt)

    def _update_animation(self, dt: float) -> None:
        """Tick frame timers and handle looping / freeze frames."""
        frames = self.asset_mgr.get_character_frames(
            self.archetype, self.current_anim, self.facing_right
        )
        num_frames = len(frames)
        if num_frames == 0:
            return
            
        anim_speed = self.weapon.speed_mult if self.state == FighterState.ATTACK else 1.0
        self.frame_timer += dt * anim_speed
        
        if self.frame_timer >= self.frame_duration:
            self.frame_timer -= self.frame_duration
            self.frame_index += 1
            
            if self.frame_index >= num_frames:
                # Defeat holds the final collapsed frame
                if self.state == FighterState.DEFEAT:
                    self.frame_index = num_frames - 1
                elif self.state in (FighterState.IDLE, FighterState.WALK, FighterState.RUN, FighterState.VICTORY):
                    self.frame_index = 0
                else:
                    self.frame_index = num_frames - 1

    def render(self, surface: pygame.Surface) -> None:
        """Draw character sprite and active effects."""
        frames = self.asset_mgr.get_character_frames(
            self.archetype, self.current_anim, self.facing_right
        )
        if not frames:
            return
            
        idx = min(self.frame_index, len(frames) - 1)
        frame_surf = frames[idx]
        
        # Position sprite such that frame's baseline (y=168 in 192x192 box) aligns with self.y
        draw_x = int(self.x - frame_surf.get_width() // 2)
        draw_y = int(self.y - 168)
        
        surface.blit(frame_surf, (draw_x, draw_y))
        
        # Draw special burst effect overlay if executing special
        if self.state == FighterState.SPECIAL and self.attack_phase == "active":
            eff = self.asset_mgr.get_effect("special_burst")
            eff_x = int(self.x + (60 if self.facing_right else -60) - eff.get_width() // 2)
            eff_y = int(self.y - 85 - eff.get_height() // 2)
            surface.blit(eff, (eff_x, eff_y))
