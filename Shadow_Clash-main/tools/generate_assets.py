"""SHADOW CLASH - Procedural & Vector Graphic Asset Generator.

Generates:
1. Character animation sprite sheets for 6 distinct fighter archetypes:
   - Player (Shadow Warrior)
   - Rogue (Basic enemy)
   - Swift Fang (Agile enemy)
   - Iron Guard (Defensive enemy)
   - Night Reaper (Advanced enemy)
   - Shadow Master (Final boss)
2. 3 Complete Multi-Layered Fighting Arenas:
   - Abandoned Dojo
   - Crimson Forest
   - Ruined Temple
3. Visual Combat Effects (Impacts, Barriers, Sparks, Nova)
4. UI Assets (Logo, Menu Background, Buttons, Bars, Weapon Icons, Portraits, Currency)
5. Comprehensive Asset Manifest (assets_manifest.json)
"""

from __future__ import annotations
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
CHAR_DIR = ASSETS_DIR / "characters"
ARENAS_DIR = ASSETS_DIR / "arenas"
EFFECTS_DIR = ASSETS_DIR / "effects"
UI_DIR = ASSETS_DIR / "ui"
ICONS_DIR = ASSETS_DIR / "icons"

FRAME_WIDTH = 192
FRAME_HEIGHT = 192
BASELINE_Y = 168  # Ground contact line for feet inside 192x192 box

# Color definitions
C_BLACK = (12, 12, 18, 255)
C_SHADOW_CORE = (22, 24, 34, 255)
C_SHADOW_HIGHLIGHT = (45, 52, 70, 255)
C_CLEAR = (0, 0, 0, 0)


def create_gradient_surface(width: int, height: int, top_color: tuple, bottom_color: tuple) -> Image.Image:
    """Create a vertical gradient image."""
    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    top = np.array(top_color, dtype=np.float32)
    bottom = np.array(bottom_color, dtype=np.float32)
    for y in range(height):
        factor = y / max(1, height - 1)
        col = (top * (1.0 - factor) + bottom * factor).astype(np.uint8)
        base.paste(Image.new("RGBA", (width, 1), tuple(col)), (0, y))
    return base


# ==========================================
# 1. CHARACTER SPRITE SHEET GENERATOR
# ==========================================

ARCHETYPES = {
    "player": {
        "scale": 1.0,
        "width_scale": 1.0,
        "eye_color": (100, 220, 255, 255),  # Cyan
        "accent_color": (220, 45, 60, 255), # Crimson sash
        "head_style": "headband",
        "weapon_type": "fists",
        "cloak": False,
    },
    "rogue": {
        "scale": 0.95,
        "width_scale": 0.9,
        "eye_color": (255, 180, 50, 255),  # Amber
        "accent_color": (180, 40, 40, 255), # Red cloth
        "head_style": "mask",
        "weapon_type": "daggers",
        "cloak": False,
    },
    "swift_fang": {
        "scale": 0.96,
        "width_scale": 0.88,
        "eye_color": (210, 100, 255, 255), # Violet
        "accent_color": (150, 60, 230, 255),# Long violet scarf
        "head_style": "ninja_hood",
        "weapon_type": "claws",
        "cloak": False,
    },
    "iron_guard": {
        "scale": 1.08,
        "width_scale": 1.25,
        "eye_color": (80, 230, 140, 255),  # Jade
        "accent_color": (220, 180, 50, 255),# Brass armor trim
        "head_style": "samurai_crest",
        "weapon_type": "heavy_gauntlets",
        "cloak": False,
    },
    "night_reaper": {
        "scale": 1.05,
        "width_scale": 1.0,
        "eye_color": (255, 60, 60, 255),   # Blood red
        "accent_color": (140, 30, 80, 255), # Dark wine shroud
        "head_style": "cowl",
        "weapon_type": "sickles",
        "cloak": True,
    },
    "shadow_master": {
        "scale": 1.18,
        "width_scale": 1.3,
        "eye_color": (255, 40, 40, 255),   # Glowing Demonic Crimson
        "accent_color": (160, 20, 40, 255), # Dark Warlord Mantle
        "head_style": "horned_helm",
        "weapon_type": "dual_blades",
        "cloak": True,
    },
}

# 17 Animation states with frame counts and loop settings
ANIMATION_SPECS = {
    "idle": {"frames": 6, "duration": 0.14, "loop": True},
    "walk": {"frames": 6, "duration": 0.12, "loop": True},
    "run": {"frames": 6, "duration": 0.10, "loop": True},
    "jump": {"frames": 4, "duration": 0.12, "loop": False},
    "fall": {"frames": 3, "duration": 0.12, "loop": True},
    "land": {"frames": 3, "duration": 0.08, "loop": False},
    "crouch": {"frames": 3, "duration": 0.10, "loop": False},
    "light_punch": {"frames": 5, "duration": 0.07, "loop": False},
    "heavy_punch": {"frames": 6, "duration": 0.09, "loop": False},
    "light_kick": {"frames": 5, "duration": 0.08, "loop": False},
    "heavy_kick": {"frames": 6, "duration": 0.10, "loop": False},
    "crouch_attack": {"frames": 5, "duration": 0.08, "loop": False},
    "jump_punch": {"frames": 4, "duration": 0.10, "loop": False},
    "jump_kick": {"frames": 4, "duration": 0.10, "loop": False},
    "block": {"frames": 3, "duration": 0.10, "loop": False},
    "hit": {"frames": 4, "duration": 0.08, "loop": False},
    "knockback": {"frames": 6, "duration": 0.10, "loop": False},
    "special": {"frames": 8, "duration": 0.09, "loop": False},
    "victory": {"frames": 6, "duration": 0.14, "loop": True},
    "defeat": {"frames": 6, "duration": 0.15, "loop": False},
}


def draw_limb(draw: ImageDraw.ImageDraw, p1: tuple[float, float], p2: tuple[float, float], 
              thickness: float, color: tuple = C_BLACK) -> None:
    """Draw a smooth rounded martial arts limb."""
    draw.line([p1, p2], fill=color, width=int(thickness))
    r = thickness / 2.0
    draw.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=color)
    draw.ellipse([p2[0] - r, p2[1] - r, p2[0] + r, p2[1] + r], fill=color)


