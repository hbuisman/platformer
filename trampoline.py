# trampoline.py
import pygame
from draggable import Draggable

class Trampoline(Draggable):
    DEFAULT_IMAGE_PATH = "images/trampoline.png"
    DEFAULT_HEIGHT = 40

    def __init__(self, x, y, width, height=None):
        """
        Create a trampoline.

        Args:
            x, y: Top‐left coordinates.
            width: Desired width.
            height: Desired height (defaults to DEFAULT_HEIGHT).
        """
        if height is None:
            height = Trampoline.DEFAULT_HEIGHT
        self.rect = pygame.Rect(x, y, width, height)
        original = pygame.image.load(Trampoline.DEFAULT_IMAGE_PATH).convert_alpha()
        self.texture = pygame.transform.smoothscale(original, (width, height))

    def draw(self, surface):
        """Draw the trampoline by blitting its texture."""
        surface.blit(self.texture, self.rect)
