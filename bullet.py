import pygame

class Bullet:
    def __init__(self, x, y, direction):
        self.image = pygame.image.load("images/bullet.png").convert_alpha()
        bullet_scale = 0.20  # Scale down to 20% of original size
        bullet_new_size = (int(self.image.get_width() * bullet_scale),
                           int(self.image.get_height() * bullet_scale))
        self.image = pygame.transform.smoothscale(self.image, bullet_new_size)
        self.rect = self.image.get_rect(center=(x, y))
        bullet_speed = 15  # Adjust bullet speed as desired
        if direction == "right":
            self.velocity = (bullet_speed, 0)
        else:
            self.velocity = (-bullet_speed, 0)
    
    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def is_off_screen(self, screen_width, screen_height):
        return (self.rect.right < 0 or self.rect.left > screen_width or 
                self.rect.bottom < 0 or self.rect.top > screen_height) 