def draw_character_frame(arch: dict, anim_name: str, frame_idx: int, num_frames: int) -> Image.Image:
    """Render a single character frame with distinct silhouette martial arts anatomy."""
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), C_CLEAR)
    draw = ImageDraw.Draw(img)
    
    scale = arch["scale"]
    w_scale = arch["width_scale"]
    cx = FRAME_WIDTH / 2.0
    by = BASELINE_Y
    
    t = frame_idx / max(1, num_frames - 1)
    
    # Baseline anatomy coordinates relative to ground (facing RIGHT)
    # Default idle stance
    hip_h = 76.0 * scale
    chest_h = 108.0 * scale
    head_h = 132.0 * scale
    
    offset_x = 0.0
    offset_y = 0.0
    torso_tilt = 0.0
    
    # Procedural Joint Angles & Displacements per Animation
    knee_l = (cx - 18 * w_scale, by - hip_h * 0.5)
    foot_l = (cx - 24 * w_scale, by)
    knee_r = (cx + 14 * w_scale, by - hip_h * 0.48)
    foot_r = (cx + 26 * w_scale, by)
    
    hip = (cx, by - hip_h)
    chest = (cx + 4 * w_scale, by - chest_h)
    head = (cx + 6 * w_scale, by - head_h)
    
    # Default guard arm positions
    elbow_l = (cx - 12 * w_scale, by - chest_h + 10)
    hand_l = (cx + 16 * w_scale, by - chest_h + 2)
    elbow_r = (cx + 20 * w_scale, by - chest_h + 12)
    hand_r = (cx + 34 * w_scale, by - chest_h)
    
    if anim_name == "idle":
        breath = math.sin(t * math.pi * 2) * 2.5
        hip = (cx, by - hip_h + breath * 0.5)
        chest = (cx + 3 * w_scale, by - chest_h + breath)
        head = (cx + 5 * w_scale, by - head_h + breath)
        hand_r = (cx + 32 * w_scale, by - chest_h + breath * 0.7)
        hand_l = (cx + 14 * w_scale, by - chest_h + 4 + breath * 0.7)
        
    elif anim_name == "walk":
        phase = t * math.pi * 2
        bob = math.sin(phase * 2) * 3.0
        hip = (cx, by - hip_h + abs(bob))
        chest = (cx + 5 * w_scale, by - chest_h + abs(bob))
        head = (cx + 8 * w_scale, by - head_h + abs(bob))
        
        step_l = math.sin(phase) * 26.0 * w_scale
        step_r = math.sin(phase + math.pi) * 26.0 * w_scale
        lift_l = max(0.0, math.cos(phase)) * 14.0
        lift_r = max(0.0, math.cos(phase + math.pi)) * 14.0
        
        foot_l = (cx - 10 + step_l, by - lift_l)
        foot_r = (cx + 10 + step_r, by - lift_r)
        knee_l = (cx - 8 + step_l * 0.6, by - hip_h * 0.5 - lift_l * 0.5)
        knee_r = (cx + 8 + step_r * 0.6, by - hip_h * 0.5 - lift_r * 0.5)
        
        # Arm swing
        hand_l = (cx + math.sin(phase + math.pi) * 20 * w_scale, by - chest_h + 10)
        hand_r = (cx + math.sin(phase) * 22 * w_scale, by - chest_h + 8)

    elif anim_name == "run":
        phase = t * math.pi * 2
        hip = (cx + 10, by - hip_h + 6)
        chest = (cx + 22 * w_scale, by - chest_h + 12)
        head = (cx + 28 * w_scale, by - head_h + 14)
        
        step_l = math.sin(phase) * 38.0 * w_scale
        step_r = math.sin(phase + math.pi) * 38.0 * w_scale
        lift_l = max(0.0, math.cos(phase)) * 22.0
        lift_r = max(0.0, math.cos(phase + math.pi)) * 22.0
        
        foot_l = (cx + step_l, by - lift_l)
        foot_r = (cx + step_r, by - lift_r)
        knee_l = (cx + step_l * 0.7, by - hip_h * 0.45 - lift_l * 0.7)
        knee_r = (cx + step_r * 0.7, by - hip_h * 0.45 - lift_r * 0.7)
        
        hand_l = (cx + math.sin(phase + math.pi) * 32 * w_scale, by - chest_h + 14)
        hand_r = (cx + math.sin(phase) * 36 * w_scale, by - chest_h + 10)

    elif anim_name == "jump":
        jump_y = -35.0 * math.sin(t * math.pi * 0.75)
        hip = (cx, by - hip_h + jump_y)
        chest = (cx + 6, by - chest_h + jump_y)
        head = (cx + 8, by - head_h + jump_y)
        # Tucked knees
        knee_l = (cx - 16, hip[1] + 25)
        foot_l = (cx - 8, hip[1] + 48)
        knee_r = (cx + 16, hip[1] + 28)
        foot_r = (cx + 12, hip[1] + 52)
        hand_l = (cx - 20, chest[1] - 8)
        hand_r = (cx + 26, chest[1] - 14)

    elif anim_name == "fall":
        fall_y = -18.0
        hip = (cx, by - hip_h + fall_y)
        chest = (cx + 4, by - chest_h + fall_y)
        head = (cx + 6, by - head_h + fall_y)
        knee_l = (cx - 14, hip[1] + 35)
        foot_l = (cx - 18, hip[1] + 68)
        knee_r = (cx + 14, hip[1] + 38)
        foot_r = (cx + 18, hip[1] + 70)
        hand_l = (cx - 28, chest[1] - 12)
        hand_r = (cx + 28, chest[1] - 16)

    elif anim_name == "land":
        squat = (1.0 - t) * 22.0
        hip = (cx, by - hip_h + squat)
        chest = (cx + 8, by - chest_h + squat * 1.2)
        head = (cx + 10, by - head_h + squat * 1.3)
        knee_l = (cx - 26 * w_scale, by - 24)
        knee_r = (cx + 28 * w_scale, by - 22)
        foot_l = (cx - 28 * w_scale, by)
        foot_r = (cx + 30 * w_scale, by)
        hand_l = (cx - 10, by - 28)
        hand_r = (cx + 18, by - 24)

    elif anim_name == "crouch":
        drop = 30.0 * min(1.0, t * 1.5)
        hip = (cx - 6, by - hip_h + drop)
        chest = (cx + 8, by - chest_h + drop * 1.2)
        head = (cx + 12, by - head_h + drop * 1.3)
        knee_l = (cx - 24 * w_scale, by - 20)
        knee_r = (cx + 24 * w_scale, by - 18)
        foot_l = (cx - 26 * w_scale, by)
        foot_r = (cx + 28 * w_scale, by)
        hand_l = (cx + 12, by - 55)
        hand_r = (cx + 28, by - 50)

    elif anim_name == "light_punch":
        # Jab: fast extension in middle frames
        progress = math.sin(t * math.pi)
        chest = (cx + 6 * w_scale + progress * 8, by - chest_h)
        head = (cx + 8 * w_scale + progress * 6, by - head_h)
        elbow_r = (cx + 30 * w_scale + progress * 24, by - chest_h + 6)
        hand_r = (cx + 36 * w_scale + progress * 58, by - chest_h + 2)
        # Left hand guards chin
        elbow_l = (cx - 8, by - chest_h + 12)
        hand_l = (cx + 14, by - chest_h)

    elif anim_name == "heavy_punch":
        # Lunging power straight punch
        if t < 0.4:  # Wind up
            wind = t / 0.4
            chest = (cx - 8 * wind, by - chest_h + 4)
            elbow_r = (cx - 18 * wind, by - chest_h + 10)
            hand_r = (cx - 22 * wind, by - chest_h + 8)
        else:  # Power lunge
            strike = math.sin((t - 0.4) / 0.6 * math.pi)
            chest = (cx + 18 * strike, by - chest_h + 6)
            head = (cx + 22 * strike, by - head_h + 6)
            elbow_r = (cx + 42 * strike + 20, by - chest_h + 8)
            hand_r = (cx + 78 * strike + 22, by - chest_h + 4)
            foot_r = (cx + 38 * w_scale + strike * 12, by)

    elif anim_name == "light_kick":
        # Snappy front mid kick
        lift = math.sin(t * math.pi)
        hip = (cx - 8 * lift, by - hip_h)
        knee_r = (cx + 24 + lift * 32, by - hip_h * 0.7 - lift * 28)
        foot_r = (cx + 28 + lift * 65, by - hip_h * 0.7 - lift * 25)
        # Left leg posts firmly
        knee_l = (cx - 18, by - hip_h * 0.48)
        foot_l = (cx - 22, by)
        hand_l = (cx - 10, by - chest_h + 12)
        hand_r = (cx + 18, by - chest_h + 18)

    elif anim_name == "heavy_kick":
        # High spinning roundhouse kick
        k_prog = math.sin(t * math.pi)
        hip = (cx - 4, by - hip_h - k_prog * 8)
        chest = (cx - 12 * k_prog, by - chest_h)
        head = (cx - 14 * k_prog, by - head_h)
        knee_r = (cx + 28 * w_scale + k_prog * 36, by - chest_h - k_prog * 12)
        foot_r = (cx + 34 * w_scale + k_prog * 75, by - chest_h - k_prog * 18)
        knee_l = (cx - 14, by - hip_h * 0.5)
        foot_l = (cx - 16, by)
        hand_l = (cx - 24, by - chest_h + 14)
        hand_r = (cx + 6, by - chest_h + 22)

    elif anim_name == "crouch_attack":
        # Low sweep kick along the floor
        sweep = math.sin(t * math.pi)
        hip = (cx - 10, by - hip_h + 34)
        chest = (cx + 6, by - chest_h + 42)
        head = (cx + 8, by - head_h + 44)
        knee_l = (cx - 28, by - 16)
        foot_l = (cx - 26, by)
        knee_r = (cx + 22 + sweep * 30, by - 14)
        foot_r = (cx + 32 + sweep * 68, by - 6)
        hand_l = (cx - 4, by - 22)
        hand_r = (cx + 20, by - 24)

    elif anim_name == "jump_punch":
        hip = (cx, by - hip_h - 26)
        chest = (cx + 12, by - chest_h - 26)
        head = (cx + 16, by - head_h - 24)
        knee_l = (cx - 14, hip[1] + 28)
        foot_l = (cx - 8, hip[1] + 52)
        knee_r = (cx + 12, hip[1] + 32)
        foot_r = (cx + 18, hip[1] + 55)
        hand_r = (cx + 56 * w_scale, chest[1] + 14)

    elif anim_name == "jump_kick":
        hip = (cx - 10, by - hip_h - 28)
        chest = (cx - 4, by - chest_h - 26)
        head = (cx, by - head_h - 24)
        knee_l = (cx - 20, hip[1] + 24)
        foot_l = (cx - 14, hip[1] + 48)
        knee_r = (cx + 26, hip[1] + 12)
        foot_r = (cx + 72 * w_scale, hip[1] + 18)
        hand_l = (cx - 22, chest[1] + 10)
        hand_r = (cx + 12, chest[1] + 16)

    elif anim_name == "block":
        # Tight raised guard
        hip = (cx - 8, by - hip_h + 4)
        chest = (cx - 4, by - chest_h + 6)
        head = (cx - 2, by - head_h + 6)
        # Crossed forearms in front of face/chest
        elbow_l = (cx + 12 * w_scale, by - chest_h + 12)
        hand_l = (cx + 24 * w_scale, by - head_h + 14)
        elbow_r = (cx + 16 * w_scale, by - chest_h + 10)
        hand_r = (cx + 26 * w_scale, by - head_h + 10)

    elif anim_name == "hit":
        # Torso and head snapped back
        recoil = math.sin(t * math.pi) * 16.0
        hip = (cx - recoil * 0.6, by - hip_h + 4)
        chest = (cx - recoil * 1.2, by - chest_h + 6)
        head = (cx - recoil * 1.8, by - head_h + 8)
        hand_l = (cx - recoil - 12, by - chest_h + 20)
        hand_r = (cx - recoil + 14, by - chest_h + 24)

    elif anim_name == "knockback":
        # Flying back and sliding
        kb = t * 32.0
        lift = math.sin(t * math.pi) * 18.0
        hip = (cx - kb, by - hip_h - lift + 12 * t)
        chest = (cx - kb - 18, by - chest_h - lift + 18 * t)
        head = (cx - kb - 24, by - head_h - lift + 22 * t)
        knee_l = (hip[0] + 18, hip[1] + 28)
        foot_l = (hip[0] + 34, by - max(0.0, lift - 6))
        knee_r = (hip[0] + 12, hip[1] + 24)
        foot_r = (hip[0] + 26, by)
        hand_l = (chest[0] - 18, chest[1] + 14)
        hand_r = (chest[0] + 12, chest[1] + 18)

    elif anim_name == "special":
        # Shadow burst power surge
        if t < 0.4:  # Gather energy
            s = t / 0.4
            hip = (cx - 4, by - hip_h + 8 * s)
            chest = (cx + 4, by - chest_h + 10 * s)
            head = (cx + 6, by - head_h + 10 * s)
            hand_l = (cx + 12, by - chest_h + 24)
            hand_r = (cx + 18, by - chest_h + 22)
        else:  # Detonate forward
            rel = (t - 0.4) / 0.6
            burst = math.sin(rel * math.pi)
            chest = (cx + 20 * burst, by - chest_h + 6)
            head = (cx + 24 * burst, by - head_h + 6)
            hand_l = (cx + 62 * burst + 20, by - chest_h + 6)
            hand_r = (cx + 74 * burst + 24, by - chest_h + 2)

    elif anim_name == "victory":
        # Kata triumph flourish
        hip = (cx, by - hip_h - 2)
        chest = (cx, by - chest_h - 4)
        head = (cx, by - head_h - 6)
        hand_l = (cx - 24 * w_scale, by - chest_h - 12)
        hand_r = (cx + 24 * w_scale, by - chest_h - 12)
        knee_l = (cx - 22 * w_scale, by - hip_h * 0.48)
        foot_l = (cx - 26 * w_scale, by)
        knee_r = (cx + 22 * w_scale, by - hip_h * 0.48)
        foot_r = (cx + 26 * w_scale, by)

    elif anim_name == "defeat":
        # Falling to knees/ground
        d = min(1.0, t * 1.2)
        hip = (cx - 10 * d, by - hip_h + 46 * d)
        chest = (cx - 16 * d, by - chest_h + 65 * d)
        head = (cx - 22 * d, by - head_h + 85 * d)
        knee_l = (cx - 24 * d, by - 12)
        foot_l = (cx - 36 * d, by)
        knee_r = (cx + 8 * d, by - 10)
        foot_r = (cx - 12 * d, by)
        hand_l = (cx - 28 * d, by - 8)
        hand_r = (cx - 8 * d, by - 10)

    # ==========================
    # RENDER SILHOUETTE BODY
    # ==========================
    limb_thick = 9.0 * scale
    torso_thick = 16.0 * scale * w_scale
    head_rad = 12.0 * scale
    
    # Back leg
    draw_limb(draw, hip, knee_l, limb_thick * 0.95, C_SHADOW_CORE)
    draw_limb(draw, knee_l, foot_l, limb_thick * 0.85, C_SHADOW_CORE)
    # Foot paddle
    draw.polygon([foot_l, (foot_l[0] + 12 * w_scale, foot_l[1]), (foot_l[0] + 6, foot_l[1] - 5)], fill=C_SHADOW_CORE)

    # Cloak / Cape (if archetype has one)
    if arch.get("cloak", False):
        cloak_pts = [
            (chest[0] - 10 * w_scale, chest[1]),
            (hip[0] - 16 * w_scale, hip[1]),
            (hip[0] - 32 * w_scale - (10 if anim_name in ["run", "walk"] else 0), by - 15),
            (chest[0] + 6 * w_scale, chest[1] + 10)
        ]
        draw.polygon(cloak_pts, fill=(18, 16, 24, 255))

    # Torso (Muscular martial taper)
    draw_limb(draw, hip, chest, torso_thick, C_BLACK)
    
    # Waist sash / belt accent
    sash_y = hip[1] - 8
    draw.rectangle([hip[0] - 12 * w_scale, sash_y - 3, hip[0] + 12 * w_scale, sash_y + 3], fill=arch["accent_color"])
    # Trailing sash ribbons
    draw.polygon([
        (hip[0] - 8 * w_scale, sash_y),
        (hip[0] - 16 * w_scale, sash_y + 22),
        (hip[0] - 10 * w_scale, sash_y + 20)
    ], fill=arch["accent_color"])

    # Front leg
    draw_limb(draw, hip, knee_r, limb_thick, C_BLACK)
    draw_limb(draw, knee_r, foot_r, limb_thick * 0.9, C_BLACK)
    draw.polygon([foot_r, (foot_r[0] + 14 * w_scale, foot_r[1]), (foot_r[0] + 8, foot_r[1] - 6)], fill=C_BLACK)

    # Back arm
    draw_limb(draw, chest, elbow_l, limb_thick * 0.85, C_SHADOW_CORE)
    draw_limb(draw, elbow_l, hand_l, limb_thick * 0.75, C_SHADOW_CORE)

    # Head
    draw.ellipse([head[0] - head_rad * 0.9, head[1] - head_rad * 1.1, 
                  head[0] + head_rad * 0.9, head[1] + head_rad * 0.9], fill=C_BLACK)

    # Head adornments based on archetype
    head_style = arch["head_style"]
    if head_style == "headband":
        # Martial arts headband with trailing ties
        hb_y = head[1] - head_rad * 0.2
        draw.rectangle([head[0] - head_rad, hb_y - 2, head[0] + head_rad, hb_y + 3], fill=arch["accent_color"])
        draw.polygon([(head[0] - head_rad, hb_y), (head[0] - head_rad - 16, hb_y + 10), (head[0] - head_rad - 12, hb_y + 14)], fill=arch["accent_color"])
    elif head_style == "horned_helm":
        # Horns for Shadow Master boss
        draw.polygon([(head[0] - 6, head[1] - 10), (head[0] - 16, head[1] - 28), (head[0] - 2, head[1] - 14)], fill=C_BLACK)
        draw.polygon([(head[0] + 6, head[1] - 10), (head[0] + 18, head[1] - 26), (head[0] + 2, head[1] - 14)], fill=C_BLACK)
    elif head_style == "samurai_crest":
        # Golden crescent crest on kabuto
        draw.arc([head[0] - 16, head[1] - 22, head[0] + 16, head[1] - 4], 180, 360, fill=arch["accent_color"], width=3)
    elif head_style == "ninja_hood":
        # Trailing long scarf for Swift Fang
        scarf_pts = [
            (head[0] - 8, head[1] + 8),
            (head[0] - 28, head[1] + 14 + math.sin(t * 6) * 6),
            (head[0] - 44, head[1] + 22 + math.sin(t * 6) * 10),
            (head[0] - 22, head[1] + 18)
        ]
        draw.polygon(scarf_pts, fill=arch["accent_color"])

    # Glowing eyes (Dark silhouette martial aesthetic)
    eye_c = arch["eye_color"]
    eye_x = head[0] + head_rad * 0.35
    eye_y = head[1] - head_rad * 0.15
    draw.ellipse([eye_x - 3, eye_y - 1.5, eye_x + 3, eye_y + 1.5], fill=eye_c)
    # Eye flare
    draw.line([(eye_x - 1, eye_y), (eye_x + 5, eye_y)], fill=(255, 255, 255, 255), width=1)

    # Front arm
    draw_limb(draw, chest, elbow_r, limb_thick * 0.9, C_BLACK)
    draw_limb(draw, elbow_r, hand_r, limb_thick * 0.8, C_BLACK)

    # Weapons attached to hand
    w_type = arch["weapon_type"]
    if w_type == "daggers":
        draw.line([hand_r, (hand_r[0] + 18, hand_r[1] - 6)], fill=(180, 195, 215, 255), width=3)
        draw.line([hand_l, (hand_l[0] + 14, hand_l[1] - 4)], fill=(150, 165, 185, 255), width=2)
    elif w_type == "claws":
        for off in [-3, 0, 3]:
            draw.line([(hand_r[0], hand_r[1] + off), (hand_r[0] + 16, hand_r[1] + off - 2)], fill=arch["eye_color"], width=2)
    elif w_type == "dual_blades":
        draw.line([hand_r, (hand_r[0] + 34, hand_r[1] - 12)], fill=(225, 235, 255, 255), width=4)
        draw.line([(hand_r[0] - 4, hand_r[1] + 2), (hand_r[0] + 6, hand_r[1] - 2)], fill=arch["accent_color"], width=5)
    elif w_type == "sickles":
        draw.arc([hand_r[0], hand_r[1] - 20, hand_r[0] + 28, hand_r[1] + 12], 240, 60, fill=(210, 220, 235, 255), width=3)

    return img


