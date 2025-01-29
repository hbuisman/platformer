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
        
        # ADD A DIAGONAL SLIDE PLATFORM HERE:
        self.slides = [
            # This slide goes from (500, 250) down to (700, 550)
            # Adjust coordinates however you like
            SlidePlatform(500, 250, 700, 550)
        ]

    def draw(self, surface):
        for platform in self.platforms:
            pygame.draw.rect(surface, BLUE, platform)
        # Draw the slide(s)
        for slide in self.slides:
            slide.draw(surface)

class SlidePlatform:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = (0, 200, 0)  # green line for the slide

    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x1, self.y1), (self.x2, self.y2), 5) 