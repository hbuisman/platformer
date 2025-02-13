import pygame

class PhysicsObject:
    GRAVITY = 0.5

    def __init__(self):
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False
        self.on_elevator = False
        # Default bounce multiplier; note that Player will override its bounce behavior.
        self.bounce_multiplier = 20

    def apply_gravity(self):
        self.y_velocity += self.GRAVITY

    def update_vertical_position(self):
        self.rect.y += self.y_velocity

    def handle_vertical_collisions(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                # When falling:
                if self.y_velocity > 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True
                # When rising:
                elif self.y_velocity < 0:
                    self.rect.top = platform.bottom
                    self.y_velocity = 0

    def handle_horizontal_collisions(self, platforms):
        self.rect.x += self.x_velocity
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.x_velocity > 0:
                    self.rect.right = platform.left
                elif self.x_velocity < 0:
                    self.rect.left = platform.right
                self.x_velocity = 0

    def check_trampolines(self, trampolines):
        # Default behavior: bounce with a fixed multiplier.
        for tramp in trampolines:
            if self.rect.colliderect(tramp.rect):
                if self.y_velocity > 0:
                    self.rect.bottom = tramp.rect.top
                    self.y_velocity = -self.bounce_multiplier
                    self.on_ground = False

    def check_portals(self, portals, level):
        teleported = False
        for portal in portals:
            if hasattr(portal, 'is_entrance') and portal.is_entrance and self.rect.colliderect(portal.rect):
                exit_portal = level.find_portal_pair(portal)
                if exit_portal:
                    self.rect.centerx = exit_portal.rect.centerx
                    self.rect.bottom = exit_portal.rect.bottom
                    teleported = True
        if teleported and hasattr(self, "portal_sound"):
            self.portal_sound.play()

    def update_physics(self, platforms, trampolines, portals, level):
        self.apply_gravity()
        self.update_vertical_position()
        self.handle_vertical_collisions(platforms)
        self.handle_horizontal_collisions(platforms)
        # Note: the call to check_trampolines will invoke the overridden method if defined in a subclass.
        self.check_trampolines(trampolines)
        self.check_portals(portals, level)