def generate_all_character_sprites() -> dict:
    """Generate all sprite sheets for all archetypes and return manifest info."""
    manifest = {}
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    
    for arch_name, arch_data in ARCHETYPES.items():
        print(f"Generating sprite sheets for {arch_name}...")
        arch_manifest = {}
        char_folder = CHAR_DIR / arch_name
        char_folder.mkdir(parents=True, exist_ok=True)
        
        for anim_name, spec in ANIMATION_SPECS.items():
            n_frames = spec["frames"]
            sheet = Image.new("RGBA", (FRAME_WIDTH * n_frames, FRAME_HEIGHT), C_CLEAR)
            
            for f in range(n_frames):
                f_img = draw_character_frame(arch_data, anim_name, f, n_frames)
                sheet.paste(f_img, (f * FRAME_WIDTH, 0))
                
            out_filename = f"{anim_name}.png"
            sheet.save(char_folder / out_filename, optimize=True)
            
            arch_manifest[anim_name] = {
                "file": f"characters/{arch_name}/{out_filename}",
                "frames": n_frames,
                "frame_width": FRAME_WIDTH,
                "frame_height": FRAME_HEIGHT,
                "duration": spec["duration"],
                "loop": spec["loop"],
                "baseline_y": BASELINE_Y,
            }
            
        manifest[arch_name] = arch_manifest
        
    return manifest


