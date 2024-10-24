import pygame
import random
import math
from constants import screen, WIDTH, HEIGHT
from particle import Particle

class Unit:
    def __init__(self, x, y, health, attack, color):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.health = health
        self.attack = attack
        self.color = color
        self.moving = False
        self.returning = False
        self.target_unit = None
        self.health_animation = 0
        self.health_animation_time = 0
        self.fading = False
        self.dead = False
        self.attack_animation = 0
        self.attack_direction = 1
        self.particles = []
        self.should_create_particles = False
        self.start_attack_x = None
        self.start_attack_y = None
        self.current_speed = 0.5
        self.acceleration = 0.5
        self.should_fade = False
        self.fade_alpha = 50
        self.fade_speed = 5
        self.ready_to_fade = False  # 새로운 속성 추가

    def draw(self, screen):
        if self.fading and self.ready_to_fade:
            faded_color = self.color + (self.fade_alpha,)
            s = pygame.Surface((50, 100), pygame.SRCALPHA)
            s.fill(faded_color)
        else:
            s = pygame.Surface((50, 100), pygame.SRCALPHA)
            s.fill(self.color + (255,))  # Always use full opacity for non-fading state
        
        screen.blit(s, (self.x, self.y))

        font = pygame.font.Font(None, 24)
        
        health_size = 24 + self.health_animation
        health_font = pygame.font.Font(None, int(health_size))
        health_text = health_font.render(str(self.health), True, (0, 0, 0))
        health_text.set_alpha(self.fade_alpha if self.fading and self.ready_to_fade else 255)
        health_rect = health_text.get_rect()
        health_rect.bottomright = (self.x + 50, self.y + 100)
        screen.blit(health_text, health_rect)

        attack_text = font.render(str(self.attack), True, (255, 255, 255))
        attack_text.set_alpha(self.fade_alpha if self.fading and self.ready_to_fade else 255)
        attack_rect = attack_text.get_rect()
        attack_rect.bottomleft = (self.x, self.y + 100)
        screen.blit(attack_text, attack_rect)

        if self.health_animation > 0:
            self.health_animation_time += 1
            if self.health_animation_time > 10:
                self.health_animation = max(0, self.health_animation - 1)
                self.health_animation_time = 0

        if self.fading and self.ready_to_fade:
            self.fade_alpha = max(0, self.fade_alpha - 5)
            if self.fade_alpha == 0:
                self.dead = True

        for particle in self.particles:
            particle.draw(screen)

    def update_health(self, new_health):
        self.health = new_health
        self.health_animation = 10
        self.health_animation_time = 0
        if self.health <= 0:
            self.health = 0
            self.dead = True
            self.should_create_particles = True

    def move_to_target(self):
        if not self.moving:
            return "idle"

        if self.target_unit:
            if self.start_attack_x is None:
                self.start_attack_x = self.x
                self.start_attack_y = self.y

            target_x = self.target_unit.x if not self.returning else self.original_x
            target_y = self.target_unit.y if not self.returning else self.original_y

            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 5:
                self.current_speed = min(self.current_speed + self.acceleration, 8)
                self.x += self.current_speed * dx / distance
                self.y += self.current_speed * dy / distance
            else:
                self.x = target_x
                self.y = target_y
                if not self.returning:
                    return "attack"
                else:
                    self.moving = False
                    self.target_unit = None
                    self.returning = False
                    self.current_speed = 0.5
                    if self.should_create_particles:
                        self.create_particles()
                        self.should_create_particles = False
                    return "returned"
        else:
            self.moving = False
            self.current_speed = 0.5
        return "moving"

    def is_fading(self):
        return self.fading and self.fade_alpha > 0

    def create_particles(self):
        for _ in range(30):
            particle_x = self.x + 25 + random.uniform(-10, 10)
            particle_y = self.y + 50 + random.uniform(-10, 10)
            self.particles.append(Particle(particle_x, particle_y, self.color, random.uniform(0, 2*math.pi)))

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def create_collision_particles(self, direction):
        dust_color = (139, 69, 19)
        for _ in range(20):
            particle_x = self.x + 25 + random.uniform(-10, 10)
            particle_y = self.y + 50 + random.uniform(-10, 10)
            self.particles.append(Particle(particle_x, particle_y, dust_color, direction, speed_multiplier=2))

    def reset_attack_start_position(self):
        self.start_attack_x = None
        self.start_attack_y = None

    def start_fading(self):
        self.fading = True
        self.ready_to_fade = False  # 아직 페이딩을 시작하지 않음

    def is_completely_faded(self):
        return self.fade_alpha <= 0

    def update(self):
        if self.fading and self.ready_to_fade:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
            if self.fade_alpha <= 0:
                self.dead = True

    def prepare_to_fade(self):
        self.ready_to_fade = True  # 이제 페이딩을 시작할 준비가 됨
