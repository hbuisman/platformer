# slide.py
import pygame
from dataclasses import dataclass
from typing import Optional
from draggable import Draggable

@dataclass
class SlidePhysics:
    """Physics data for a player on the slide."""
    alignment_y: float
    velocity_x: float
    velocity_y: float

class SlidePlatform(Draggable):
    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.hover_timer = 0
        self._load_textures()
        self.is_flipped = False
        self.rect = self._calculate_rect()
        self.flip_icon_rect = pygame.Rect(0, 0, 32, 32)
        self._update_flip_icon_position()

    def _load_textures(self):
        original = pygame.image.load("images/slide.png").convert_alpha()
        height = 120
        width = int(379 * (height / 349.0))  # Maintain aspect ratio
        self.original_texture = pygame.transform.smoothscale(original, (width, height))
        self.texture = self.original_texture  # Current texture
        self.flipped_texture = pygame.transform.flip(self.texture, True, False)
        self.rotate_icon = pygame.image.load("images/rotate.png").convert_alpha()
        self.rotate_icon = pygame.transform.smoothscale(self.rotate_icon, (32, 32))

    def _calculate_rect(self) -> pygame.Rect:
        mid_x = (self.start_x + self.end_x) // 2
        mid_y = (self.start_y + self.end_y) // 2
        return self.texture.get_rect(center=(mid_x, mid_y))

    def _update_flip_icon_position(self):
        if self.is_flipped:
            self.flip_icon_rect.topright = self.rect.topright
        else:
            self.flip_icon_rect.topleft = self.rect.topleft

    def flip(self):
        self.is_flipped = not self.is_flipped
        self.texture = pygame.transform.flip(self.texture, True, False)
        self.start_x, self.end_x = self.end_x, self.start_x
        old_center = self.rect.center
        self.rect = self.texture.get_rect()
        self.rect.center = old_center
        self._update_flip_icon_position()

    def contains_point(self, x: int, y: int, threshold: int = 30) -> bool:
        if not self.rect.collidepoint(x, y):
            return False
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        if dx == 0 and dy == 0:
            return False
        px = x - self.start_x
        py = y - self.start_y
        t = max(0, min(1, (px * dx + py * dy) / (dx * dx + dy * dy)))
        proj_x = self.start_x + t * dx
        proj_y = self.start_y + t * dy
        dist_sq = (x - proj_x)**2 + (y - proj_y)**2
        return dist_sq <= threshold * threshold

    def compute_physics(self, player_x: float, player_y: float) -> Optional[SlidePhysics]:
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        if dx == 0:
            return None
        t = (player_x - self.start_x) / dx
        t = max(0, min(1, t))
        align_y = self.start_y + t * dy
        SLIDE_SPEED = 4.0
        length = (dx * dx + dy * dy) ** 0.5
        dir_x = dx / length
        dir_y = dy / length
        if self.end_y < self.start_y:
            dir_x = -dir_x
            dir_y = -dir_y
        velocity_x = dir_x * SLIDE_SPEED
        velocity_y = dir_y * SLIDE_SPEED
        return SlidePhysics(alignment_y=align_y, velocity_x=velocity_x, velocity_y=velocity_y)

    def start_drag(self, mouse_x, mouse_y):
        # Override: store offset relative to the slide's start point
        self.drag_offset_x = self.start_x - mouse_x
        self.drag_offset_y = self.start_y - mouse_y

    def update_drag(self, mouse_x, mouse_y):
        new_start_x = mouse_x + self.drag_offset_x
        new_start_y = mouse_y + self.drag_offset_y
        delta_x = new_start_x - self.start_x
        delta_y = new_start_y - self.start_y
        self.start_x += delta_x
        self.start_y += delta_y
        self.end_x += delta_x
        self.end_y += delta_y
        self.rect = self._calculate_rect()
        self._update_flip_icon_position()

    def draw(self, surface, highlight: bool = False):
        texture = self.texture.copy() if highlight else self.texture
        if highlight:
            overlay = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 255, 128))
            texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(texture, self.rect)
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self._draw_flip_icon(surface)

    def _draw_flip_icon(self, surface):
        surface.blit(self.rotate_icon, self.flip_icon_rect)

    def handle_click(self, pos) -> bool:
        if not self.rect.collidepoint(pos):
            return False
        if self.flip_icon_rect.collidepoint(pos):
            self.flip()
            return True
        return False
