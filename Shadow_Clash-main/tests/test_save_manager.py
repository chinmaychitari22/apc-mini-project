"""Automated Tests - Persistence, Schema Versioning, and Data Recovery."""

import unittest
from pathlib import Path
import tempfile
import shutil
import json

from systems.save_manager import SaveManager, get_default_save_data


class TestSaveManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.save_mgr = SaveManager(saves_dir=self.temp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_save_provides_defaults(self) -> None:
        self.assertFalse(self.save_mgr.has_save_file())
        data = self.save_mgr.load()
        self.assertEqual(data["coins"], 150)
        self.assertEqual(data["current_stage"], 1)
        self.assertEqual(data["schema_version"], 1)

    def test_save_and_load_roundtrip(self) -> None:
        self.save_mgr.data["coins"] = 750
        self.save_mgr.data["max_unlocked_stage"] = 4
        self.save_mgr.data["owned_weapons"].append("shadow_blade")
        
        saved = self.save_mgr.save()
        self.assertTrue(saved)
        self.assertTrue(self.save_mgr.has_save_file())

        # Load fresh instance from disk
        fresh_mgr = SaveManager(saves_dir=self.temp_dir)
        loaded = fresh_mgr.load()
        self.assertEqual(loaded["coins"], 750)
        self.assertEqual(loaded["max_unlocked_stage"], 4)
        self.assertIn("shadow_blade", loaded["owned_weapons"])

    def test_partial_or_missing_keys_safe_merge(self) -> None:
        # Save a file with missing subkeys
        partial_data = {
            "schema_version": 1,
            "coins": 999
            # Missing "upgrades", "statistics", "owned_weapons", etc.
        }
        with open(self.save_mgr.save_path, "w", encoding="utf-8") as f:
            json.dump(partial_data, f)

        loaded = self.save_mgr.load()
        self.assertEqual(loaded["coins"], 999)
        # Missing keys must be populated with defaults without crashing
        self.assertIn("upgrades", loaded)
        self.assertIn("statistics", loaded)
        self.assertEqual(loaded["max_unlocked_stage"], 1)

    def test_corrupted_save_recovery(self) -> None:
        # Create a valid backup file
        backup_data = get_default_save_data()
        backup_data["coins"] = 555
        with open(self.save_mgr.save_path.with_suffix(".bak"), "w", encoding="utf-8") as bf:
            json.dump(backup_data, bf)

        # Write corrupt bytes to main save file
        with open(self.save_mgr.save_path, "w", encoding="utf-8") as f:
            f.write("CORRUPT_INVALID_JSON_@#$%^&*")

        loaded = self.save_mgr.load()
        # Recovery from backup must succeed
        self.assertEqual(loaded["coins"], 555)


if __name__ == "__main__":
    unittest.main()
