import pygame
import random
import math
from constants import screen

class Particle:
    def __init__(self, x, y, color, direction, speed_multiplier=1, size_range=(1, 3)):
        self.x = x
        self.y = y
        self.color = color if len(color) == 4 else color + (255,)
        self.radius = random.uniform(size_range[0], size_range[1])  # 크기 범위를 매개변수로 받음
        self.speed = random.uniform(1, 3) * speed_multiplier
        self.angle = direction
        self.lifetime = random.randint(20, 40)
        self.alpha = 255

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.lifetime -= 1
        self.radius = max(0, self.radius - 0.05)
        self.alpha = max(0, self.alpha - 5)

    def draw(self, screen):
        if self.alpha > 0:
            color_with_alpha = self.color[:3] + (self.alpha,)
            particle_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surface, (int(self.x - self.radius), int(self.y - self.radius)))
