import pygame
from physics_object import PhysicsObject
from draggable import Draggable

class Enemy(PhysicsObject, Draggable):
    def __init__(self, x, y, enemy_type):
        # Initialize parent classes.
        PhysicsObject.__init__(self)
        Draggable.__init__(self)
        self.enemy_type = enemy_type

        # Determine the image path.
        if enemy_type == "spaghetti_monster":
            image_path = "images/spaghetti_monster.png"
        else:
            image_path = f"images/enemy{enemy_type}.png"

        # Load and scale the image.
        original_image = pygame.image.load(image_path).convert_alpha()
        scaled_image = pygame.transform.smoothscale(original_image, (120, 120))

        # Cache both right- and left-facing images.
        self.image_right = scaled_image
        self.image_left = pygame.transform.flip(scaled_image, True, False)

        # Set the initial image and facing direction.
        self.image = self.image_right
        self.facing_direction = 1  # 1 means right, -1 means left

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.on_ground = False
        self.on_elevator = False
        self.elevator_offset = None
        self.controlled = False
        # Autonomous movement: 1 for right, -1 for left.
        self.autonomous_direction = 1

    def update(self, platforms, level, elevator_movements):
        if self.being_dragged:
            return
        # If not controlled by the player, set our horizontal speed automatically.
        if not self.controlled:
            self.x_velocity = 5 * self.autonomous_direction
        # Combine the regular platforms with elevator platforms.
        all_platforms = platforms.copy()
        for elevator in level.elevators:
            all_platforms.append(elevator.platform_rect)
        # Remember the x-position before updating physics.
        old_x = self.rect.x
        self.update_physics(all_platforms, level.trampolines, level.portals, level)
        # If not controlled, check if the movement was blocked (or check for falling off an edge)
        if not self.controlled:
            # If the enemy didn't move horizontally, assume a collision and reverse direction.
            if self.rect.x == old_x:
                self.autonomous_direction *= -1
            # Otherwise, if the enemy is on the ground, check if there is ground ahead.
            elif self.on_ground:
                if self.autonomous_direction > 0:
                    look_x = self.rect.right + 1
                else:
                    look_x = self.rect.left - 1
                look_y = self.rect.bottom + 1
                ground_ahead = False
                for platform in platforms:
                    # Assume each platform has a 'rect' attribute.
                    if platform.rect.collidepoint(look_x, look_y):
                        ground_ahead = True
                        break
                if not ground_ahead:
                    self.autonomous_direction *= -1
        self._handle_elevators(level.elevators, elevator_movements)

        # Update facing direction based on the current horizontal velocity.
        if self.x_velocity < 0:
            self.facing_direction = -1
        elif self.x_velocity > 0:
            self.facing_direction = 1

        # Set the current image based on the facing direction.
        if self.facing_direction < 0:
            self.image = self.image_left
        else:
            self.image = self.image_right

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
                self.rect.x += movement[0]
                self.rect.y += movement[1]
                self.rect.x = elevator.platform_rect.x + self.elevator_offset[0]
                self.rect.y = elevator.platform_rect.y + self.elevator_offset[1]
        self.on_elevator = len(elevator_collisions) > 0
        if not elevator_collisions and hasattr(self, 'elevator_offset'):
            del self.elevator_offset

    def draw(self, surface):
        if self.being_dragged:
            tinted = self.get_tinted_surface(self.image)
            surface.blit(tinted, self.rect)
        else:
            surface.blit(self.image, self.rect)

    def handle_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.controlled = True
                return "controlled"
            elif event.button == 3:
                return "remove"
        return None

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_velocity = -5
        elif keys[pygame.K_RIGHT]:
            self.x_velocity = 5
        else:
            self.x_velocity = 0
