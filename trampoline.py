import pygame
from draggable import Draggable

class Trampoline(Draggable):
    DEFAULT_IMAGE_PATH = "images/trampoline.png"
    DEFAULT_HEIGHT = 40

    def __init__(self, x, y, width, height=None):
        Draggable.__init__(self)
        if height is None:
            height = Trampoline.DEFAULT_HEIGHT
        self.rect = pygame.Rect(x, y, width, height)
        original = pygame.image.load(Trampoline.DEFAULT_IMAGE_PATH).convert_alpha()
        self.texture = pygame.transform.smoothscale(original, (width, height))

    def draw(self, surface):
        if self.being_dragged:
            tinted = self.get_tinted_surface(self.texture)
            surface.blit(tinted, self.rect)
        else:
            surface.blit(self.texture, self.rect)