# ==========================================
# 2. ARENAS GENERATOR (3 DISTINCT ENVIRONMENTS)
# ==========================================

def generate_arenas() -> None:
    """Generate Abandoned Dojo, Crimson Forest, and Ruined Temple layered backgrounds."""
    ARENAS_DIR.mkdir(parents=True, exist_ok=True)
    w, h = 1280, 720
    
    # --- 1. ABANDONED DOJO ---
    print("Generating Abandoned Dojo arena...")
    dojo_bg = Image.new("RGBA", (w, h), C_CLEAR)
    # Deep midnight sky gradient
    sky = create_gradient_surface(w, h, (10, 14, 28, 255), (28, 36, 62, 255))
    dojo_bg.paste(sky, (0, 0))
    d_draw = ImageDraw.Draw(dojo_bg)
    
    # Massive full pale moon
    moon_x, moon_y, moon_r = 640, 240, 140
    d_draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(230, 240, 255, 255))
    # Moon aura ring
    d_draw.ellipse([moon_x - moon_r - 20, moon_y - moon_r - 20, moon_x + moon_r + 20, moon_y + moon_r + 20], outline=(200, 220, 255, 60), width=18)
    
    # Dojo Wooden Pillars & Pagoda Eaves Silhouette
    d_draw.polygon([(0, 160), (320, 220), (320, 240), (0, 200)], fill=(14, 16, 24, 255))
    d_draw.polygon([(1280, 160), (960, 220), (960, 240), (1280, 200)], fill=(14, 16, 24, 255))
    # Massive Center Torii Arch
    d_draw.rectangle([200, 180, 230, 580], fill=(16, 18, 26, 255))
    d_draw.rectangle([1050, 180, 1080, 580], fill=(16, 18, 26, 255))
    d_draw.rectangle([160, 160, 1120, 195], fill=(18, 20, 30, 255))
    d_draw.rectangle([180, 210, 1100, 230], fill=(18, 20, 30, 255))
    
    # Hanging lanterns with warm golden glow
    for lx in [380, 900]:
        d_draw.line([(lx, 230), (lx, 290)], fill=(20, 20, 20, 255), width=2)
        # Glow
        d_draw.ellipse([lx - 25, 290 - 15, lx + 25, 335 + 15], fill=(255, 180, 50, 45))
        d_draw.rectangle([lx - 14, 290, lx + 14, 335], fill=(235, 140, 30, 255))
        d_draw.rectangle([lx - 16, 286, lx + 16, 292], fill=(40, 30, 20, 255))
        d_draw.rectangle([lx - 16, 333, lx + 16, 339], fill=(40, 30, 20, 255))
        
    # Shoji lattice screen silhouettes in background
    for sx in range(260, 1020, 90):
        d_draw.line([(sx, 240), (sx, 580)], fill=(25, 30, 45, 120), width=2)
    for sy in range(260, 580, 60):
        d_draw.line([(240, sy), (1040, sy)], fill=(25, 30, 45, 120), width=2)
        
    # Ground: Polished dark tatami/wood floor with moon reflection sheen
    d_draw.rectangle([0, 580, 1280, 720], fill=(16, 18, 26, 255))
    d_draw.line([(0, 580), (1280, 580)], fill=(65, 80, 110, 255), width=3)
    # Floor reflections
    for rx in range(480, 800, 25):
        d_draw.line([(rx, 585), (rx + 40, 585)], fill=(180, 200, 230, 40), width=2)
        d_draw.line([(rx - 20, 610), (rx + 60, 610)], fill=(180, 200, 230, 25), width=3)
        
    dojo_bg.save(ARENAS_DIR / "abandoned_dojo.png", optimize=True)

    # --- 2. CRIMSON FOREST ---
    print("Generating Crimson Forest arena...")
    forest_bg = Image.new("RGBA", (w, h), C_CLEAR)
    sky_forest = create_gradient_surface(w, h, (25, 10, 18, 255), (75, 18, 30, 255))
    forest_bg.paste(sky_forest, (0, 0))
    f_draw = ImageDraw.Draw(forest_bg)
    
    # Blood Moon
    f_draw.ellipse([640 - 120, 180 - 120, 640 + 120, 180 + 120], fill=(245, 55, 75, 255))
    f_draw.ellipse([640 - 150, 180 - 150, 640 + 150, 180 + 150], outline=(255, 90, 110, 50), width=25)
    
    # Gnarled Tree Silhouettes
    for tx, tw, th in [(80, 50, 500), (280, 35, 460), (1000, 40, 480), (1200, 60, 520)]:
        f_draw.polygon([
            (tx - tw, 580), (tx - tw * 0.4, 580 - th), 
            (tx + tw * 0.4, 580 - th), (tx + tw, 580)
        ], fill=(12, 10, 16, 255))
        # Twisted branches
        f_draw.line([(tx, 580 - th * 0.7), (tx - 90, 580 - th * 0.95)], fill=(12, 10, 16, 255), width=14)
        f_draw.line([(tx, 580 - th * 0.6), (tx + 80, 580 - th * 0.9)], fill=(12, 10, 16, 255), width=12)
        
    # Torii Gate in midground
    f_draw.rectangle([480, 260, 505, 580], fill=(22, 12, 18, 255))
    f_draw.rectangle([775, 260, 800, 580], fill=(22, 12, 18, 255))
    f_draw.rectangle([440, 240, 840, 265], fill=(24, 14, 20, 255))
    
    # Crimson Forest Ground with fallen red leaves
    f_draw.rectangle([0, 580, 1280, 720], fill=(18, 12, 16, 255))
    f_draw.line([(0, 580), (1280, 580)], fill=(180, 35, 50, 255), width=3)
    # Scatter leaves
    np.random.seed(42)
    for _ in range(120):
        lx = np.random.randint(0, 1280)
        ly = np.random.randint(582, 715)
        f_draw.ellipse([lx, ly, lx + 6, ly + 3], fill=(215, 45, 60, 190))
        
    forest_bg.save(ARENAS_DIR / "crimson_forest.png", optimize=True)

    # --- 3. RUINED TEMPLE ---
    print("Generating Ruined Temple arena...")
    temple_bg = Image.new("RGBA", (w, h), C_CLEAR)
    sky_temple = create_gradient_surface(w, h, (12, 8, 24, 255), (38, 20, 65, 255))
    temple_bg.paste(sky_temple, (0, 0))
    t_draw = ImageDraw.Draw(temple_bg)
    
    # Celestial Rift / Cosmic Eclipse
    f_draw = t_draw
    t_draw.ellipse([640 - 100, 200 - 100, 640 + 100, 200 + 100], fill=(15, 10, 28, 255))
    t_draw.ellipse([640 - 106, 200 - 106, 640 + 106, 200 + 106], outline=(175, 80, 255, 180), width=6)
    t_draw.ellipse([640 - 130, 200 - 130, 640 + 130, 200 + 130], outline=(130, 50, 220, 60), width=18)
    
    # Crumbling stone pillars & dragon statues
    for px in [140, 340, 940, 1140]:
        # Fractured pillar silhouette
        t_draw.polygon([
            (px - 30, 580), (px - 26, 280), (px - 10, 270), 
            (px + 24, 275), (px + 30, 580)
        ], fill=(16, 14, 24, 255))
        # Rune carvings with violet glow
        t_draw.line([(px, 340), (px, 420)], fill=(180, 90, 255, 160), width=2)
        t_draw.line([(px - 8, 380), (px + 8, 380)], fill=(180, 90, 255, 160), width=2)
        
    # Stone Pagoda Roof Fragments
    t_draw.polygon([(0, 240), (220, 280), (0, 310)], fill=(14, 12, 22, 255))
    t_draw.polygon([(1280, 240), (1060, 280), (1280, 310)], fill=(14, 12, 22, 255))
    
    # Ancient Cracked Flagstone Floor
    t_draw.rectangle([0, 580, 1280, 720], fill=(16, 14, 22, 255))
    t_draw.line([(0, 580), (1280, 580)], fill=(140, 70, 220, 255), width=3)
    # Ground Runes
    for gx in range(220, 1100, 140):
        t_draw.ellipse([gx - 18, 595 - 6, gx + 18, 595 + 6], outline=(170, 80, 245, 90), width=2)
        
    temple_bg.save(ARENAS_DIR / "ruined_temple.png", optimize=True)


