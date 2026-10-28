"""Automated Tests - Fighter and Movement Mechanics."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from entities.fighter import Fighter, FighterState
from settings import GROUND_Y, ARENA_LEFT, ARENA_RIGHT


class TestFighter(unittest.TestCase):
    def setUp(self) -> None:
        self.fighter = Fighter(
            entity_id=1,
            name="Test Warrior",
            archetype="player",
            x=600.0,
            y=GROUND_Y,
            facing_right=True,
            max_health=200.0,
            speed=300.0
        )

    def test_initial_state(self) -> None:
        self.assertEqual(self.fighter.state, FighterState.IDLE)
        self.assertEqual(self.fighter.current_health, 200.0)
        self.assertEqual(self.fighter.max_health, 200.0)
        self.assertTrue(self.fighter.is_grounded)
        self.assertTrue(self.fighter.is_alive)
        self.assertEqual(self.fighter.current_energy, 0.0)

    def test_horizontal_movement_boundaries(self) -> None:
        # Move left beyond boundary
        self.fighter.x = ARENA_LEFT + 10
        self.fighter.move(-1.0)
        self.fighter.update(1.0)  # Move far left
        self.assertGreaterEqual(self.fighter.x, ARENA_LEFT)

        # Move right beyond boundary
        self.fighter.x = ARENA_RIGHT - 10
        self.fighter.move(1.0)
        self.fighter.update(1.0)
        self.assertLessEqual(self.fighter.x, ARENA_RIGHT)

    def test_jump_and_gravity(self) -> None:
        # Grounded jump succeeds
        jumped = self.fighter.jump()
        self.assertTrue(jumped)
        self.assertFalse(self.fighter.is_grounded)
        self.assertEqual(self.fighter.state, FighterState.JUMP)
        self.assertLess(self.fighter.vy, 0.0)

        # Airborne jump prevented (no infinite jump)
        second_jump = self.fighter.jump()
        self.assertFalse(second_jump)

        # Update physics through apex and land back on ground
        for _ in range(60):
            self.fighter.update(1.0 / 60.0)
        
        self.assertTrue(self.fighter.is_grounded)
        self.assertEqual(self.fighter.y, GROUND_Y)

    def test_crouch_state(self) -> None:
        self.fighter.crouch()
        self.assertEqual(self.fighter.state, FighterState.CROUCH)
        # Hurtbox height lowers during crouch
        self.fighter.update(0.01)
        self.assertEqual(self.fighter.hurtbox.rect.height, 80)

        self.fighter.uncrouch()
        self.assertEqual(self.fighter.state, FighterState.IDLE)

    def test_defeat_behavior(self) -> None:
        # Taking fatal damage
        self.fighter.take_hit(
            damage=250.0,
            knockback=(100, 0),
            stun_duration=0.5,
            attacker_facing_right=True
        )
        self.assertEqual(self.fighter.current_health, 0.0)
        self.assertFalse(self.fighter.is_alive)
        self.assertEqual(self.fighter.state, FighterState.DEFEAT)

        # Defeated fighter cannot move, jump, or attack
        self.fighter.move(1.0)
        self.assertEqual(self.fighter.vx, 0.0)
        self.assertFalse(self.fighter.jump())
        self.assertEqual(self.fighter.state, FighterState.DEFEAT)


if __name__ == "__main__":
    unittest.main()
