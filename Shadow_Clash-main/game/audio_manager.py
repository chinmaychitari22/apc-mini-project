"""SHADOW CLASH - Centralized Audio Manager.

Manages sound effects, ambient martial music loops, volume controls,
sound cooldown debouncing (prevents frame-stacked audio distortion),
and safe fallbacks if audio hardware is unavailable.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
import pygame

from settings import AUDIO_ASSETS_DIR, DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME


class AudioManager:
    """Manages audio playback, volume balancing, and channel scheduling."""
    
    _instance: Optional[AudioManager] = None

    def __init__(self) -> None:
        self.mixer_initialized: bool = False
        self.music_volume: float = DEFAULT_MUSIC_VOLUME
        self.sfx_volume: float = DEFAULT_SFX_VOLUME
        self.is_muted: bool = False
        
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.last_played_time: dict[str, float] = {}
        self.sound_cooldowns: dict[str, float] = {
            "light_punch": 0.08,
            "heavy_punch": 0.12,
            "kick": 0.08,
            "heavy_kick": 0.12,
            "block": 0.08,
            "weapon_strike": 0.10,
            "jump": 0.15,
            "land": 0.12,
            "special_attack": 0.30,
            "special_charge": 0.30,
            "menu_hover": 0.05,
            "menu_click": 0.05,
        }
        
        self.current_bgm_track: Optional[str] = None
        self._init_mixer()
        
    @classmethod
    def get_instance(cls) -> AudioManager:
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def _init_mixer(self) -> None:
        """Initialize pygame mixer safely."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.mixer_initialized = True
            pygame.mixer.set_num_channels(16)
        except Exception as e:
            print(f"[AudioManager] Audio hardware not available: {e}")
            self.mixer_initialized = False

    def load_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Load and cache a sound effect."""
        if not self.mixer_initialized:
            return None
            
        if name in self.sounds:
            return self.sounds[name]
            
        snd_file = AUDIO_ASSETS_DIR / f"{name}.wav"
        if snd_file.is_file():
            try:
                snd = pygame.mixer.Sound(str(snd_file))
                snd.set_volume(self.sfx_volume if not self.is_muted else 0.0)
                self.sounds[name] = snd
                return snd
            except Exception as e:
                print(f"[AudioManager] Failed to load sound {name}: {e}")
        return None

    def play_sfx(self, name: str, current_time: float = 0.0, volume_override: Optional[float] = None) -> None:
        """Play sound effect with cooldown debounce protection."""
        if not self.mixer_initialized or self.is_muted:
            return
            
        cooldown = self.sound_cooldowns.get(name, 0.05)
        last_t = self.last_played_time.get(name, -999.0)
        if current_time - last_t < cooldown:
            return  # Suppress duplicate sound on rapid consecutive triggers
            
        self.last_played_time[name] = current_time
        
        snd = self.load_sound(name)
        if snd:
            vol = volume_override if volume_override is not None else self.sfx_volume
            snd.set_volume(max(0.0, min(1.0, vol)))
            snd.play()

    def play_bgm(self, track_name: str, loop: bool = True) -> None:
        """Play looping background music track cleanly."""
        if not self.mixer_initialized:
            return
            
        if self.current_bgm_track == track_name and pygame.mixer.music.get_busy():
            return  # Already playing this track
            
        track_path = AUDIO_ASSETS_DIR / f"{track_name}.wav"
        if not track_path.is_file():
            print(f"[AudioManager] Missing BGM file: {track_path}")
            return
            
        try:
            pygame.mixer.music.load(str(track_path))
            vol = 0.0 if self.is_muted else self.music_volume
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_bgm_track = track_name
        except Exception as e:
            print(f"[AudioManager] Failed to play BGM {track_name}: {e}")

    def stop_bgm(self) -> None:
        """Stop background music."""
        if self.mixer_initialized:
            try:
                pygame.mixer.music.stop()
                self.current_bgm_track = None
            except Exception:
                pass

    def pause_bgm(self) -> None:
        if self.mixer_initialized:
            pygame.mixer.music.pause()

    def unpause_bgm(self) -> None:
        if self.mixer_initialized:
            pygame.mixer.music.unpause()

    def set_music_volume(self, volume: float) -> None:
        """Update music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized and not self.is_muted:
            pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """Update SFX volume across all cached sound instances."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized and not self.is_muted:
            for snd in self.sounds.values():
                snd.set_volume(self.sfx_volume)

    def toggle_mute(self) -> bool:
        """Toggle mute state on or off."""
        self.is_muted = not self.is_muted
        if self.mixer_initialized:
            if self.is_muted:
                pygame.mixer.music.set_volume(0.0)
                for snd in self.sounds.values():
                    snd.set_volume(0.0)
            else:
                pygame.mixer.music.set_volume(self.music_volume)
                for snd in self.sounds.values():
                    snd.set_volume(self.sfx_volume)
        return self.is_muted
