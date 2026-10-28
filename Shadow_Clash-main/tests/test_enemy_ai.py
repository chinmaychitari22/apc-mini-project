"""Automated Tests - Enemy AI Decision Making and Boss Phases."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from entities.fighter import Fighter, FighterState
from entities.enemy import EnemyFighter
from ai.enemy_controller import EnemyController
from settings import GROUND_Y


class TestEnemyAI(unittest.TestCase):
    def setUp(self) -> None:
        self.player = Fighter(1, "Player", "player", x=300.0, y=GROUND_Y, facing_right=True)
        self.enemy = EnemyFighter(archetype_key="rogue", x=800.0, y=GROUND_Y)
        self.ai = EnemyController(self.enemy)

    def test_approach_behavior_when_far(self) -> None:
        # Distance is 500px (far beyond preferred distance ~85px)
        self.ai.decision_timer = 0.0  # Force immediate decision
        self.ai.update(0.01, self.player)
        # Enemy must move towards player (negative X direction because enemy x=800, player x=300)
        self.assertLess(self.enemy.vx, 0.0)

    def test_attack_execution_in_range(self) -> None:
        # Position enemy in close range (x=380, distance 80px)
        self.enemy.x = 380.0
        self.ai.decision_timer = 0.0
        self.ai.aggression = 1.0  # Force attack choice

        self.ai.update(0.01, self.player)
        # Enemy should trigger an attack
        self.assertIn(self.enemy.state, (FighterState.ATTACK, FighterState.SPECIAL))
        self.assertIsNotNone(self.enemy.current_attack)

    def test_boss_phase_transitions(self) -> None:
        boss = EnemyFighter(archetype_key="shadow_master", x=800.0, y=GROUND_Y)
        self.assertTrue(boss.is_boss)
        self.assertEqual(boss.current_phase, 1)

        # Drop health to 40% (below 50% threshold)
        boss.current_health = boss.max_health * 0.40
        new_phase = boss.check_boss_phase_transition()
        self.assertEqual(new_phase, 2)
        self.assertEqual(boss.current_phase, 2)

        # Drop health to 15% (below 25% threshold)
        boss.current_health = boss.max_health * 0.15
        final_phase = boss.check_boss_phase_transition()
        self.assertEqual(final_phase, 3)
        self.assertEqual(boss.current_phase, 3)

    def test_defeated_enemy_stops_acting(self) -> None:
        self.enemy.current_health = 0.0
        self.enemy.set_state(FighterState.DEFEAT)
        self.ai.decision_timer = 0.0

        self.ai.update(0.05, self.player)
        self.assertEqual(self.enemy.vx, 0.0)
        self.assertEqual(self.enemy.state, FighterState.DEFEAT)


if __name__ == "__main__":
    unittest.main()
