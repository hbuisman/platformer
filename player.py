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
        
        # New flag to track whether player is on the slide
        self.on_slide = False
        
        # Load the "ouch.wav" sound when the player object is created
        self.ouch_sound = pygame.mixer.Sound("sounds/ouch.wav")
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # If the player isn't on a slide, accept left/right input
        if not self.on_slide:
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

    def update(self, platforms, slides, trampolines):
        # Apply horizontal movement
        self.rect.x += self.x_velocity
        # Collision in x-direction
        self.check_collisions_x(platforms)
        
        # Apply gravity
        self.apply_gravity()
        self.rect.y += self.y_velocity
        # Collision in y-direction
        self.check_collisions_y(platforms)
        
        # Now check if we're on the slide
        self.check_slides(slides)
        # Finally, check trampolines
        self.check_trampolines(trampolines)

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

    # NEW SLIDE COLLISION LOGIC:
    def check_slides(self, slides):
        # Reset the on_slide flag each frame; we'll set it True if we find a slide
        self.on_slide = False
        for slide in slides:
            if self.is_on_slide(slide):
                self.align_on_slide(slide)
                self.on_slide = True
                break  # already aligned on one slide

    def is_on_slide(self, slide):
        # Check if player's bottom center is within the slide's x-range
        bottom_center_x = self.rect.centerx
        min_x = min(slide.x1, slide.x2)
        max_x = max(slide.x1, slide.x2)
        
        if bottom_center_x < min_x or bottom_center_x > max_x:
            return False
        
        # Calculate the y-value on the slide for that x
        dx = slide.x2 - slide.x1
        dy = slide.y2 - slide.y1
        if dx == 0:  # vertical line edge case
            return False
        
        slope = dy / dx
        y_on_slide = slide.y1 + slope * (bottom_center_x - slide.x1)
        
        # If player's bottom is close to y_on_slide
        if abs(self.rect.bottom - y_on_slide) < 5:
            return True
        
        return False

    def align_on_slide(self, slide):
        # Compute slope of the line
        dx = slide.x2 - slide.x1
        dy = slide.y2 - slide.y1
        slope = dy / dx
        
        # Reposition the player so bottom is exactly on the slide
        bottom_center_x = self.rect.centerx
        y_on_slide = slide.y1 + slope * (bottom_center_x - slide.x1)
        self.rect.bottom = y_on_slide
        
        # Optionally give a sideways + downward velocity
        # We can set x_velocity based on the slope's direction
        slide_direction = 1 if slide.x2 > slide.x1 else -1
        self.x_velocity = slide_direction * 2  # speed along x
        # For downward effect, add some downward velocity
        self.y_velocity = abs(self.x_velocity * slope)
        
    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)

    def check_trampolines(self, trampolines):
        for tramp in trampolines:
            if self.rect.colliderect(tramp):
                # If the player is falling down
                if self.y_velocity > 0:
                    # Position player on top of trampoline
                    self.rect.bottom = tramp.top
                    # Bounce higher than normal
                    self.y_velocity = -JUMP_FORCE * 2
                    # Not on_ground so we can keep applying gravity
                    self.on_ground = False 