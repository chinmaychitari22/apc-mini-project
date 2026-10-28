"""SHADOW CLASH - Player Controlled Shadow Warrior Entity.

Translates user input buffer and held keys into martial arts actions,
combos, jumps, blocks, and special moves.
"""

from __future__ import annotations
from typing import Optional
from entities.fighter import Fighter, FighterState
from combat.attack import AttackRegistry
from game.input_manager import InputManager
from settings import GROUND_Y


class PlayerFighter(Fighter):
    """Player controlled martial arts warrior."""

    def __init__(self, x: float = 380.0, y: float = GROUND_Y) -> None:
        super().__init__(
            entity_id=1,
            name="Shadow Warrior",
            archetype="player",
            x=x,
            y=y,
            facing_right=True,
            max_health=200.0,
            speed=320.0,
            is_player=True
        )
        self.input_mgr = InputManager.get_instance()

    def handle_input(self) -> None:
        """Process buffered inputs and held key states."""
        if not self.is_alive or self.state == FighterState.DEFEAT:
            return
            
        # 1. Check Special Attack Execution
        if self.input_mgr.consume_buffered_action("special"):
            sp_atk = AttackRegistry.get("special_attack")
            if sp_atk and self.start_attack(sp_atk):
                return
                
        # 2. Check Attack Inputs
        if self.is_grounded:
            is_crouching = self.input_mgr.is_action_held("crouch")
            
            # Crouching low attack
            if is_crouching and (self.input_mgr.consume_buffered_action("light_punch") or 
                                 self.input_mgr.consume_buffered_action("light_kick")):
                atk = AttackRegistry.get("crouch_attack")
                if atk and self.start_attack(atk):
                    return
                    
            # Heavy Punch
            if self.input_mgr.consume_buffered_action("heavy_punch"):
                atk = AttackRegistry.get("heavy_punch")
                if atk and self.start_attack(atk):
                    return
                    
            # Heavy Kick
            if self.input_mgr.consume_buffered_action("heavy_kick"):
                atk = AttackRegistry.get("heavy_kick")
                if atk and self.start_attack(atk):
                    return
                    
            # Light Punch
            if self.input_mgr.consume_buffered_action("light_punch"):
                atk = AttackRegistry.get("light_punch")
                if atk and self.start_attack(atk):
                    return
                    
            # Light Kick
            if self.input_mgr.consume_buffered_action("light_kick"):
                atk = AttackRegistry.get("light_kick")
                if atk and self.start_attack(atk):
                    return
        else:
            # Aerial Attacks
            if self.input_mgr.consume_buffered_action("light_punch") or self.input_mgr.consume_buffered_action("heavy_punch"):
                atk = AttackRegistry.get("jump_punch")
                if atk and self.start_attack(atk):
                    return
            if self.input_mgr.consume_buffered_action("light_kick") or self.input_mgr.consume_buffered_action("heavy_kick"):
                atk = AttackRegistry.get("jump_kick")
                if atk and self.start_attack(atk):
                    return

        # 3. Defensive Guard (Block)
        if self.input_mgr.is_action_held("block"):
            self.start_block()
        else:
            self.stop_block()

        # 4. Movement (Jump, Crouch, Left, Right)
        if not self.is_blocking and self.state not in (FighterState.ATTACK, FighterState.SPECIAL):
            if self.input_mgr.consume_buffered_action("jump") or self.input_mgr.is_action_just_pressed("jump"):
                self.jump()
            elif self.input_mgr.is_action_held("crouch"):
                self.crouch()
            else:
                self.uncrouch()
                # Horizontal movement
                move_dir = 0.0
                if self.input_mgr.is_action_held("right"):
                    move_dir += 1.0
                if self.input_mgr.is_action_held("left"):
                    move_dir -= 1.0
                self.move(move_dir)
