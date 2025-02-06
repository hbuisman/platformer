import pygame
from draggable import Draggable

class Trash(Draggable):
    def __init__(self, x, y):
        super().__init__()
        # Load the trash image and scale it to 40x40 (you can adjust as needed)
        self.image = pygame.image.load("images/trash.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        if self.being_dragged:
            tinted = self.get_tinted_surface(self.image)
            surface.blit(tinted, self.rect)
        else:
            surface.blit(self.image, self.rect) 