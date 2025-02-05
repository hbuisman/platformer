import pygame
from draggable import Draggable

class Star(Draggable):
    def __init__(self, x, y):
        Draggable.__init__(self)
        self.image = pygame.image.load("images/star.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False

    def draw(self, surface):
        if not self.collected:
            if self.being_dragged:
                tinted = self.get_tinted_surface(self.image)
                surface.blit(tinted, self.rect)
            else:
                surface.blit(self.image, self.rect)
