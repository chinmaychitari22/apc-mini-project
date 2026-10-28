"""SHADOW CLASH - Unified Input Manager.

Handles keyboard and mouse input, coordinate mapping from actual window space
to the fixed 1280x720 logical canvas, and input buffering for responsive combat execution.
"""

from __future__ import annotations
from typing import Optional
import pygame

from settings import DEFAULT_CONTROLS, LOGICAL_WIDTH, LOGICAL_HEIGHT


class InputManager:
    """Processes Pygame events, manages key states, and maintains input buffers."""
    
    _instance: Optional[InputManager] = None

    def __init__(self) -> None:
        self.controls = dict(DEFAULT_CONTROLS)
        
        self.keys_pressed: set[int] = set()
        self.keys_just_down: set[int] = set()
        self.keys_just_up: set[int] = set()
        
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_logical_pos: tuple[int, int] = (0, 0)
        self.mouse_buttons_down: set[int] = set()
        self.mouse_just_down: set[int] = set()
        self.mouse_just_up: set[int] = set()
        
        # Display scaling transform values (updated by SceneManager)
        self.scale_factor: float = 1.0
        self.offset_x: int = 0
        self.offset_y: int = 0
        
        # Combat input buffer (action_name, timestamp)
        self.input_buffer: list[tuple[str, float]] = []
        self.buffer_window: float = 0.25  # seconds
        self.current_time: float = 0.0

    @classmethod
    def get_instance(cls) -> InputManager:
        if cls._instance is None:
            cls._instance = InputManager()
        return cls._instance

    def set_display_transform(self, scale: float, off_x: int, off_y: int) -> None:
        """Update window scaling parameters to map mouse positions accurately."""
        self.scale_factor = max(0.001, scale)
        self.offset_x = off_x
        self.offset_y = off_y

    def begin_frame(self, current_time: float) -> None:
        """Clear frame-local impulse events at start of game loop."""
        self.current_time = current_time
        self.keys_just_down.clear()
        self.keys_just_up.clear()
        self.mouse_just_down.clear()
        self.mouse_just_up.clear()
        
        # Prune expired inputs from buffer
        self.input_buffer = [
            (action, t) for action, t in self.input_buffer 
            if current_time - t <= self.buffer_window
        ]

    def process_event(self, event: pygame.event.Event) -> None:
        """Handle individual Pygame event."""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_just_down.add(event.key)
            
            # Map key to combat action and buffer it
            for action, key_codes in self.controls.items():
                if event.key in key_codes:
                    self.buffer_action(action)
                    
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            self.keys_just_up.add(event.key)
            
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self._update_logical_mouse()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_down.add(event.button)
            self.mouse_just_down.add(event.button)
            self._update_logical_mouse()
            
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_down.discard(event.button)
            self.mouse_just_up.add(event.button)
            self._update_logical_mouse()

    def _update_logical_mouse(self) -> None:
        """Convert actual screen pixel mouse position to 1280x720 canvas coordinates."""
        mx, my = self.mouse_pos
        lx = int((mx - self.offset_x) / self.scale_factor)
        ly = int((my - self.offset_y) / self.scale_factor)
        self.mouse_logical_pos = (
            max(0, min(LOGICAL_WIDTH, lx)),
            max(0, min(LOGICAL_HEIGHT, ly))
        )

    def is_action_held(self, action: str) -> bool:
        """Check if any bound key for an action is currently held."""
        bound = self.controls.get(action, [])
        return any(k in self.keys_pressed for k in bound)

    def is_action_just_pressed(self, action: str) -> bool:
        """Check if an action key was pressed down this frame."""
        bound = self.controls.get(action, [])
        return any(k in self.keys_just_down for k in bound)

    def buffer_action(self, action: str) -> None:
        """Buffer an action for combo/attack input tolerance."""
        self.input_buffer.append((action, self.current_time))

    def consume_buffered_action(self, action: str) -> bool:
        """Check if action is in buffer and consume it if found."""
        for i, (act, t) in enumerate(self.input_buffer):
            if act == action:
                self.input_buffer.pop(i)
                return True
        return False

    def clear_buffer(self) -> None:
        """Flush the input buffer."""
        self.input_buffer.clear()

    def is_mouse_button_just_down(self, button: int = 1) -> bool:
        """Check if mouse button (1 = Left) was clicked this frame."""
        return button in self.mouse_just_down

    def get_mouse_logical_pos(self) -> tuple[int, int]:
        """Return the cursor coordinates in logical 1280x720 space."""
        return self.mouse_logical_pos
