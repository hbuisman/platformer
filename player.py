import pygame
from slide import SlidePlatform, SlidePhysics

GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_FORCE = 10

class Player:
    def __init__(self, x, y, width, height):
        # Make the player twice as big (80x80 instead of 40x40)
        self.rect = pygame.Rect(x, y, width * 2, height * 2)
        self.x_velocity = 0
        self.y_velocity = 0
        
        # Track how many jumps remain (for double jump)
        self.jumps_left = 2
        
        self.on_ground = False
        
        # New flag to track whether player is on the slide
        self.on_slide = False
        
        # Load player image and scale it to match the new collision rect
        self.image = pygame.image.load("images/player_big.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (width * 2, height * 2))
        
        # Create flipped version of the image
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        
        # Track which direction player is facing
        self.facing_right = True
        
        # Load the "ouch.wav" sound when the player object is created
        self.ouch_sound = pygame.mixer.Sound("sounds/big_player_ouch.wav")
        self.boing_sound = pygame.mixer.Sound("sounds/big_player_boing.wav")
        self.portal_sound = pygame.mixer.Sound("sounds/big_player_portal.wav")
        
        self.width = width * 2
        self.height = height * 2
        
        self.lives = 3
        self.invulnerable_timer = 0
        self.game_over = False
        
        # Load heart image
        self.heart_image = pygame.image.load("images/heart.png").convert_alpha()
        self.heart_image = pygame.transform.smoothscale(self.heart_image, (40, 40))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # If the player isn't on a slide, accept left/right input
        if not self.on_slide:
            if keys[pygame.K_LEFT]:
                self.x_velocity = -PLAYER_SPEED
                self.facing_right = False
            elif keys[pygame.K_RIGHT]:
                self.x_velocity = PLAYER_SPEED
                self.facing_right = True
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

    def update(self, platforms, slides, trampolines, level, elevator_movements=None):
        # Get all platforms including elevators
        all_platforms = platforms.copy()
        elevator_collisions = []
        for elevator in level.elevators:
            all_platforms.append(elevator.platform_rect)
            if self.rect.colliderect(elevator.platform_rect):
                elevator_collisions.append(elevator)
        
        print(f"x_velocity at start of update: {self.x_velocity}") # DEBUG PRINT

        # Check horizontal collisions
        self.rect.x += self.x_velocity
        for platform in all_platforms:
            if self.rect.colliderect(platform):
                print("Horizontal Collision Detected!") # DEBUG PRINT
                if self.x_velocity > 0:  # Moving right
                    self.rect.right = platform.left
                elif self.x_velocity < 0:  # Moving left
                    self.rect.left = platform.right
                self.x_velocity = 0

        # Vertical movement and collision
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity
        
        # Check vertical collisions
        self.on_ground = False
        for platform in all_platforms:
            if self.rect.colliderect(platform):
                if self.y_velocity > 0:  # Falling down
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True
                    self.jumps_left = 2
                elif self.y_velocity < 0:  # Moving up
                    self.rect.top = platform.bottom
                    self.y_velocity = 0
        
        # Handle elevator movement - now use elevator_movements from level
        for elevator in elevator_collisions:
            if self.rect.bottom == elevator.platform_rect.top:  # If we're standing on the elevator
                movement = elevator_movements.get(elevator, (0, 0)) # Get movement from level
                
                # If this is the first frame on the elevator, store the relative position
                if not hasattr(self, 'elevator_offset'):
                    self.elevator_offset = (self.rect.x - elevator.platform_rect.x, self.rect.y - elevator.platform_rect.y)
                
                # Apply the elevator movement
                self.rect.x += movement[0]
                self.rect.y += movement[1]
                
                # Apply player's horizontal velocity to the relative position
                self.elevator_offset = (self.elevator_offset[0] + self.x_velocity, self.elevator_offset[1])
                
                # Keep the player at the same relative position on the platform
                self.rect.x = elevator.platform_rect.x + self.elevator_offset[0]
                self.rect.y = elevator.platform_rect.y + self.elevator_offset[1]
            else:
                # If not on the elevator, remove the offset
                if hasattr(self, 'elevator_offset'):
                    del self.elevator_offset

        # Now check if we're on the slide
        self.check_slides(slides)
        # Finally, check trampolines
        self.check_trampolines(trampolines)
        self.check_portals(level.portals, level)

        # 1) Make sure we aren't stuck below any platform
        self.ensure_not_below_any_platform(platforms)

        # 2) Check if we've gone off-screen
        self.check_off_screen()

        # Check enemy collisions if not invulnerable
        if self.invulnerable_timer <= 0:
            self.check_enemy_collisions(level.enemies)
        else:
            self.invulnerable_timer -= 1

    def check_slides(self, slides):
        # Reset the on_slide flag each frame; we'll set it True if we find a slide
        self.on_slide = False
        # Debug message to always show slide state
        self.slide_debug_msg = "Not on slide"
        
        for slide in slides:
            if self.is_on_slide(slide):
                self.align_on_slide(slide)
                self.on_slide = True
                break  # already aligned on one slide

    def is_on_slide(self, slide):
        if not slide.contains_point(self.rect.centerx, self.rect.bottom):
            return False
            
        physics = slide.compute_physics(self.rect.centerx, self.rect.bottom)
        if not physics:
            return False
            
        # Update debug message
        self.slide_debug_msg = f"On slide: y={physics.alignment_y:.2f}, vel=({physics.velocity_x:.1f},{physics.velocity_y:.1f})"
        
        # If player's bottom is close to computed alignment y
        return abs(self.rect.bottom - physics.alignment_y) < 8

    def align_on_slide(self, slide):
        physics = slide.compute_physics(self.rect.centerx, self.rect.bottom)
        if not physics:
            return
            
        # Align player with slide
        self.rect.bottom = physics.alignment_y
        
        # Set velocities from physics
        self.x_velocity = physics.velocity_x
        self.y_velocity = physics.velocity_y

    def draw(self, surface):
        # Use the appropriate image based on direction
        image_to_draw = self.image_right if self.facing_right else self.image_left
        surface.blit(image_to_draw, self.rect)

    def check_trampolines(self, trampolines):
        for tramp in trampolines:
            if self.rect.colliderect(tramp):
                # If the player is falling down
                if self.y_velocity > 0:
                    # Play boing sound
                    self.boing_sound.play()
                    # Position player on top of trampoline
                    self.rect.bottom = tramp.top
                    # Bounce higher than normal
                    self.y_velocity = -JUMP_FORCE * 2
                    # Not on_ground so we can keep applying gravity
                    self.on_ground = False

    def check_portals(self, portals, level):
        """Check if we've entered a portal entrance"""
        for portal in portals:
            if portal.is_entrance and self.rect.colliderect(portal.rect):
                # Find the exit portal
                exit_portal = level.find_portal_pair(portal)
                if exit_portal:
                    # Play portal sound
                    self.portal_sound.play()
                    # Teleport to exit, maintaining velocity
                    self.rect.centerx = exit_portal.rect.centerx
                    self.rect.bottom = exit_portal.rect.bottom

    def change_character(self, sprite_path, sound_path):
        """Change the player's sprite and sound"""
        # Load and scale new image
        self.image = pygame.image.load(sprite_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        
        # Update both directional images
        self.image_right = self.image
        self.image_left = pygame.transform.flip(self.image, True, False)
        
        # Load new sounds - extract the base path to use for all sounds
        base_sound_path = sound_path.replace("_ouch.wav", "")
        self.ouch_sound = pygame.mixer.Sound(f"{base_sound_path}_ouch.wav")
        self.boing_sound = pygame.mixer.Sound(f"{base_sound_path}_boing.wav")
        self.portal_sound = pygame.mixer.Sound(f"{base_sound_path}_portal.wav")

    def ensure_not_below_any_platform(self, platforms):
        """If the player is inside a platform from above, place them on top and stop sliding."""
        for platform in platforms:
            if self.rect.colliderect(platform):
                # If our bottom is below the top of the platform, we came from above
                if self.rect.bottom > platform.top and self.y_velocity >= 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_slide = False  # stop sliding
                    self.on_ground = True

    def check_off_screen(self):
        """If we go off-screen, lose a life"""
        screen = pygame.display.get_surface()
        screen_width, screen_height = screen.get_width(), screen.get_height()

        # If bottom is below the screen, or we move off left/right
        if self.rect.top > screen_height or self.rect.right < 0 or self.rect.left > screen_width:
            self.lose_life()

    def draw_hearts(self, surface):
        """Draw the player's remaining lives as hearts"""
        if self.game_over:
            return
        
        for i in range(self.lives):
            x = 10 + (i * 50)  # Space hearts 50 pixels apart
            y = 10
            surface.blit(self.heart_image, (x, y))

    def lose_life(self):
        """Handle losing a life and check for game over"""
        if self.invulnerable_timer <= 0:
            self.lives -= 1
            self.invulnerable_timer = 60  # 1 second of invulnerability
            self.ouch_sound.play()
            
            # Reset position to center of screen
            screen = pygame.display.get_surface()
            self.rect.center = (screen.get_width() // 2, screen.get_height() // 2)
            
            # Check for game over
            if self.lives <= 0:
                self.game_over = True

    def check_enemy_collisions(self, enemies):
        """Check for collisions with enemies"""
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.lose_life()
                break