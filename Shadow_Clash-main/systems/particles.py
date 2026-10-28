"""SHADOW CLASH - High-Performance Particle and Combat FX System.

Manages bounded particle simulations, hit sparks, guard deflection flashes,
dust puffs, shadow mist, and floating combat damage indicators.
"""

from __future__ import annotations
import math
import random
from typing import Optional
import pygame

from settings import (
    COLOR_MOONLIGHT, COLOR_CRIMSON_GLOW, COLOR_VIOLET_GLOW,
    COLOR_CYAN_ENERGY, COLOR_AMBER_GOLD
)


class Particle:
    """An individual dynamic visual effect particle."""
    __slots__ = (
        'x', 'y', 'vx', 'vy', 'color', 'size', 'lifetime', 
        'max_lifetime', 'gravity', 'drag', 'shape'
    )

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        size: float,
        lifetime: float,
        gravity: float = 0.0,
        drag: float = 0.95,
        shape: str = "circle"
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = max(0.001, lifetime)
        self.gravity = gravity
        self.drag = drag
        self.shape = shape

    def update(self, dt: float) -> bool:
        """Update particle physics. Returns False when particle expires."""
        self.lifetime -= dt
        if self.lifetime <= 0.0:
            return False
            
        self.vx *= (self.drag ** (dt * 60.0))
        self.vy *= (self.drag ** (dt * 60.0))
        self.vy += self.gravity * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        return True


class FloatingText:
    """Floating numerical indicator for damage and combo feedback."""
    __slots__ = ('text', 'x', 'y', 'color', 'lifetime', 'max_lifetime', 'vy')

    def __init__(self, text: str, x: float, y: float, color: tuple[int, int, int], lifetime: float = 0.8) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vy = -75.0  # Floats upward

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.y += self.vy * dt
        return self.lifetime > 0.0


class ParticleSystem:
    """Bounded, memory-efficient combat particle and visual FX emitter."""
    
    _instance: Optional[ParticleSystem] = None

    def __init__(self, max_particles: int = 300) -> None:
        self.max_particles = max_particles
        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []

    @classmethod
    def get_instance(cls) -> ParticleSystem:
        if cls._instance is None:
            cls._instance = ParticleSystem()
        return cls._instance

    def clear(self) -> None:
        """Remove all active particles and texts."""
        self.particles.clear()
        self.floating_texts.clear()

    def spawn_hit_sparks(self, x: float, y: float, is_critical: bool = False, count: int = 14) -> None:
        """Spawn martial arts strike impact sparks."""
        base_color = COLOR_CRIMSON_GLOW if is_critical else COLOR_AMBER_GOLD
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(120, 420) * (1.4 if is_critical else 1.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            col = (
                min(255, base_color[0] + random.randint(-20, 20)),
                min(255, base_color[1] + random.randint(-20, 20)),
                min(255, base_color[2] + random.randint(-20, 20))
            )
            self.particles.append(Particle(
                x=x, y=y, vx=vx, vy=vy,
                color=col,
                size=random.uniform(2.5, 4.5 if is_critical else 3.5),
                lifetime=random.uniform(0.18, 0.35),
                gravity=600.0,
                drag=0.92,
                shape="spark"
            ))

    def spawn_block_barrier(self, x: float, y: float, count: int = 10) -> None:
        """Spawn defensive deflection energy shards."""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = random.uniform(-math.pi * 0.6, math.pi * 0.6)
            speed = random.uniform(80, 260)
            self.particles.append(Particle(
                x=x, y=y,
                vx=-math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=COLOR_CYAN_ENERGY,
                size=random.uniform(3.0, 5.0),
                lifetime=random.uniform(0.15, 0.28),
                gravity=200.0,
                drag=0.90,
                shape="spark"
            ))

    def spawn_dust_puff(self, x: float, y: float, count: int = 8) -> None:
        """Spawn landing or heavy step ground dust."""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            self.particles.append(Particle(
                x=x + random.uniform(-15, 15),
                y=y,
                vx=random.uniform(-90, 90),
                vy=random.uniform(-40, -10),
                color=(120, 130, 150),
                size=random.uniform(4.0, 7.5),
                lifetime=random.uniform(0.22, 0.40),
                gravity=-30.0,
                drag=0.88,
                shape="circle"
            ))

    def spawn_shadow_burst(self, x: float, y: float, count: int = 35) -> None:
        """Spawn explosive special attack nova particles."""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(160, 550)
            color = random.choice([COLOR_VIOLET_GLOW, COLOR_CYAN_ENERGY, COLOR_CRIMSON_GLOW])
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                size=random.uniform(3.5, 7.0),
                lifetime=random.uniform(0.35, 0.65),
                gravity=150.0,
                drag=0.93,
                shape="spark"
            ))

    def spawn_damage_number(self, text: str, x: float, y: float, color: tuple[int, int, int]) -> None:
        """Spawn floating numerical combat feedback."""
        if len(self.floating_texts) < 30:
            self.floating_texts.append(FloatingText(text, x, y, color))

    def update(self, dt: float) -> None:
        """Advance all active particles and text indicators."""
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

    def render(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Render all active visual effects onto logical game surface."""
        # 1. Render Particles
        for p in self.particles:
            alpha = max(0.0, min(1.0, p.lifetime / p.max_lifetime))
            cur_size = max(1.0, p.size * alpha)
            
            if p.shape == "spark":
                # Draw high-speed line segment oriented with velocity
                speed = math.hypot(p.vx, p.vy)
                if speed > 10:
                    dir_x = p.vx / speed
                    dir_y = p.vy / speed
                    tail_len = min(18.0, speed * 0.04)
                    start_pt = (int(p.x), int(p.y))
                    end_pt = (int(p.x - dir_x * tail_len), int(p.y - dir_y * tail_len))
                    pygame.draw.line(surface, p.color, start_pt, end_pt, int(cur_size))
                else:
                    pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), int(cur_size))
            else:
                pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), int(cur_size))

        # 2. Render Floating Text
        for ft in self.floating_texts:
            alpha_ratio = max(0.0, min(1.0, ft.lifetime / ft.max_lifetime))
            text_surf = font.render(ft.text, True, ft.color)
            if alpha_ratio < 0.9:
                text_surf.set_alpha(int(255 * alpha_ratio))
            rect = text_surf.get_rect(center=(int(ft.x), int(ft.y)))
            surface.blit(text_surf, rect)
