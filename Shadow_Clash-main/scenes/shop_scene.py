"""SHADOW CLASH - Armory and Dojo Dojo Shop Scene.

Manages purchasing new weapons, equipping owned weapons, and acquiring
permanent martial stat upgrades (Strength, Vitality, Defense, Special Surge).
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import pygame

from settings import (
    COLOR_MOONLIGHT, COLOR_AMBER_GOLD, COLOR_CRIMSON,
    COLOR_SILVER_MUTED, LOGICAL_WIDTH, LOGICAL_HEIGHT
)
from scenes.base_scene import BaseScene
from ui.buttons import Button
from ui.typography import Typography
from ui.notifications import NotificationToast
from systems.save_manager import SaveManager
from systems.progression import ProgressionSystem
from systems.economy import EconomyManager
from systems.achievements import AchievementManager
from entities.weapon import WeaponRegistry
from game.asset_manager import AssetManager
from game.audio_manager import AudioManager
from game.input_manager import InputManager

if TYPE_CHECKING:
    from game.scene_manager import SceneManager


class ShopScene(BaseScene):
    """Armory store interface."""

    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.asset_mgr = AssetManager.get_instance()
        self.audio_mgr = AudioManager.get_instance()
        self.input_mgr = InputManager.get_instance()
        
        self.save_mgr = SaveManager()
        self.progression = ProgressionSystem(self.save_mgr)
        self.economy = EconomyManager(self.save_mgr)
        self.achievement_mgr = AchievementManager(self.save_mgr)
        self.toast = NotificationToast()
        
        # Tabs: "WEAPONS" or "UPGRADES"
        self.current_tab: str = "WEAPONS"
        
        # Weapons list
        self.weapons = list(WeaponRegistry.all_weapons().values())
        self.selected_weapon_idx: int = 0
        
        # Upgrades list
        self.upgrade_keys = ["strength", "vitality", "defense", "special_efficiency"]
        self.selected_upgrade_idx: int = 0
        
        # Buttons
        self.tab_buttons: list[Button] = []
        self.action_button: Optional[Button] = None
        self.back_button: Button = Button(
            rect=pygame.Rect(80, 640, 180, 44),
            text="BACK",
            callback=self._on_back
        )
        self.item_select_buttons: list[Button] = []

        self._init_ui()
        self._update_action_button()

    def _init_ui(self) -> None:
        # Tab Buttons
        self.tab_buttons = [
            Button(pygame.Rect(80, 110, 200, 42), "WEAPONS", lambda: self._set_tab("WEAPONS")),
            Button(pygame.Rect(300, 110, 200, 42), "UPGRADES", lambda: self._set_tab("UPGRADES")),
        ]
        self._rebuild_item_buttons()

    def _set_tab(self, tab: str) -> None:
        self.current_tab = tab
        self._rebuild_item_buttons()
        self._update_action_button()

    def _rebuild_item_buttons(self) -> None:
        self.item_select_buttons.clear()
        start_y = 180
        
        if self.current_tab == "WEAPONS":
            for i, w in enumerate(self.weapons):
                idx = i
                btn = Button(
                    rect=pygame.Rect(80, start_y + i * 90, 440, 75),
                    text=w.name,
                    callback=lambda i=idx: self._select_weapon(i),
                    font_size=20
                )
                self.item_select_buttons.append(btn)
        else:
            for i, k in enumerate(self.upgrade_keys):
                idx = i
                name = self.progression.upgrades_config.get(k, {}).get("name", k.title())
                btn = Button(
                    rect=pygame.Rect(80, start_y + i * 90, 440, 75),
                    text=name,
                    callback=lambda i=idx: self._select_upgrade(i),
                    font_size=20
                )
                self.item_select_buttons.append(btn)

    def _select_weapon(self, idx: int) -> None:
        self.selected_weapon_idx = idx
        self._update_action_button()

    def _select_upgrade(self, idx: int) -> None:
        self.selected_upgrade_idx = idx
        self._update_action_button()

    def _update_action_button(self) -> None:
        """Update the action button based on current selection."""
        px, py = 560, 180  # Panel position from render()

        if self.current_tab == "WEAPONS":
            w = self.weapons[self.selected_weapon_idx]
            if self.economy.is_weapon_equipped(w.id):
                self.action_button = Button(pygame.Rect(px + 30, py + 350, 240, 48), "EQUIPPED", enabled=False)
            elif self.economy.is_weapon_owned(w.id):
                self.action_button = Button(pygame.Rect(px + 30, py + 350, 240, 48), "EQUIP", lambda: self._equip_weapon(w.id))
            else:
                can_buy = self.economy.can_afford(w.price)
                self.action_button = Button(
                    pygame.Rect(px + 30, py + 350, 240, 48),
                    f"BUY ({w.price}c)",
                    lambda: self._buy_weapon_and_check(w.id),
                    enabled=can_buy
                )
        else:
            k = self.upgrade_keys[self.selected_upgrade_idx]
            info = self.progression.upgrades_config.get(k, {})
            max_lvl = int(info.get("max_level", 5))
            cur_lvl = self.progression.get_upgrade_level(k)
            cost = self.progression.get_upgrade_cost(k)

            if cur_lvl >= max_lvl:
                self.action_button = Button(pygame.Rect(px + 30, py + 350, 260, 48), "MAX LEVEL", enabled=False)
            else:
                can_up = self.progression.can_purchase_upgrade(k)
                self.action_button = Button(
                    pygame.Rect(px + 30, py + 350, 260, 48),
                    f"UPGRADE ({cost}c)",
                    lambda: self._purchase_upgrade(k),
                    enabled=can_up
                )

    def _on_back(self) -> None:
        from scenes.main_menu import MainMenuScene
        self.scene_manager.change_scene(MainMenuScene(self.scene_manager))

    def on_enter(self) -> None:
        self.audio_mgr.play_bgm("bgm_menu", loop=True)

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse_pos = self.input_mgr.get_mouse_logical_pos()
        for tb in self.tab_buttons:
            tb.handle_event(event, mouse_pos)
        for ib in self.item_select_buttons:
            ib.handle_event(event, mouse_pos)
        self.back_button.handle_event(event, mouse_pos)
        if self.action_button:
            self.action_button.handle_event(event, mouse_pos)

    def update(self, dt: float) -> None:
        self.toast.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        # Background
        bg = self.asset_mgr.get_ui_image("menu_background")
        surface.blit(bg, (0, 0))
        
        veil = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        veil.fill((12, 14, 22, 235))
        surface.blit(veil, (0, 0))

        # Title & Currency Display
        Typography.draw_text_with_shadow(
            surface, "THE SHADOW ARMORY", self.asset_mgr.get_font(42, bold=True), COLOR_MOONLIGHT, 80, 40
        )
        
        # Coins Display
        coin_icon = self.asset_mgr.get_icon("coin")
        surface.blit(pygame.transform.smoothscale(coin_icon, (36, 36)), (1060, 44))
        Typography.draw_text_with_shadow(
            surface, f"{self.economy.current_coins} COINS", self.asset_mgr.get_font(24, bold=True), COLOR_AMBER_GOLD, 1105, 50
        )

        # Tabs & Back
        for tb in self.tab_buttons:
            tb.render(surface)
        for ib in self.item_select_buttons:
            ib.render(surface)
        self.back_button.render(surface)

        # Right-side Detail Inspection Panel
        panel_rect = pygame.Rect(560, 180, 640, 430)
        p_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        p_surf.fill((18, 22, 32, 240))
        pygame.draw.rect(p_surf, (70, 85, 115), (0, 0, panel_rect.width, panel_rect.height), 2)
        surface.blit(p_surf, panel_rect.topleft)

        px, py = panel_rect.x, panel_rect.y
        f_name = self.asset_mgr.get_font(28, bold=True)
        f_desc = self.asset_mgr.get_font(18)
        f_stat = self.asset_mgr.get_font(20, bold=True)

        if self.current_tab == "WEAPONS":
            w = self.weapons[self.selected_weapon_idx]
            # Weapon icon
            icon_img = self.asset_mgr.get_icon(w.id)
            surface.blit(pygame.transform.smoothscale(icon_img, (80, 80)), (px + 30, py + 30))

            Typography.draw_text_with_shadow(surface, w.name, f_name, COLOR_AMBER_GOLD, px + 130, py + 35)
            status_text = "EQUIPPED" if self.economy.is_weapon_equipped(w.id) else ("OWNED" if self.economy.is_weapon_owned(w.id) else f"PRICE: {w.price} COINS")
            status_col = (120, 230, 160) if self.economy.is_weapon_equipped(w.id) else ((220, 230, 245) if self.economy.is_weapon_owned(w.id) else COLOR_AMBER_GOLD)
            Typography.draw_text_with_shadow(surface, status_text, f_stat, status_col, px + 130, py + 72)

            # Description
            Typography.draw_text_with_shadow(surface, w.description, f_desc, COLOR_SILVER_MUTED, px + 30, py + 130)

            # Modifiers
            Typography.draw_text_with_shadow(surface, f"DAMAGE: +{int((w.damage_mult - 1.0) * 100)}%", f_stat, COLOR_MOONLIGHT, px + 30, py + 180)
            Typography.draw_text_with_shadow(surface, f"STRIKE SPEED: {int(w.speed_mult * 100)}%", f_stat, COLOR_MOONLIGHT, px + 30, py + 215)
            Typography.draw_text_with_shadow(surface, f"COMBAT REACH: +{int(w.reach_bonus)}px", f_stat, COLOR_MOONLIGHT, px + 30, py + 250)
            Typography.draw_text_with_shadow(surface, f"ENERGY SIPHON: +{int((w.energy_gain_mult - 1.0) * 100)}%", f_stat, COLOR_MOONLIGHT, px + 30, py + 285)

        else:
            # Upgrades View
            k = self.upgrade_keys[self.selected_upgrade_idx]
            info = self.progression.upgrades_config.get(k, {})
            name = info.get("name", k.title())
            desc = info.get("description", "")
            cur_lvl = self.progression.get_upgrade_level(k)
            max_lvl = int(info.get("max_level", 5))
            cost = self.progression.get_upgrade_cost(k)

            Typography.draw_text_with_shadow(surface, name, f_name, COLOR_AMBER_GOLD, px + 30, py + 35)
            Typography.draw_text_with_shadow(surface, f"LEVEL: {cur_lvl} / {max_lvl}", f_stat, COLOR_MOONLIGHT, px + 30, py + 75)
            Typography.draw_text_with_shadow(surface, desc, f_desc, COLOR_SILVER_MUTED, px + 30, py + 125)

            # Level Pips
            for p in range(max_lvl):
                pip_col = COLOR_AMBER_GOLD if p < cur_lvl else (40, 45, 60)
                pygame.draw.rect(surface, pip_col, (px + 30 + p * 35, py + 175, 26, 16))
                pygame.draw.rect(surface, (80, 95, 120), (px + 30 + p * 35, py + 175, 26, 16), 1)

        if self.action_button:
            self.action_button.render(surface)

        self.toast.render(surface)

    def _equip_weapon(self, weapon_id: str) -> None:
        self.economy.equip_weapon(weapon_id)
        self._update_action_button()

    def _purchase_upgrade(self, upgrade_key: str) -> None:
        self.progression.purchase_upgrade(upgrade_key)
        self._update_action_button()

    def _buy_weapon_and_check(self, weapon_id: str) -> None:
        if self.economy.buy_weapon(weapon_id):
            # Update button state after purchase
            self._update_action_button()
            # Check armory achievements
            new_achs = self.achievement_mgr.check_collection_milestones()
            for ach in new_achs:
                self.toast.enqueue(ach["title"], ach["description"])
