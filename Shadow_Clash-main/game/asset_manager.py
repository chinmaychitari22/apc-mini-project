"""SHADOW CLASH - Centralized Asset Manager.

Handles caching and retrieval of:
- Character sprite sheets and extracted animation frames
- Directional sprite flipping (cached)
- Arena background surfaces
- Visual FX textures
- UI graphics and icons
- Fonts with graceful fallbacks
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import pygame

from settings import (
    ASSETS_DIR, CHARACTERS_ASSETS_DIR, ARENAS_ASSETS_DIR,
    EFFECTS_ASSETS_DIR, UI_ASSETS_DIR, ICONS_ASSETS_DIR, FONTS_ASSETS_DIR
)


class AssetManager:
    """Singleton-style asset cache and resource manager."""
    
    _instance: Optional[AssetManager] = None

    def __init__(self) -> None:
        self.manifest: dict = {}
        self.sprite_frames: dict[str, dict[str, list[pygame.Surface]]] = {}
        self.flipped_frames: dict[str, dict[str, list[pygame.Surface]]] = {}
        self.arenas: dict[str, pygame.Surface] = {}
        self.effects: dict[str, pygame.Surface] = {}
        self.ui_images: dict[str, pygame.Surface] = {}
        self.icons: dict[str, pygame.Surface] = {}
        self.fonts: dict[tuple[str, int], pygame.font.Font] = {}
        
        self.load_manifest()
        
    @classmethod
    def get_instance(cls) -> AssetManager:
        if cls._instance is None:
            cls._instance = AssetManager()
        return cls._instance

    def load_manifest(self) -> None:
        """Load the master asset manifest JSON."""
        manifest_path = ASSETS_DIR / "assets_manifest.json"
        if manifest_path.is_file():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    self.manifest = json.load(f)
            except Exception as e:
                print(f"[AssetManager] Warning: Failed to load manifest: {e}")
                self.manifest = {}

    def get_character_frames(self, character: str, animation: str, facing_right: bool = True) -> list[pygame.Surface]:
        """Retrieve pre-cut animation frames for a character archetype."""
        if character not in self.sprite_frames:
            self.sprite_frames[character] = {}
            self.flipped_frames[character] = {}
            
        if animation not in self.sprite_frames[character]:
            self._load_character_animation(character, animation)
            
        frames = self.sprite_frames[character].get(animation, [])
        if facing_right:
            return frames
        return self.flipped_frames[character].get(animation, frames)

    def _load_character_animation(self, character: str, animation: str) -> None:
        """Load a sprite sheet from disk and chop it into individual frame surfaces."""
        char_manifest = self.manifest.get("characters", {}).get(character, {})
        anim_data = char_manifest.get(animation, {})
        
        rel_file = anim_data.get("file", f"characters/{character}/{animation}.png")
        full_path = ASSETS_DIR / rel_file
        
        frame_width = anim_data.get("frame_width", self.manifest.get("frame_width", 192))
        frame_height = anim_data.get("frame_height", self.manifest.get("frame_height", 192))
        num_frames = anim_data.get("frames", 1)
        
        frames_right: list[pygame.Surface] = []
        frames_left: list[pygame.Surface] = []
        
        if full_path.is_file():
            try:
                sheet = pygame.image.load(str(full_path)).convert_alpha()
                sheet_w, sheet_h = sheet.get_size()
                actual_frames = max(1, sheet_w // frame_width)
                
                for i in range(actual_frames):
                    sub_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    frame_surf = sheet.subsurface(sub_rect).copy()
                    flipped_surf = pygame.transform.flip(frame_surf, True, False)
                    frames_right.append(frame_surf)
                    frames_left.append(flipped_surf)
            except Exception as e:
                print(f"[AssetManager] Error loading sprite sheet {full_path}: {e}")
                
        if not frames_right:
            # Emergency procedural fallback surface
            fallback = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            pygame.draw.circle(fallback, (40, 40, 50), (frame_width // 2, frame_height // 2), 30)
            frames_right = [fallback]
            frames_left = [fallback]
            
        self.sprite_frames[character][animation] = frames_right
        self.flipped_frames[character][animation] = frames_left

    def get_arena(self, name: str) -> pygame.Surface:
        """Retrieve arena background surface (1280x720)."""
        if name in self.arenas:
            return self.arenas[name]
            
        arena_file = ARENAS_ASSETS_DIR / f"{name}.png"
        if arena_file.is_file():
            try:
                surf = pygame.image.load(str(arena_file)).convert()
                self.arenas[name] = surf
                return surf
            except Exception as e:
                print(f"[AssetManager] Error loading arena {arena_file}: {e}")
                
        # Fallback dark background
        fallback = pygame.Surface((1280, 720))
        fallback.fill((16, 20, 30))
        self.arenas[name] = fallback
        return fallback

    def get_effect(self, name: str) -> pygame.Surface:
        """Retrieve combat effect texture."""
        if name in self.effects:
            return self.effects[name]
            
        eff_file = EFFECTS_ASSETS_DIR / f"{name}.png"
        if eff_file.is_file():
            try:
                surf = pygame.image.load(str(eff_file)).convert_alpha()
                self.effects[name] = surf
                return surf
            except Exception as e:
                print(f"[AssetManager] Error loading effect {eff_file}: {e}")
                
        fallback = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(fallback, (255, 200, 50, 180), (32, 32), 24)
        self.effects[name] = fallback
        return fallback

    def get_ui_image(self, name: str) -> pygame.Surface:
        """Retrieve UI element image."""
        if name in self.ui_images:
            return self.ui_images[name]
            
        ui_file = UI_ASSETS_DIR / f"{name}.png"
        if ui_file.is_file():
            try:
                surf = pygame.image.load(str(ui_file)).convert_alpha()
                self.ui_images[name] = surf
                return surf
            except Exception as e:
                print(f"[AssetManager] Error loading UI image {ui_file}: {e}")
                
        fallback = pygame.Surface((100, 40), pygame.SRCALPHA)
        fallback.fill((30, 35, 45, 200))
        self.ui_images[name] = fallback
        return fallback

    def get_icon(self, name: str) -> pygame.Surface:
        """Retrieve weapon or currency icon."""
        if name in self.icons:
            return self.icons[name]
            
        icon_file = ICONS_ASSETS_DIR / f"{name}.png"
        if icon_file.is_file():
            try:
                surf = pygame.image.load(str(icon_file)).convert_alpha()
                self.icons[name] = surf
                return surf
            except Exception as e:
                print(f"[AssetManager] Error loading icon {icon_file}: {e}")
                
        fallback = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(fallback, (230, 180, 50), (8, 8, 48, 48), 2)
        self.icons[name] = fallback
        return fallback

    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """Retrieve cached pygame Font with martial arts fallback hierarchy."""
        key = ("default", size)
        if key in self.fonts:
            return self.fonts[key]
            
        # Try custom font first, then system fonts (consolas, trebuchet ms, arial)
        custom_font_path = FONTS_ASSETS_DIR / "martial.ttf"
        font = None
        if custom_font_path.is_file():
            try:
                font = pygame.font.Font(str(custom_font_path), size)
            except Exception:
                pass
                
        if font is None:
            # System font candidates with clean modern/martial styling
            for sys_name in ["trebuchetms", "consolas", "segoeui", "arial"]:
                try:
                    font = pygame.font.SysFont(sys_name, size, bold=bold)
                    if font:
                        break
                except Exception:
                    pass
                    
        if font is None:
            font = pygame.font.Font(None, size)
            
        self.fonts[key] = font
        return font