# ==========================================
# 3. VISUAL EFFECTS GENERATOR
# ==========================================

def generate_effects() -> None:
    """Generate punch impact, kick impact, block barrier, and special burst effects."""
    EFFECTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Punch Impact (Radial flash star with spark lines)
    p_img = Image.new("RGBA", (128, 128), C_CLEAR)
    p_draw = ImageDraw.Draw(p_img)
    cx, cy = 64, 64
    for r in [40, 28, 16]:
        alpha = int(255 * (1.0 - r / 50.0))
        p_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 230, 180, alpha))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        ex = cx + math.cos(rad) * 55
        ey = cy + math.sin(rad) * 55
        p_draw.line([(cx, cy), (ex, ey)], fill=(255, 255, 255, 220), width=2)
    p_img.save(EFFECTS_DIR / "punch_impact.png")
    
    # 2. Kick Impact (Sweeping crescent slash arc)
    k_img = Image.new("RGBA", (160, 160), C_CLEAR)
    k_draw = ImageDraw.Draw(k_img)
    k_draw.arc([20, 20, 140, 140], 210, 340, fill=(255, 80, 95, 240), width=10)
    k_draw.arc([25, 25, 135, 135], 220, 330, fill=(255, 240, 245, 255), width=4)
    k_img.save(EFFECTS_DIR / "kick_impact.png")
    
    # 3. Block Barrier (Hexagonal glowing energy shield)
    b_img = Image.new("RGBA", (140, 180), C_CLEAR)
    b_draw = ImageDraw.Draw(b_img)
    pts = [
        (70, 10), (125, 45), (125, 135), 
        (70, 170), (15, 135), (15, 45)
    ]
    b_draw.polygon(pts, fill=(50, 180, 255, 40), outline=(80, 210, 255, 230), width=3)
    # Inner hexagon
    in_pts = [(70 + (x - 70) * 0.7, 90 + (y - 90) * 0.7) for x, y in pts]
    b_draw.polygon(in_pts, outline=(150, 235, 255, 180), width=2)
    b_img.save(EFFECTS_DIR / "block_barrier.png")
    
    # 4. Special Attack Nova (Shadow Burst Detonation Ring)
    s_img = Image.new("RGBA", (256, 256), C_CLEAR)
    s_draw = ImageDraw.Draw(s_img)
    scx, scy = 128, 128
    # Outer violet energy corona
    s_draw.ellipse([scx - 110, scy - 110, scx + 110, scy + 110], outline=(180, 60, 255, 160), width=8)
    s_draw.ellipse([scx - 85, scy - 85, scx + 85, scy + 85], outline=(220, 110, 255, 210), width=12)
    # Dark shadow vortex core
    s_draw.ellipse([scx - 55, scy - 55, scx + 55, scy + 55], fill=(14, 10, 22, 255), outline=(255, 255, 255, 230), width=3)
    s_img.save(EFFECTS_DIR / "special_burst.png")


