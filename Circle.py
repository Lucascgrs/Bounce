import pygame
import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class CircleParams:
    """Classe de paramètres pour configurer facilement les cercles"""
    x: float = 0.0
    y: float = 0.0
    radius: float = 50.0
    thickness: int = 2
    color: Tuple[int, int, int] = (255, 255, 255)  # Blanc par défaut
    rotation_speed: float = 0.0
    is_rotating: bool = False
    has_gravity: bool = False
    gravity: float = 9.81
    arc_start: float = 0.0
    arc_length: float = 360.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    bounce_factor: float = 0.8
    friction: float = 0.99
    mass: float = 1.0
    active: bool = True
    visible: bool = True


class Circle:
    def __init__(self, params: Optional[CircleParams] = None):
        """
        Initialise un cercle avec les paramètres donnés ou les valeurs par défaut
        :param params: CircleParams contenant les paramètres personnalisés
        """
        if params is None:
            params = CircleParams()

        # Position
        self.x = float(params.x)
        self.y = float(params.y)
        self.original_x = params.x
        self.original_y = params.y

        # Propriétés physiques
        self.radius = params.radius
        self.thickness = params.thickness
        self.color = params.color
        self.mass = params.mass

        # Rotation
        self.rotation = 0
        self.rotation_speed = params.rotation_speed
        self.is_rotating = params.is_rotating

        # Arc
        self.arc_start = params.arc_start
        self.arc_length = min(params.arc_length, 360)

        # Physique
        self.has_gravity = params.has_gravity
        self.gravity = params.gravity
        self.velocity_x = params.velocity_x
        self.velocity_y = params.velocity_y
        self.bounce_factor = params.bounce_factor
        self.friction = params.friction

        # État
        self.active = params.active
        self.visible = params.visible

        # Rectangle englobant
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,self.radius * 2, self.radius * 2)

    def update(self, dt: float, screen_width: int, screen_height: int):
        if not self.active:
            return

        if self.is_rotating:
            self.rotation = (self.rotation + self.rotation_speed * dt) % 360

        if self.has_gravity:
            self.velocity_y += self.gravity * dt

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        self._handle_screen_collision(screen_width, screen_height)

        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return

        if self.arc_length >= 360:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius), self.thickness)
        else:
            start_angle = math.radians(self.arc_start + self.rotation)
            end_angle = math.radians(self.arc_start + self.arc_length + self.rotation)
            pygame.draw.arc(screen, self.color, self.rect, start_angle, end_angle, self.thickness)

    def _handle_screen_collision(self, screen_width: int, screen_height: int):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.velocity_x = abs(self.velocity_x) * self.bounce_factor
        elif self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            self.velocity_x = -abs(self.velocity_x) * self.bounce_factor

        if self.y - self.radius < 0:
            self.y = self.radius
            self.velocity_y = abs(self.velocity_y) * self.bounce_factor
        elif self.y + self.radius > screen_height:
            self.y = screen_height - self.radius
            self.velocity_y = -abs(self.velocity_y) * self.bounce_factor