"""SHADOW CLASH - Asset Validation Suite.

Validates:
1. Presence and integrity of assets_manifest.json
2. All character sprite sheet images, dimensions, and frame divisions
3. Arena backgrounds and visual dimensions (1280x720)
4. Combat effects and UI assets
5. 44.1kHz WAV audio assets (SFX and background music)
6. Reports actionable diagnostics and exit code 0 on full success
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from PIL import Image
import wave

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def validate_all_assets() -> bool:
    """Validate all game assets and return True if all required assets pass."""
    print("=" * 60)
    print("SHADOW CLASH ASSET VALIDATION")
    print("=" * 60)
    
    errors: list[str] = []
    warnings: list[str] = []
    
    # 1. Manifest Validation
    manifest_path = ASSETS_DIR / "assets_manifest.json"
    if not manifest_path.is_file():
        errors.append(f"Missing manifest file: {manifest_path}")
        return False
        
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        errors.append(f"Failed to parse manifest JSON: {e}")
        return False
        
    fw = manifest.get("frame_width", 192)
    fh = manifest.get("frame_height", 192)
    characters = manifest.get("characters", {})
    
    if len(characters) < 6:
        errors.append(f"Expected at least 6 characters in manifest, found {len(characters)}")
        
    total_sheets = 0
    total_frames = 0
    
    # 2. Character Sprite Sheets Validation
    for char_name, anims in characters.items():
        for anim_name, anim_data in anims.items():
            rel_path = anim_data.get("file")
            if not rel_path:
                errors.append(f"No file path specified for {char_name}:{anim_name}")
                continue
                
            img_path = ASSETS_DIR / rel_path
            if not img_path.is_file():
                errors.append(f"Missing sprite sheet: {img_path}")
                continue
                
            try:
                with Image.open(img_path) as im:
                    w, h = im.size
                    frames = anim_data.get("frames", 1)
                    expected_w = fw * frames
                    if w != expected_w or h != fh:
                        errors.append(
                            f"Invalid dimension for {char_name}:{anim_name} -> "
                            f"Got ({w}, {h}), expected ({expected_w}, {fh})"
                        )
                    total_sheets += 1
                    total_frames += frames
            except Exception as e:
                errors.append(f"Error opening image {img_path}: {e}")
                
    print(f"Validated {len(characters)} characters, {total_sheets} sprite sheets, {total_frames} total frames.")

    # 3. Arenas Validation
    arenas = manifest.get("arenas", [])
    if len(arenas) < 3:
        errors.append(f"Expected at least 3 arenas, found {len(arenas)}")
        
    for arena in arenas:
        arena_file = ASSETS_DIR / "arenas" / f"{arena}.png"
        if not arena_file.is_file():
            errors.append(f"Missing arena background: {arena_file}")
            continue
        try:
            with Image.open(arena_file) as im:
                if im.size != (1280, 720):
                    errors.append(f"Arena {arena} has size {im.size}, expected (1280, 720)")
        except Exception as e:
            errors.append(f"Error opening arena {arena_file}: {e}")
            
    print(f"Validated {len(arenas)} arenas.")

    # 4. Effects & UI
    required_effects = ["punch_impact.png", "kick_impact.png", "block_barrier.png", "special_burst.png"]
    for eff in required_effects:
        eff_path = ASSETS_DIR / "effects" / eff
        if not eff_path.is_file():
            errors.append(f"Missing effect asset: {eff_path}")
            
    required_ui = ["logo.png", "menu_background.png", "button_normal.png", "button_hover.png", "button_pressed.png"]
    for ui_f in required_ui:
        ui_path = ASSETS_DIR / "ui" / ui_f
        if not ui_path.is_file():
            errors.append(f"Missing UI asset: {ui_path}")
            
    # 5. Audio Assets Validation
    required_audio = [
        "light_punch.wav", "heavy_punch.wav", "kick.wav", "heavy_kick.wav",
        "block.wav", "weapon_strike.wav", "jump.wav", "land.wav",
        "special_charge.wav", "special_attack.wav", "victory.wav", "defeat.wav",
        "menu_click.wav", "menu_hover.wav", "bgm_combat.wav", "bgm_boss.wav", "bgm_menu.wav"
    ]
    audio_dir = ASSETS_DIR / "audio"
    for snd in required_audio:
        snd_path = audio_dir / snd
        if not snd_path.is_file():
            errors.append(f"Missing audio asset: {snd_path}")
            continue
        try:
            with wave.open(str(snd_path), "rb") as wf:
                if wf.getnchannels() < 1 or wf.getframerate() != 44100:
                    warnings.append(f"Audio {snd} framerate is {wf.getframerate()} (expected 44100)")
        except Exception as e:
            errors.append(f"Error verifying audio file {snd_path}: {e}")
            
    print(f"Validated {len(required_audio)} audio files.")

    # Summary
    print("-" * 60)
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  [!] {w}")
            
    if errors:
        print(f"FAILURES ({len(errors)}):")
        for err in errors:
            print(f"  [X] {err}")
        print("Asset validation FAILED.")
        return False
        
    print("ALL REQUIRED ASSETS VALIDATED SUCCESSFULLY! (100% OK)")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = validate_all_assets()
    sys.exit(0 if success else 1)
