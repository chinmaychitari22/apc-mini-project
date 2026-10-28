"""SHADOW CLASH - Settings and Controls Reference Scene.

Configures music and SFX volume levels, mute state, displays keyboard bindings,
and synchronizes with persistence.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from settings import (
    COLOR_MOONLIGHT, COLOR_AMBER_GOLD, COLOR_CRIMSON,
    COLOR_SILVER_MUTED, LOGICAL_WIDTH, LOGICAL_HEIGHT
)
from scenes.base_scene import BaseScene
from ui.buttons import Button
from ui.typography import Typography
from systems.save_manager import SaveManager
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class SettingsScene(BaseScene):
    """Audio calibration and controls overview."""

    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        self.save_mgr = SaveManager()
        
        self.buttons: list[Button] = []
        self._init_buttons()

    def _init_buttons(self) -> None:
        cx = 640
        btn_y = 200
        
        # Music Volume Buttons
        self.buttons.append(Button(
            pygame.Rect(cx + 80, btn_y, 44, 40), "-", self._music_down, font_size=20
        ))
        self.buttons.append(Button(
            pygame.Rect(cx + 180, btn_y, 44, 40), "+", self._music_up, font_size=20
        ))
        
        # SFX Volume Buttons
        self.buttons.append(Button(
            pygame.Rect(cx + 80, btn_y + 60, 44, 40), "-", self._sfx_down, font_size=20
        ))
        self.buttons.append(Button(
            pygame.Rect(cx + 180, btn_y + 60, 44, 40), "+", self._sfx_up, font_size=20
        ))
        
        # Mute Toggle
        mute_label = "UNMUTE" if self.audio_mgr.is_muted else "MUTE ALL"
        self.mute_btn = Button(
            pygame.Rect(cx - 100, btn_y + 130, 200, 44), mute_label, self._toggle_mute, font_size=20
        )
        self.buttons.append(self.mute_btn)
        
        # Back Button
        self.buttons.append(Button(
            pygame.Rect(cx - 120, 620, 240, 48), "MAIN MENU", self._on_back
        ))

    def _music_up(self) -> None:
        vol = min(1.0, self.audio_mgr.music_volume + 0.1)
        self.audio_mgr.set_music_volume(vol)
        self.save_mgr.data["audio_settings"]["music_volume"] = vol
        self.save_mgr.save()

    def _music_down(self) -> None:
        vol = max(0.0, self.audio_mgr.music_volume - 0.1)
        self.audio_mgr.set_music_volume(vol)
        self.save_mgr.data["audio_settings"]["music_volume"] = vol
        self.save_mgr.save()

    def _sfx_up(self) -> None:
        vol = min(1.0, self.audio_mgr.sfx_volume + 0.1)
        self.audio_mgr.set_sfx_volume(vol)
        self.save_mgr.data["audio_settings"]["sfx_volume"] = vol
        self.save_mgr.save()
        self.audio_mgr.play_sfx("menu_click")

    def _sfx_down(self) -> None:
        vol = max(0.0, self.audio_mgr.sfx_volume - 0.1)
        self.audio_mgr.set_sfx_volume(vol)
        self.save_mgr.data["audio_settings"]["sfx_volume"] = vol
        self.save_mgr.save()
        self.audio_mgr.play_sfx("menu_click")

    def _toggle_mute(self) -> None:
        muted = self.audio_mgr.toggle_mute()
        self.mute_btn.text = "UNMUTE" if muted else "MUTE ALL"
        self.save_mgr.data["audio_settings"]["is_muted"] = muted
        self.save_mgr.save()

    def _on_back(self) -> None:
        from scenes.main_menu import MainMenuScene
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse_pos = self.input_mgr.get_mouse_logical_pos()
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        bg = self.asset_mgr.get_ui_image("menu_background")
        surface.blit(bg, (0, 0))
        
        veil = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        veil.fill((10, 12, 18, 235))
        surface.blit(veil, (0, 0))

        cx = 640
        f_title = self.asset_mgr.get_font(42, bold=True)
        f_label = self.asset_mgr.get_font(22, bold=True)
        f_sub = self.asset_mgr.get_font(18)

        Typography.draw_text_with_shadow(surface, "SETTINGS & CONTROLS", f_title, COLOR_MOONLIGHT, cx, 80, align="center")

        # Audio Volume Displays
        Typography.draw_text_with_shadow(surface, "MUSIC VOLUME", f_label, COLOR_AMBER_GOLD, cx - 200, 208)
        Typography.draw_text_with_shadow(surface, f"{int(self.audio_mgr.music_volume * 100)}%", f_label, COLOR_MOONLIGHT, cx + 135, 208)

        Typography.draw_text_with_shadow(surface, "SFX VOLUME", f_label, COLOR_AMBER_GOLD, cx - 200, 268)
        Typography.draw_text_with_shadow(surface, f"{int(self.audio_mgr.sfx_volume * 100)}%", f_label, COLOR_MOONLIGHT, cx + 135, 268)

        # Controls Overview Panel
        panel = pygame.Rect(cx - 360, 400, 720, 180)
        p_surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        p_surf.fill((18, 22, 32, 230))
        pygame.draw.rect(p_surf, (65, 80, 110), (0, 0, panel.width, panel.height), 2)
        surface.blit(p_surf, panel.topleft)

        Typography.draw_text_with_shadow(surface, "MARTIAL ARTS CONTROLS REFERENCE", f_label, COLOR_AMBER_GOLD, cx, 420, align="center")
        
        col1_x = cx - 320
        col2_x = cx + 40
        Typography.draw_text_with_shadow(surface, "A / D  -  Move Left / Right", f_sub, COLOR_MOONLIGHT, col1_x, 460)
        Typography.draw_text_with_shadow(surface, "W  -  Jump", f_sub, COLOR_MOONLIGHT, col1_x, 490)
        Typography.draw_text_with_shadow(surface, "S  -  Crouch / Low Stance", f_sub, COLOR_MOONLIGHT, col1_x, 520)
        Typography.draw_text_with_shadow(surface, "L / SPACE  -  Block Guard", f_sub, COLOR_MOONLIGHT, col1_x, 550)

        Typography.draw_text_with_shadow(surface, "J  -  Light Punch", f_sub, COLOR_MOONLIGHT, col2_x, 460)
        Typography.draw_text_with_shadow(surface, "U  -  Heavy Punch", f_sub, COLOR_MOONLIGHT, col2_x, 490)
        Typography.draw_text_with_shadow(surface, "K  -  Light Kick", f_sub, COLOR_MOONLIGHT, col2_x, 520)
        Typography.draw_text_with_shadow(surface, "I  -  Heavy Kick", f_sub, COLOR_MOONLIGHT, col2_x, 550)

        for btn in self.buttons:
            btn.render(surface)
