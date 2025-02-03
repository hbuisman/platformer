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
        
        # Add physics properties like player
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False
        self.on_elevator = False
        self.elevator_offset = None

    def update(self, platforms, level, elevator_movements, is_dragging=False):
        # Skip physics if being dragged
        if is_dragging:
            return
            
        # Apply gravity
        self.y_velocity += 0.5  # Same as player's GRAVITY
        self.rect.y += self.y_velocity
        
        # Check trampolines first
        self.check_trampolines(level.trampolines)
        
        # Collision detection with platforms
        self._handle_vertical_collisions(platforms, level.elevators)
        self._handle_horizontal_collisions(platforms, level.elevators)
        
        # Handle elevator movement
        self._handle_elevators(level.elevators, elevator_movements)

    def _handle_vertical_collisions(self, platforms, elevators):
        self.on_ground = False
        all_platforms = platforms + [e.platform_rect for e in elevators]
        
        for platform in all_platforms:
            if self.rect.colliderect(platform):
                if self.y_velocity > 0:  # Falling down
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True
                elif self.y_velocity < 0:  # Moving up
                    self.rect.top = platform.bottom
                    self.y_velocity = 0

    def _handle_horizontal_collisions(self, platforms, elevators):
        all_platforms = platforms + [e.platform_rect for e in elevators]
        self.rect.x += self.x_velocity
        
        for platform in all_platforms:
            if self.rect.colliderect(platform):
                if self.x_velocity > 0:  # Moving right
                    self.rect.right = platform.left
                elif self.x_velocity < 0:  # Moving left
                    self.rect.left = platform.right
                self.x_velocity = 0

    def _handle_elevators(self, elevators, elevator_movements):
        elevator_collisions = []
        for elevator in elevators:
            if self.rect.colliderect(elevator.platform_rect):
                elevator_collisions.append(elevator)
        
        for elevator in elevator_collisions:
            if self.rect.bottom == elevator.platform_rect.top:
                movement = elevator_movements.get(elevator, (0, 0))
                
                if not hasattr(self, 'elevator_offset'):
                    self.elevator_offset = (self.rect.x - elevator.platform_rect.x, 
                                          self.rect.y - elevator.platform_rect.y)
                
                # Apply elevator movement
                self.rect.x += movement[0]
                self.rect.y += movement[1]
                
                # Maintain relative position
                self.rect.x = elevator.platform_rect.x + self.elevator_offset[0]
                self.rect.y = elevator.platform_rect.y + self.elevator_offset[1]
        
        self.on_elevator = len(elevator_collisions) > 0
        if not elevator_collisions and hasattr(self, 'elevator_offset'):
            del self.elevator_offset

    def check_trampolines(self, trampolines):
        """Handle trampoline bouncing like the player does"""
        for tramp in trampolines:
            if self.rect.colliderect(tramp):
                # Only bounce if falling downward
                if self.y_velocity > 0:
                    self.rect.bottom = tramp.top
                    self.y_velocity = -20  # Same bounce force as player
                    self.on_ground = True

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