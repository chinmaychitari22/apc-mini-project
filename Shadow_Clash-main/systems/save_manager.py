"""SHADOW CLASH - Save Manager and Local Persistence System.

Implements schema-versioned JSON persistence, atomic file writing to prevent
corruption, robust fallback handling for missing/invalid keys, and recovery mechanisms.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

from settings import SAVES_DIR

CURRENT_SCHEMA_VERSION = 1
SAVE_FILE_NAME = "shadow_clash_save.json"


def get_default_save_data() -> dict[str, Any]:
    """Provide guaranteed default player progression and system state."""
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "coins": 150,
        "experience": 0,
        "current_stage": 1,
        "max_unlocked_stage": 1,
        "equipped_weapon": "training_gloves",
        "owned_weapons": ["training_gloves"],
        "upgrades": {
            "strength": 0,
            "vitality": 0,
            "defense": 0,
            "special_efficiency": 0
        },
        "statistics": {
            "battles_won": 0,
            "battles_lost": 0,
            "total_damage_dealt": 0.0,
            "highest_combo": 0,
            "survival_best_wave": 0,
            "flawless_victories": 0
        },
        "unlocked_achievements": [],
        "audio_settings": {
            "music_volume": 0.65,
            "sfx_volume": 0.85,
            "is_muted": False
        }
    }


class SaveManager:
    """Manages reading, writing, validation, and recovery of save files."""

    def __init__(self, saves_dir: Path = SAVES_DIR) -> None:
        self.saves_dir = saves_dir
        self.save_path = self.saves_dir / SAVE_FILE_NAME
        self.data: dict[str, Any] = get_default_save_data()
        self.ensure_save_directory()

    def ensure_save_directory(self) -> None:
        self.saves_dir.mkdir(parents=True, exist_ok=True)

    def has_save_file(self) -> bool:
        """Check if an existing save file exists on disk."""
        return self.save_path.is_file()

    def load(self) -> dict[str, Any]:
        """Load save data from disk with schema validation and safe defaults merge."""
        if not self.has_save_file():
            self.data = get_default_save_data()
            return self.data

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                
            defaults = get_default_save_data()
            self.data = self._merge_defaults(loaded, defaults)
            return self.data
        except Exception as e:
            print(f"[SaveManager] Warning: Error loading save ({e}). Attempting backup recovery...")
            backup_path = self.save_path.with_suffix(".bak")
            if backup_path.is_file():
                try:
                    with open(backup_path, "r", encoding="utf-8") as bf:
                        loaded_b = json.load(bf)
                    self.data = self._merge_defaults(loaded_b, get_default_save_data())
                    print("[SaveManager] Successfully recovered from backup save!")
                    return self.data
                except Exception as be:
                    print(f"[SaveManager] Backup recovery also failed: {be}")

            self.data = get_default_save_data()
            return self.data

    def _merge_defaults(self, source: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
        """Recursively merge loaded data over safe defaults, preserving valid fields."""
        merged = dict(defaults)
        for k, v in source.items():
            if k in defaults and isinstance(defaults[k], dict) and isinstance(v, dict):
                merged[k] = self._merge_defaults(v, defaults[k])
            elif k in defaults and isinstance(defaults[k], list) and isinstance(v, list):
                merged[k] = list(v)
            elif k in defaults:
                merged[k] = v
        return merged

    def save(self) -> bool:
        """Atomic write to temporary file followed by replacement to prevent file corruption."""
        self.ensure_save_directory()
        temp_path = self.save_path.with_suffix(".tmp")
        backup_path = self.save_path.with_suffix(".bak")

        try:
            # 1. Write to temp file
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            # 2. Update backup if main file already exists
            if self.save_path.is_file():
                try:
                    if backup_path.is_file():
                        backup_path.unlink()
                    self.save_path.replace(backup_path)
                except Exception:
                    pass

            # 3. Replace target with temp file
            temp_path.replace(self.save_path)
            return True
        except Exception as e:
            print(f"[SaveManager] Failed to save game: {e}")
            if temp_path.is_file():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            return False

    def reset_save(self) -> None:
        """Reset save data to factory defaults."""
        self.data = get_default_save_data()
        self.save()
