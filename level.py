import pygame

BLUE = (0, 0, 255)

class Level:
    def __init__(self):
        # You can define platforms here or load them from a file, etc.
        self.platforms = [
            pygame.Rect(0, 550, 800, 50),    # Floor platform
            pygame.Rect(200, 450, 100, 20), # Lower platform
            pygame.Rect(400, 400, 100, 20), # Middle platform
            pygame.Rect(250, 350, 100, 20), # Another one for vertical stepping
            pygame.Rect(450, 300, 100, 20), # A bit higher
        ]

    def draw(self, surface):
        for platform in self.platforms:
            pygame.draw.rect(surface, BLUE, platform) 