import pygame

GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_FORCE = 10
RED = (255, 0, 0)

class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_velocity = 0
        self.y_velocity = 0
        
        # Track how many jumps remain (for double jump)
        self.jumps_left = 2
        
        self.on_ground = False
        
        # Load the "ouch.wav" sound when the player object is created
        self.ouch_sound = pygame.mixer.Sound("sounds/ouch.wav")
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Left/right movement
        if keys[pygame.K_LEFT]:
            self.x_velocity = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.x_velocity = PLAYER_SPEED
        else:
            self.x_velocity = 0
        
        # Double jump logic
        # If SPACE is pressed and we have jumps left, jump!
        if keys[pygame.K_SPACE] and self.jumps_left > 0:
            # We check if we are not currently moving upwards (to avoid repeated triggers in one press)
            if self.y_velocity >= 0:
                self.y_velocity = -JUMP_FORCE
                self.jumps_left -= 1

    def apply_gravity(self):
        self.y_velocity += GRAVITY

    def update(self, platforms):
        # Apply horizontal movement
        self.rect.x += self.x_velocity
        # Collision in x-direction
        self.check_collisions_x(platforms)
        
        # Apply gravity
        self.apply_gravity()
        self.rect.y += self.y_velocity
        # Collision in y-direction
        self.check_collisions_y(platforms)

    def check_collisions_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform):
                # Moving to the right
                if self.x_velocity > 0:
                    self.rect.right = platform.left
                # Moving to the left
                elif self.x_velocity < 0:
                    self.rect.left = platform.right

    def check_collisions_y(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                # Moving down
                if self.y_velocity > 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True
                    
                    # Reset jumps_left when you land
                    self.jumps_left = 2
                # Moving up
                elif self.y_velocity < 0:
                    # Play the ouch sound when bumping head on a platform
                    self.ouch_sound.play()
                    self.rect.top = platform.bottom
                    self.y_velocity = 0

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect) 