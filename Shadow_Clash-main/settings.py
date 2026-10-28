"""SHADOW CLASH - Global Configuration and Settings.

Defines display resolutions, physics constants, combat tuning, color palette,
audio configuration, and default key bindings.
"""

from __future__ import annotations
import os
from pathlib import Path
import pygame

# Project Root & Directory Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
SAVES_DIR = BASE_DIR / "saves"

CHARACTERS_ASSETS_DIR = ASSETS_DIR / "characters"
ANIMATIONS_ASSETS_DIR = ASSETS_DIR / "animations"
BACKGROUNDS_ASSETS_DIR = ASSETS_DIR / "backgrounds"
ARENAS_ASSETS_DIR = ASSETS_DIR / "arenas"
EFFECTS_ASSETS_DIR = ASSETS_DIR / "effects"
UI_ASSETS_DIR = ASSETS_DIR / "ui"
ICONS_ASSETS_DIR = ASSETS_DIR / "icons"
AUDIO_ASSETS_DIR = ASSETS_DIR / "audio"
FONTS_ASSETS_DIR = ASSETS_DIR / "fonts"

# Display & Window
LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 720
TARGET_FPS = 60
WINDOW_TITLE = "SHADOW CLASH - Martial Arts Silhouette"

# Physics & World Space
GRAVITY = 2100.0            # Pixels per second squared
GROUND_Y = 580              # Baseline ground elevation for fighter feet
ARENA_LEFT = 70             # Left boundary in logical coordinates
ARENA_RIGHT = 1210          # Right boundary in logical coordinates

# Combat System Configuration
MAX_ENERGY = 100.0
ENERGY_PER_HIT_DEALT = 14.0
ENERGY_PER_HIT_TAKEN = 8.0
ENERGY_PASSIVE_REGEN = 4.0   # Energy regenerated per second passively
SPECIAL_COST = 60.0          # Energy cost for Shadow Burst
COMBO_TIMEOUT = 1.7          # Seconds before combo counter resets

# Blocking Parameters
BLOCK_DAMAGE_REDUCTION = 0.75  # 75% damage blocked
BLOCK_KNOCKBACK_FACTOR = 0.35  # Knockback reduced to 35%
GUARD_BREAK_THRESHOLD = 3      # Consecutive blocked heavy attacks break guard

# Color Palette (Dark Silhouette Martial Arts Aesthetic)
COLOR_BLACK = (10, 10, 15)
COLOR_SHADOW = (18, 20, 28)
COLOR_DARK_CHARCOAL = (28, 32, 42)
COLOR_INDIGO_NIGHT = (35, 42, 65)
COLOR_MIDNIGHT_BLUE = (20, 26, 48)
COLOR_MOONLIGHT = (220, 232, 245)
COLOR_SILVER_MUTED = (160, 172, 190)

# Accents & FX Colors
COLOR_CRIMSON = (215, 38, 56)
COLOR_CRIMSON_DARK = (130, 18, 32)
COLOR_CRIMSON_GLOW = (255, 75, 95)
COLOR_VIOLET = (142, 54, 218)
COLOR_VIOLET_GLOW = (188, 102, 255)
COLOR_CYAN_ENERGY = (48, 204, 245)
COLOR_AMBER_GOLD = (235, 182, 45)
COLOR_HEALTH_GREEN = (46, 204, 113)
COLOR_HEALTH_DELAY = (231, 76, 60)
COLOR_WHITE = (255, 255, 255)

# Audio Settings
DEFAULT_MUSIC_VOLUME = 0.65
DEFAULT_SFX_VOLUME = 0.85

# Default Controls Mapping
DEFAULT_CONTROLS = {
    "left": [pygame.K_a, pygame.K_LEFT],
    "right": [pygame.K_d, pygame.K_RIGHT],
    "jump": [pygame.K_w, pygame.K_UP],
    "crouch": [pygame.K_s, pygame.K_DOWN],
    "light_punch": [pygame.K_j],
    "heavy_punch": [pygame.K_u],
    "light_kick": [pygame.K_k],
    "heavy_kick": [pygame.K_i],
    "block": [pygame.K_l, pygame.K_SPACE],
    "special": [pygame.K_o, pygame.K_q],
    "pause": [pygame.K_ESCAPE, pygame.K_p],
}
