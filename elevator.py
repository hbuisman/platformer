import pygame
import math
from draggable import Draggable

class ElevatorPoint(Draggable):
    def __init__(self, x, y, is_start=True, elevator_id=1):
        Draggable.__init__(self)
        self.rect = pygame.Rect(x, y, 30, 30)
        self.is_start = is_start
        self.elevator_id = elevator_id
        self.font = pygame.font.SysFont(None, 24)
        
    def draw(self, surface):
        color = (0, 255, 0) if self.is_start else (255, 0, 0)
        if self.being_dragged:
            color = (255, 0, 255)
        pygame.draw.circle(surface, color, self.rect.center, 15)
        text = self.font.render(str(self.elevator_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class Elevator:
    def __init__(self, start_x, start_y, elevator_id=1):
        self.start_point = ElevatorPoint(start_x, start_y, True, elevator_id)
        self.end_point = ElevatorPoint(start_x + 50, start_y - 200, False, elevator_id)
        self.elevator_id = elevator_id
        self.platform_width = 112
        self.platform_height = 30
        self.platform_rect = pygame.Rect(start_x, start_y, self.platform_width, self.platform_height)
        self.speed = 3
        self.direction = -1
        self.current_pos = pygame.Vector2(start_x, start_y)
        stone_texture_orig = pygame.image.load("images/stone-platform.png").convert_alpha()
        height_ratio = self.platform_height / stone_texture_orig.get_height()
        scaled_w = int(stone_texture_orig.get_width() * height_ratio)
        self.stone_texture = pygame.transform.smoothscale(stone_texture_orig, (scaled_w, self.platform_height))
    
    def update(self, platforms):
        target = self.end_point.rect.center if self.direction == 1 else self.start_point.rect.center
        target_vec = pygame.Vector2(target)
        move_vec = target_vec - self.current_pos
        if move_vec.length() > self.speed:
            move_step = move_vec.normalize() * self.speed
        else:
            move_step = move_vec
        temp_rect = self.platform_rect.copy()
        temp_rect.center += pygame.Vector2(move_step)
        collision = any(temp_rect.colliderect(p) for p in platforms)
        if collision:
            self.direction *= -1
        else:
            self.current_pos += move_step
            if (self.current_pos - target_vec).length() <= self.speed:
                self.current_pos = target_vec
                self.direction *= -1
        self.platform_rect.center = (round(self.current_pos.x), round(self.current_pos.y))
    
    def draw(self, surface):
        pygame.draw.line(surface, (100, 100, 100), self.start_point.rect.center, self.end_point.rect.center, 2)
        texture_w = self.stone_texture.get_width()
        for x in range(self.platform_rect.x, self.platform_rect.x + self.platform_rect.width, texture_w):
            surface.blit(self.stone_texture, (x, self.platform_rect.y))
        self.start_point.draw(surface)
        self.end_point.draw(surface)
    
    def contains_point(self, x, y):
        if self.platform_rect.collidepoint(x, y):
            return True
        if self.start_point.rect.collidepoint(x, y) or self.end_point.rect.collidepoint(x, y):
            return True
        return False
    
    def reverse_direction(self):
        self.direction *= -1 
