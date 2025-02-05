# star.py
import pygame
from draggable import Draggable

class Star(Draggable):
    def __init__(self, x, y):
        self.image = pygame.image.load("images/star.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False

    def draw(self, surface, is_dragging=False):
        if not self.collected:
            if is_dragging:
                tinted = self.image.copy()
                overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 255, 128))
                tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(tinted, self.rect)
            else:
                surface.blit(self.image, self.rect)
