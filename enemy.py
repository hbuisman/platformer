import pygame

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type
        # Load the appropriate image based on enemy type
        self.image = pygame.image.load(f"images/enemy{enemy_type}.png").convert_alpha()
        # Scale enemy to be 120x120 pixels (twice as big)
        self.image = pygame.transform.smoothscale(self.image, (120, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface, is_dragging=False):
        if is_dragging:
            # Create magenta-tinted version for dragging
            tinted = self.image.copy()
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 255, 128))  # semi-transparent magenta
            tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted, self.rect)
        else:
            surface.blit(self.image, self.rect) 