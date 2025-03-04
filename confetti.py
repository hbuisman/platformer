import pygame
import math
import random

class ConfettiParticle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.radius = random.randint(3, 6)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(5, 10)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.lifetime = random.randint(30, 60)
        self.color = random.choice([
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (255, 165, 0), (128, 0, 128)
        ])
        self.gravity = 0.5

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class ConfettiExplosion:
    def __init__(self, pos, num_particles=100):
        self.particles = [ConfettiParticle(pos) for _ in range(num_particles)]

    def update(self):
        for particle in self.particles:
            particle.update()
        # Remove particles once their lifetime is over
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

    def is_finished(self):
        return len(self.particles) == 0 