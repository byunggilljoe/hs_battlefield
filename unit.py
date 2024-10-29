import pygame
import random
import math
from constants import screen, WIDTH, HEIGHT
from particle import Particle

class Unit:
    def __init__(self, x, y, health, attack, color, game_state, cost=3):
        self.name = "Unit"
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
        self.fade_speed = 2.0  # 1에서 0.5로 변경하여 페이딩 속도를 절반으로 줄임
        self.ready_to_fade = False  # 새로운 속성 추가
        self.game_state = game_state
        self.taunt = False  # 도발 상태
        self.taunt_particles = []  # 도발 시각 효과를 위한 파티클
        self.battle_cry = False  # 전장의 함성 특성 추가
        self.shake_offset = 0  # 좌우 흔들림을 위한 오프셋
        self.shake_speed = 8   # 흔들림 속도
        self.shake_amount = 2  # 최대 흔들림 범위
        self.cost = cost

    def draw(self, screen):
        # 페이딩 중일 때 흔들림 효과 계산
        current_x = self.x
        if self.fading and self.ready_to_fade:
            self.shake_offset = math.sin(pygame.time.get_ticks() * 0.01 * self.shake_speed) * self.shake_amount
            current_x += self.shake_offset

        # 도발 효과 그리기 (taunt 속성이 있는 유닛만)
        if hasattr(self, 'taunt') and self.taunt:
            taunt_thickness = 15
            taunt_surface = pygame.Surface((50 + taunt_thickness, 100 + taunt_thickness), pygame.SRCALPHA)
            pygame.draw.rect(taunt_surface, (128, 128, 128, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                           (0, 0, 50 + taunt_thickness, 100 + taunt_thickness))
            screen.blit(taunt_surface, (current_x - taunt_thickness//2, self.y - taunt_thickness//2))
        
        # 기본 유닛 그리기
        unit_surface = pygame.Surface((50, 100), pygame.SRCALPHA)
        pygame.draw.rect(unit_surface, (*self.color, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                        (0, 0, 50, 100))
        screen.blit(unit_surface, (current_x, self.y))

        # 텍스트 그리기도 흔들림 효과 적용
        font = pygame.font.Font(None, 24)
        
        # 유닛 이름 그리기
        name_font = pygame.font.Font(None, 20)
        name_text = name_font.render(self.name, True, (255, 255, 255))
        name_text.set_alpha(self.fade_alpha if self.fading and self.ready_to_fade else 255)
        name_rect = name_text.get_rect(center=(current_x + 25, self.y + 50))
        screen.blit(name_text, name_rect)

        # 체력 텍스트
        health_size = 24 + self.health_animation
        health_font = pygame.font.Font(None, int(health_size))
        health_text = health_font.render(str(self.health), True, (0, 0, 0))
        health_text.set_alpha(self.fade_alpha if self.fading and self.ready_to_fade else 255)
        health_rect = health_text.get_rect()
        health_rect.bottomright = (current_x + 50, self.y + 100)
        screen.blit(health_text, health_rect)

        # 공격력 텍스트
        attack_text = font.render(str(self.attack), True, (255, 255, 255))
        attack_text.set_alpha(self.fade_alpha if self.fading and self.ready_to_fade else 255)
        attack_rect = attack_text.get_rect()
        attack_rect.bottomleft = (current_x, self.y + 100)
        screen.blit(attack_text, attack_rect)

        if self.health_animation > 0:
            self.health_animation_time += 1
            if self.health_animation_time > 10:
                self.health_animation = max(0, self.health_animation - 1)
                self.health_animation_time = 0

        # if self.fading and self.ready_to_fade:
        #     self.fade_alpha = max(0, self.fade_alpha - 2.5)  # 5에서 2.5로 변경
        #     if self.fade_alpha == 0:
        #         self.dead = True

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
                # starts to move
                self.on_start_move()
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
                    self.start_attack_x = None
                    self.start_attack_y = None
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
        # print("Fading!", self.name, self.fading, self.ready_to_fade)
        if self.fading and self.ready_to_fade:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)  # 5에서 2.5로 변경
            if self.fade_alpha == 0:
                self.dead = True

    def prepare_to_fade(self):
        self.ready_to_fade = True  # 이제 페이딩을 시작할 준비가 됨

    def apply_damage(self, target_unit):
        target_unit.update_health(target_unit.health - self.attack)
        
    def on_spawn(self, player_units, enemy_units):
        # 기본 구현은 아무것도 하지 않음
        pass
    
    def on_start_move(self):
        pass

    def on_attack(self, target, player_units, enemy_units):
        pass
    
    def on_death(self):
        pass