# ==========================================
# 4. USER INTERFACE & ICONS GENERATOR
# ==========================================

def generate_ui_and_icons() -> None:
    """Generate game logo, menu banner, buttons, bars, weapon icons, and currency."""
    UI_DIR.mkdir(parents=True, exist_ok=True)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Game Logo ("SHADOW CLASH")
    logo = Image.new("RGBA", (640, 160), C_CLEAR)
    l_draw = ImageDraw.Draw(logo)
    # Metallic Dark Emblem Plaque
    l_draw.polygon([(40, 30), (600, 30), (570, 130), (70, 130)], fill=(16, 18, 26, 240), outline=(215, 38, 56, 255), width=3)
    # Twin Crossed Katanas in silhouette behind logo
    l_draw.line([(80, 135), (560, 25)], fill=(180, 195, 215, 200), width=5)
    l_draw.line([(80, 25), (560, 135)], fill=(180, 195, 215, 200), width=5)
    # Crimson slash accent
    l_draw.line([(120, 80), (520, 80)], fill=(215, 38, 56, 180), width=2)
    logo.save(UI_DIR / "logo.png")
    
    # 2. Main Menu Background (Atmospheric warrior duel under full moon)
    menu_bg = Image.new("RGBA", (1280, 720), C_CLEAR)
    m_sky = create_gradient_surface(1280, 720, (8, 10, 18, 255), (24, 30, 48, 255))
    menu_bg.paste(m_sky, (0, 0))
    mb_draw = ImageDraw.Draw(menu_bg)
    # Giant Moon
    mb_draw.ellipse([640 - 180, 300 - 180, 640 + 180, 300 + 180], fill=(225, 235, 250, 255))
    # Two dueling shadow warriors on pagoda cliff
    mb_draw.polygon([(0, 520), (540, 500), (500, 720), (0, 720)], fill=(12, 12, 16, 255))
    mb_draw.polygon([(1280, 520), (740, 500), (780, 720), (1280, 720)], fill=(12, 12, 16, 255))
    # Bridge / Abyss gap
    mb_draw.line([(0, 520), (1280, 520)], fill=(50, 65, 90, 255), width=2)
    menu_bg.save(UI_DIR / "menu_background.png")
    
    # 3. Button States (Normal, Hover, Pressed)
    bw, bh = 280, 54
    for state, border_col, bg_col in [
        ("normal", (80, 95, 125, 255), (18, 22, 32, 230)),
        ("hover", (215, 38, 56, 255), (32, 28, 42, 245)),
        ("pressed", (255, 75, 95, 255), (14, 12, 20, 255))
    ]:
        b_img = Image.new("RGBA", (bw, bh), C_CLEAR)
        bd = ImageDraw.Draw(b_img)
        # Angled martial button geometry
        poly = [(12, 0), (bw, 0), (bw - 12, bh), (0, bh)]
        bd.polygon(poly, fill=bg_col, outline=border_col, width=2)
        # Accent corner tick
        bd.line([(0, bh - 10), (10, bh)], fill=border_col, width=3)
        b_img.save(UI_DIR / f"button_{state}.png")
        
    # 4. Currency Coin Icon (Gold with Shadow mark)
    coin = Image.new("RGBA", (64, 64), C_CLEAR)
    c_draw = ImageDraw.Draw(coin)
    c_draw.ellipse([4, 4, 60, 60], fill=(235, 180, 40, 255), outline=(160, 110, 15, 255), width=3)
    c_draw.ellipse([12, 12, 52, 52], outline=(255, 215, 90, 255), width=2)
    # Shadow Kanji / Yin-Yang stylized mark
    c_draw.polygon([(32, 16), (44, 32), (32, 48), (20, 32)], fill=(20, 18, 24, 255))
    coin.save(ICONS_DIR / "coin.png")
    
    # 5. Weapon Icons (4 Weapons: Training Gloves, Steel Knuckles, Shadow Blade, Eclipse Staff)
    weapon_defs = [
        ("training_gloves", (160, 120, 80, 255), "gloves"),
        ("steel_knuckles", (190, 205, 220, 255), "knuckles"),
        ("shadow_blade", (180, 60, 220, 255), "blade"),
        ("eclipse_staff", (215, 45, 60, 255), "staff"),
    ]
    for w_name, w_col, w_shape in weapon_defs:
        w_img = Image.new("RGBA", (96, 96), C_CLEAR)
        wd = ImageDraw.Draw(w_img)
        # Plaque background
        wd.rounded_rectangle([4, 4, 92, 92], radius=8, fill=(20, 22, 32, 240), outline=(55, 65, 85, 255), width=2)
        if w_shape == "gloves":
            wd.ellipse([26, 26, 70, 70], fill=w_col, outline=(30, 20, 10, 255), width=2)
            wd.line([(34, 42), (62, 42)], fill=(40, 30, 20, 255), width=3)
        elif w_shape == "knuckles":
            for kx in [30, 42, 54, 66]:
                wd.ellipse([kx - 5, 34, kx + 5, 46], fill=w_col, outline=(40, 50, 60, 255), width=2)
            wd.rectangle([25, 44, 71, 62], fill=w_col, outline=(40, 50, 60, 255), width=2)
        elif w_shape == "blade":
            wd.line([(20, 76), (76, 20)], fill=w_col, width=5)
            wd.line([(18, 78), (30, 66)], fill=(235, 180, 40, 255), width=7)
        elif w_shape == "staff":
            wd.line([(18, 78), (78, 18)], fill=w_col, width=6)
            wd.ellipse([68, 12, 84, 28], outline=(255, 215, 90, 255), width=3)
            wd.ellipse([12, 68, 28, 84], outline=(255, 215, 90, 255), width=3)
        w_img.save(ICONS_DIR / f"{w_name}.png")
        
    # 6. Fighter Portraits (For HUD & Selection)
    for arch_name, arch_data in ARCHETYPES.items():
        port = Image.new("RGBA", (128, 128), C_CLEAR)
        pd = ImageDraw.Draw(port)
        # Dark framing
        pd.rectangle([4, 4, 124, 124], fill=(16, 18, 26, 255), outline=arch_data["accent_color"], width=3)
        # Silhouette head profile
        cx, cy = 64, 64
        pd.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=C_BLACK)
        # Eyes
        pd.ellipse([cx + 6, cy - 6, cx + 16, cy], fill=arch_data["eye_color"])
        # Head adornment
        if arch_data["head_style"] == "headband":
            pd.rectangle([cx - 30, cy - 12, cx + 26, cy - 6], fill=arch_data["accent_color"])
        elif arch_data["head_style"] == "horned_helm":
            pd.polygon([(cx - 8, cy - 24), (cx - 24, cy - 50), (cx, cy - 28)], fill=C_BLACK)
            pd.polygon([(cx + 8, cy - 24), (cx + 24, cy - 50), (cx, cy - 28)], fill=C_BLACK)
        elif arch_data["head_style"] == "samurai_crest":
            pd.arc([cx - 24, cy - 42, cx + 24, cy - 18], 180, 360, fill=arch_data["accent_color"], width=4)
        port.save(UI_DIR / f"portrait_{arch_name}.png")


# ==========================================
# 5. MASTER ASSET GENERATION ENTRY POINT
# ==========================================

def generate_all_assets() -> None:
    """Run full asset generation pipeline and write asset manifest."""
    print("=== SHADOW CLASH ASSET PIPELINE START ===")
    
    char_manifest = generate_all_character_sprites()
    generate_arenas()
    generate_effects()
    generate_ui_and_icons()
    
    manifest_data = {
        "version": "1.0.0",
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "baseline_y": BASELINE_Y,
        "characters": char_manifest,
        "arenas": [
            "abandoned_dojo",
            "crimson_forest",
            "ruined_temple"
        ],
        "effects": [
            "punch_impact.png",
            "kick_impact.png",
            "block_barrier.png",
            "special_burst.png"
        ],
        "weapons": [
            "training_gloves",
            "steel_knuckles",
            "shadow_blade",
            "eclipse_staff"
        ]
    }
    
    manifest_path = ASSETS_DIR / "assets_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
        
    print(f"Asset manifest generated at {manifest_path}")
    print("=== SHADOW CLASH ASSET PIPELINE COMPLETE ===")


if __name__ == "__main__":
    generate_all_assets()
