import pygame
from physics_object import PhysicsObject
from draggable import Draggable

class Enemy(PhysicsObject, Draggable):
    def __init__(self, x, y, enemy_type):
        PhysicsObject.__init__(self)
        Draggable.__init__(self)
        self.enemy_type = enemy_type
        self.image = pygame.image.load(f"images/enemy{enemy_type}.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (120, 120))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.on_ground = False
        self.on_elevator = False
        self.elevator_offset = None
        self.controlled = False

    def update(self, platforms, level, elevator_movements):
        if self.being_dragged:
            return
        all_platforms = platforms.copy()
        for elevator in level.elevators:
            all_platforms.append(elevator.platform_rect)
        self.update_physics(all_platforms, level.trampolines, level.portals, level)
        self.handle_horizontal_collisions(platforms)
        self._handle_elevators(level.elevators, elevator_movements)

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
