"""Automated Tests - Combat Mechanics, Hitboxes, Combos, and Blocking."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
import pygame
pygame.init()
pygame.display.set_mode((1280, 720))

from entities.fighter import Fighter, FighterState
from combat.attack import AttackRegistry, AttackData
from combat.combat_system import CombatSystem
from combat.combo_system import ComboTracker
from settings import GROUND_Y, SPECIAL_COST


class TestCombat(unittest.TestCase):
    def setUp(self) -> None:
        self.attacker = Fighter(1, "Attacker", "player", x=400.0, y=GROUND_Y, facing_right=True)
        self.defender = Fighter(2, "Defender", "rogue", x=460.0, y=GROUND_Y, facing_right=False)
        self.combat = CombatSystem()
        self.attack = AttackRegistry.get("light_punch")

    def test_attack_lifecycle_and_hitbox_timing(self) -> None:
        self.assertIsNotNone(self.attack)
        started = self.attacker.start_attack(self.attack)
        self.assertTrue(started)
        self.assertEqual(self.attacker.state, FighterState.ATTACK)

        # 1. During startup: active_hitbox is None
        self.attacker.update(self.attack.startup * 0.5)
        self.assertEqual(self.attacker.attack_phase, "startup")
        self.assertIsNone(self.attacker.active_hitbox)

        # 2. During active window: active_hitbox exists and is active
        self.attacker.update(self.attack.startup * 0.6)
        self.assertEqual(self.attacker.attack_phase, "active")
        self.assertIsNotNone(self.attacker.active_hitbox)
        self.assertTrue(self.attacker.active_hitbox.is_active)

        # 3. During recovery: active_hitbox is None again
        self.attacker.update(self.attack.active + 0.01)
        self.assertEqual(self.attacker.attack_phase, "recovery")
        self.assertIsNone(self.attacker.active_hitbox)

        # 4. End of recovery: returns to IDLE
        self.attacker.update(self.attack.recovery + 0.05)
        self.assertEqual(self.attacker.state, FighterState.IDLE)
        self.assertIsNone(self.attacker.current_attack)

    def test_single_hit_per_target_rule(self) -> None:
        self.attacker.start_attack(self.attack)
        # Advance into active window
        self.attacker.update(self.attack.startup + 0.02)
        initial_hp = self.defender.current_health

        # First frame of contact
        self.combat.update(1.0 / 60.0, self.attacker, self.defender)
        hp_after_first_hit = self.defender.current_health
        self.assertLess(hp_after_first_hit, initial_hp)

        # Second frame while still in active window
        self.combat.update(1.0 / 60.0, self.attacker, self.defender)
        # Health must NOT decrease again from the same attack instance!
        self.assertEqual(self.defender.current_health, hp_after_first_hit)

    def test_blocking_mitigation_and_facing_requirement(self) -> None:
        # Defender raises block facing the attacker
        self.defender.facing_right = False  # Attacker is at x=400, defender at x=460 facing left (towards attacker)
        self.defender.start_block()
        self.assertTrue(self.defender.is_blocking)

        dmg, was_blocked = self.defender.take_hit(
            damage=100.0,
            knockback=(100, 0),
            stun_duration=0.3,
            attacker_facing_right=True
        )
        self.assertTrue(was_blocked)
        # Damage should be reduced by 75% -> 25 damage taken
        self.assertEqual(dmg, 25.0)
        self.assertEqual(self.defender.current_health, 175.0)

        # Back turned block fails (facing same direction as attacker)
        self.defender.facing_right = True  # Back turned
        self.defender.start_block()
        dmg_unblocked, was_blocked_back = self.defender.take_hit(
            damage=100.0,
            knockback=(100, 0),
            stun_duration=0.3,
            attacker_facing_right=True
        )
        self.assertFalse(was_blocked_back)
        self.assertEqual(dmg_unblocked, 100.0)

    def test_combo_counter_and_timeout(self) -> None:
        combo = ComboTracker("Test")
        self.assertEqual(combo.combo_count, 0)
        self.assertFalse(combo.is_active)

        # Register hits
        combo.register_hit(15.0)
        combo.register_hit(20.0)
        self.assertEqual(combo.combo_count, 2)
        self.assertEqual(combo.combo_damage, 35.0)
        self.assertTrue(combo.is_active)

        # Advance timer past COMBO_TIMEOUT
        expired = combo.update(2.0)
        self.assertTrue(expired)
        self.assertEqual(combo.combo_count, 0)
        self.assertFalse(combo.is_active)

    def test_special_attack_energy_consumption(self) -> None:
        special_atk = AttackRegistry.get("special_attack")
        self.assertIsNotNone(special_atk)

        # Cannot cast with 0 energy
        self.attacker.current_energy = 0.0
        success = self.attacker.start_attack(special_atk)
        self.assertFalse(success)

        # Grant full energy -> casting succeeds and consumes energy
        self.attacker.current_energy = 100.0
        success_cast = self.attacker.start_attack(special_atk)
        self.assertTrue(success_cast)
        self.assertEqual(self.attacker.current_energy, 100.0 - SPECIAL_COST)
        self.assertEqual(self.attacker.state, FighterState.SPECIAL)


if __name__ == "__main__":
    unittest.main()
