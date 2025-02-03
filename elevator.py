import pygame
import math

class ElevatorPoint:
    def __init__(self, x, y, is_start=True, elevator_id=1):
        self.rect = pygame.Rect(x, y, 30, 30)  # Circle with 30px diameter
        self.is_start = is_start
        self.elevator_id = elevator_id
        self.font = pygame.font.SysFont(None, 24)
        
    def draw(self, surface, is_dragging=False):
        color = (0, 255, 0) if self.is_start else (255, 0, 0)
        if is_dragging:
            # Add magenta tint when dragging
            color = (255, 0, 255)
            
        # Draw circle
        pygame.draw.circle(surface, color, self.rect.center, 15)
        
        # Draw elevator number
        text = self.font.render(str(self.elevator_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class Elevator:
    def __init__(self, start_x, start_y, elevator_id=1):
        self.start_point = ElevatorPoint(start_x, start_y, True, elevator_id)
        self.end_point = ElevatorPoint(start_x + 50, start_y - 200, False, elevator_id)
        self.elevator_id = elevator_id
        
        # Platform properties - now half as wide
        self.platform_width = 112  # Half of 225
        self.platform_height = 30
        self.platform_rect = pygame.Rect(start_x, start_y, self.platform_width, self.platform_height)
        
        # Movement properties
        self.speed = 3  # Pixels per frame
        self.direction = 1  # 1 for moving towards end, -1 for moving back
        self.current_pos = pygame.Vector2(start_x, start_y)
        
        # Load and scale stone texture
        stone_texture_orig = pygame.image.load("images/stone-platform.png").convert_alpha()
        height_ratio = self.platform_height / stone_texture_orig.get_height()
        scaled_w = int(stone_texture_orig.get_width() * height_ratio)
        self.stone_texture = pygame.transform.smoothscale(stone_texture_orig, (scaled_w, self.platform_height))

    def update(self, platforms):
        # Calculate vector to target
        target = self.end_point.rect.center if self.direction == 1 else self.start_point.rect.center
        target_vec = pygame.Vector2(target)
        move_vec = target_vec - self.current_pos
        
        # Calculate movement step
        if move_vec.length() > self.speed:
            move_step = move_vec.normalize() * self.speed
        else:
            move_step = move_vec  # remaining distance to target

        # Check collision with platforms before moving
        temp_rect = self.platform_rect.copy()
        temp_rect.center += pygame.Vector2(move_step)
        
        collision = any(temp_rect.colliderect(p) for p in platforms)
        
        if collision:
            # Reverse direction immediately on collision
            self.direction *= -1
        else:
            # Move normally if no collision
            self.current_pos += move_step
            # Check if reached target
            if (self.current_pos - target_vec).length() <= self.speed:
                self.current_pos = target_vec
                self.direction *= -1

        # Update platform position
        self.platform_rect.center = (round(self.current_pos.x), round(self.current_pos.y))

    def draw(self, surface, dragging_point=None):
        # Draw connection lines
        pygame.draw.line(surface, (100, 100, 100), 
                        self.start_point.rect.center, 
                        self.end_point.rect.center, 2)
        
        # Draw platform with stone texture
        texture_w = self.stone_texture.get_width()
        for x in range(self.platform_rect.x, self.platform_rect.x + self.platform_rect.width, texture_w):
            surface.blit(self.stone_texture, (x, self.platform_rect.y))
            
        # Draw points
        self.start_point.draw(surface, dragging_point == self.start_point)
        self.end_point.draw(surface, dragging_point == self.end_point)

    def contains_point(self, x, y):
        """Check if a point collides with any part of the elevator"""
        # Check platform
        if self.platform_rect.collidepoint(x, y):
            return True
        # Check start and end points
        if self.start_point.rect.collidepoint(x, y) or self.end_point.rect.collidepoint(x, y):
            return True
        return False 