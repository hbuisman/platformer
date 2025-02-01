import pygame
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class SlidePhysics:
    """Physics data for a player on the slide"""
    alignment_y: float  # Y position player should be aligned to
    velocity_x: float  # X velocity for sliding
    velocity_y: float  # Y velocity for sliding

class SlidePlatform:
    """A platform that players can slide down."""

    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """Create a slide from start point to end point."""
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        # Visual properties
        self._load_textures()
        self.is_flipped = False

        # Create collision rect centered on slide
        self.rect = self._calculate_rect()
        self.flip_icon_rect = pygame.Rect(0, 0, 32, 32)
        self._update_flip_icon_position()

    def _load_textures(self):
        """Load and prepare slide textures."""
        # Load and scale original texture
        original = pygame.image.load("images/slide.png").convert_alpha()
        height = 120
        width = int(379 * (height / 349.0))  # Maintain aspect ratio
        self.original_texture = pygame.transform.smoothscale(original, (width, height))
        self.texture = self.original_texture  # Current texture starts as original
        # Create flipped version
        self.flipped_texture = pygame.transform.flip(self.texture, True, False)
        
        # Load rotate icon
        self.rotate_icon = pygame.image.load("images/rotate.png").convert_alpha()
        self.rotate_icon = pygame.transform.smoothscale(self.rotate_icon, (32, 32))

    def _calculate_rect(self) -> pygame.Rect:
        """Calculate the slide's collision rectangle."""
        mid_x = (self.start_x + self.end_x) // 2
        mid_y = (self.start_y + self.end_y) // 2
        return self.texture.get_rect(center=(mid_x, mid_y))

    def _update_flip_icon_position(self):
        """Update flip icon position based on slide orientation."""
        if self.is_flipped:
            self.flip_icon_rect.topright = self.rect.topright
        else:
            self.flip_icon_rect.topleft = self.rect.topleft

    def flip(self):
        """Flip the slide's visual and physical orientation."""
        self.is_flipped = not self.is_flipped
        
        # Flip texture
        self.texture = pygame.transform.flip(self.texture, True, False)
        
        # Only swap x coordinates, keep y coordinates the same
        self.start_x, self.end_x = self.end_x, self.start_x
        
        # Recompute internal values
        old_center = self.rect.center
        self.rect = self.texture.get_rect()
        self.rect.center = old_center
        self._update_flip_icon_position()

    def contains_point(self, x: int, y: int, threshold: int=30) -> bool:
        """Check if point (x,y) is within sliding distance of the slide line."""
        if not self.rect.collidepoint(x, y):
            return False

        # Project point onto slide line
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        if dx == 0 and dy == 0:
            return False

        # Calculate distance from point to line
        px = x - self.start_x
        py = y - self.start_y
        t = max(0, min(1, (px * dx + py * dy) / (dx * dx + dy * dy)))
        proj_x = self.start_x + t * dx
        proj_y = self.start_y + t * dy

        dist_sq = (x - proj_x)**2 + (y - proj_y)**2
        return dist_sq <= threshold * threshold

    def compute_physics(self, player_x: float, player_y: float) -> Optional[SlidePhysics]:
        """Compute slide physics for a player at given position."""
        # Calculate vector components
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        
        if dx == 0:  # Vertical slide
            return None
            
        # Calculate how far along the slide the player is (0 to 1)
        t = (player_x - self.start_x) / dx
        t = max(0, min(1, t))  # Clamp to slide bounds
        
        # Calculate alignment position
        align_y = self.start_y + t * dy
        
        # Increased slide speed from 2.0 to 4.0
        SLIDE_SPEED = 4.0
        
        # Calculate normalized direction vector
        length = (dx * dx + dy * dy) ** 0.5
        dir_x = dx / length
        dir_y = dy / length
        
        # Only slide if moving downward (increasing y)
        if self.end_y < self.start_y:
            dir_x = -dir_x
            dir_y = -dir_y
            
        velocity_x = dir_x * SLIDE_SPEED
        velocity_y = dir_y * SLIDE_SPEED

        return SlidePhysics(
            alignment_y=align_y,
            velocity_x=velocity_x,
            velocity_y=velocity_y
        )

    def draw(self, surface: pygame.Surface, highlight: bool=False):
        """Draw the slide and its debug info."""
        # Draw slide texture
        texture = self.texture
        if highlight:
            texture = texture.copy()
            overlay = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 255, 128))
            texture.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(texture, self.rect)

        # Draw flip icon if mouse is in bounding box
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self._draw_flip_icon(surface)

    def _draw_flip_icon(self, surface: pygame.Surface):
        """Draw the flip icon when slide is hovered."""
        # Just draw the rotate icon directly - use its own transparency
        surface.blit(self.rotate_icon, self.flip_icon_rect)

    def handle_click(self, pos) -> bool:
        """Handle mouse click at position pos. Returns True if click was handled."""
        # First check if mouse is even in slide's bounding box
        if not self.rect.collidepoint(pos):
            return False
        
        # Then check if click is in flip icon's rect
        if self.flip_icon_rect.collidepoint(pos):
            self.flip()
            return True
        
        return False