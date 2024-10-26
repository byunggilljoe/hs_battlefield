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
        self.fade_speed = 1  # 기존값을 더 작게 변경 (예: 5 -> 3)
        self.ready_to_fade = False  # 새로운 속성 추가
        self.opacity = 255  # 새로운 속성 추가

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
            self.start_fading()  # dead = True 대신 페이딩 시작
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
                    
                    if self.target_unit.should_create_particles:
                        self.target_unit.create_particles()
                        self.target_unit.should_create_particles = False

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
        # Create particles at the unit's center
        unit_center_x = self.x + 25  # Assuming the unit's width is 50
        unit_center_y = self.y + 50  # Assuming the unit's height is 100

        for _ in range(10):  # Number of particles
            direction = random.uniform(0, 2 * math.pi)
            speed_multiplier = random.uniform(0.5, 1.5)
            particle = Particle(unit_center_x, unit_center_y, self.color, direction, speed_multiplier)
            self.particles.append(particle)

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def create_collision_particles(self, direction):
        dust_color = (128, 128, 128)  # 회색으로 변경 (R=128, G=128, B=128)
        for i in range(20):
            particle_x = self.x + 25 + random.uniform(-10, 10)
            particle_y = self.y + 50 + random.uniform(-10, 10)
            # 방사형으로 퍼지는 방향 계산
            radial_direction = direction + (i / 20) * 2 * math.pi
            # 충돌 파티클은 더 큰 크기 범위를 가짐 (3-8)
            self.particles.append(Particle(particle_x, particle_y, dust_color, radial_direction, speed_multiplier=0.5, size_range=(3, 8)))

    def reset_attack_start_position(self):
        self.start_attack_x = None
        self.start_attack_y = None

    def start_fading(self):
        self.fading = True
        self.ready_to_fade = False  # 아직 페이딩을 시작하지 않음

    def is_completely_faded(self):
        return self.fade_alpha <= 0

    def update(self):
        if self.fading:
            self.opacity = max(0, self.opacity - self.fade_speed)  # fade_speed 값이 작을수록 천천히 사라짐
            if self.opacity <= 0:
                self.dead = True

    def prepare_to_fade(self):
        self.ready_to_fade = True  # 이제 페이딩을 시작할 준비가 됨

    def handle_combat(self, target_unit, player_units, enemy_units):
        move_status = self.move_to_target()
        
        if move_status == "attack":
            self.update_health(self.health - target_unit.attack)
            target_unit.update_health(target_unit.health - self.attack)
            self.returning = True
            
            # 기본 충돌 방향에 랜덤한 변화(-0.5 ~ 0.5 라디안, 약 ±28.6도) 추가
            collision_direction = math.atan2(target_unit.y - self.original_y, target_unit.x - self.original_x)
            self.create_collision_particles(collision_direction + random.uniform(-0.25, 0.25))
            target_unit.create_collision_particles(collision_direction + math.pi + random.uniform(-0.25, 0.25))
            
            # 여기서 추가로 player_units와 enemy_units를 활용한 
            # 추가 전투 로직을 구현할 수 있습니다
            
        elif move_status == "returned":
            if target_unit.health <= 0:
                target_unit.prepare_to_fade()
            if self.health <= 0:
                self.prepare_to_fade()
            return "completed"
        
        return "in_progress"
