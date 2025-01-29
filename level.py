import pygame

BLUE = (0, 0, 255)
LILA = (200, 0, 200)  # new color for trampoline

class Level:
    def __init__(self):
        # You can define platforms here or load them from a file, etc.
        self.platforms = [
            pygame.Rect(0, 750, 1200, 50),   # Floor (for 800px high window)
            pygame.Rect(300, 600, 150, 20),  # Lower platform
            pygame.Rect(500, 500, 150, 20),  # Middle platform
            pygame.Rect(700, 450, 150, 20),  # Another one for vertical stepping
            pygame.Rect(900, 400, 150, 20),  # A bit higher
        ]
        
        # ADD A DIAGONAL SLIDE PLATFORM HERE:
        self.slides = [
            # This slide goes from (500, 250) down to (700, 550)
            # Adjust coordinates however you like
            SlidePlatform(500, 350, 700, 550)
        ]
        # Move trampoline to a better location (x=900, y=600)
        self.trampolines = [
            pygame.Rect(900, 600, 75, 20)
        ]

    def draw(self, surface):
        for platform in self.platforms:
            pygame.draw.rect(surface, BLUE, platform)
        # Draw the slide(s)
        for slide in self.slides:
            slide.draw(surface)
        # Draw trampolines in LILA
        for tramp in self.trampolines:
            pygame.draw.rect(surface, LILA, tramp)

class SlidePlatform:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = (0, 200, 0)  # green line for the slide

    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x1, self.y1), (self.x2, self.y2), 5) 